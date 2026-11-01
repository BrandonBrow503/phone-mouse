"""Phone Mouse server: stdlib HTTP + minimal WebSocket + long-poll fallback."""
import base64, hashlib, json, os, random, socket, struct, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def resource(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(base, "phonemouse", name)
    return p if os.path.exists(p) else os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1)); return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

class Mouse:
    """Real mouse/keyboard via pynput (imported lazily so tests can mock)."""
    def __init__(self):
        from pynput.mouse import Controller, Button
        from pynput.keyboard import Controller as KC, Key
        self.m, self.B, self.k, self.Key = Controller(), Button, KC(), Key
    def move(self, dx, dy): self.m.move(dx, dy)
    def click(self, b="left", n=1): self.m.click(self.B.right if b == "right" else self.B.left, n)
    def press(self, b="left"): self.m.press(self.B.right if b == "right" else self.B.left)
    def release(self, b="left"): self.m.release(self.B.right if b == "right" else self.B.left)
    def scroll(self, dx, dy): self.m.scroll(dx, dy)
    def type(self, text): self.k.type(text)
    def key(self, name):
        k = {"enter": self.Key.enter, "backspace": self.Key.backspace, "tab": self.Key.tab,
             "esc": self.Key.esc}.get(name)
        if k: self.k.press(k); self.k.release(k)

class Core:
    def __init__(self, mouse, pin=None):
        self.mouse = mouse
        self.pin = pin or "%04d" % random.randint(0, 9999)
        self.clients = 0
        self.lock = threading.Lock()
        self._sacc = [0.0, 0.0]
    def handle(self, msg):
        t = msg.get("t"); m = self.mouse
        with self.lock:
            if t == "m": m.move(int(msg.get("x", 0)), int(msg.get("y", 0)))
            elif t == "c": m.click(msg.get("b", "left"), int(msg.get("n", 1)))
            elif t == "d": m.press(msg.get("b", "left"))
            elif t == "u": m.release(msg.get("b", "left"))
            elif t == "s":
                self._sacc[0] += float(msg.get("x", 0)); self._sacc[1] += float(msg.get("y", 0))
                ix, iy = int(self._sacc[0]), int(self._sacc[1])
                if ix or iy:
                    self._sacc[0] -= ix; self._sacc[1] -= iy; m.scroll(ix, iy)
            elif t == "k": m.type(str(msg.get("s", ""))[:500])
            elif t == "key": m.key(msg.get("k", ""))

def make_handler(core):
    page = open(resource("index.html"), "rb").read()
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        def log_message(self, *a): pass
        def ok_pin(self, q):
            return q.get("pin", [""])[0] == core.pin
        def send(self, code, body=b"", ctype="text/plain"):
            self.send_response(code)
            self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            u = urlparse(self.path); q = parse_qs(u.query)
            if u.path in ("/", "/index.html"):
                if not self.ok_pin(q):
                    return self.send(403, b"<h2 style='font-family:sans-serif'>Wrong or missing PIN. Scan the QR code on the computer.</h2>", "text/html")
                return self.send(200, page, "text/html; charset=utf-8")
            if u.path == "/ws":
                if not self.ok_pin(q): return self.send(403)
                return self.websocket()
            if u.path == "/ping": return self.send(200 if self.ok_pin(q) else 403, b"ok")
            self.send(404)
        def do_POST(self):  # long-poll / XHR fallback: body is a JSON array of messages
            u = urlparse(self.path); q = parse_qs(u.query)
            if u.path != "/cmd" or not self.ok_pin(q): return self.send(403)
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                data = json.loads(self.rfile.read(n).decode("utf-8") or "[]")
                for msg in (data if isinstance(data, list) else [data]): core.handle(msg)
            except Exception: return self.send(400)
            self.send(200, b"ok")
        def websocket(self):
            key = self.headers.get("Sec-WebSocket-Key")
            if not key: return self.send(400)
            acc = base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()
            self.send_response(101); self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade"); self.send_header("Sec-WebSocket-Accept", acc); self.end_headers()
            self.wfile.flush(); self.close_connection = True
            r = self.rfile; core.clients += 1
            try:
                while True:
                    h = r.read(2)
                    if len(h) < 2: break
                    op = h[0] & 15; ln = h[1] & 127; masked = h[1] & 128
                    if ln == 126: ln = struct.unpack(">H", r.read(2))[0]
                    elif ln == 127: ln = struct.unpack(">Q", r.read(8))[0]
                    mk = r.read(4) if masked else b"\0\0\0\0"
                    data = bytearray(r.read(ln))
                    for i in range(len(data)): data[i] ^= mk[i % 4]
                    if op == 8: break
                    if op == 9: self.wfile.write(bytes([0x8A, len(data)]) + data); continue
                    if op == 1:
                        try:
                            msg = json.loads(data.decode("utf-8"))
                            for m in (msg if isinstance(msg, list) else [msg]): core.handle(m)
                        except Exception: pass
            finally:
                core.clients -= 1
    return H

def start(core, host="0.0.0.0", port=8765):
    for p in range(port, port + 20):
        try:
            srv = ThreadingHTTPServer((host, p), make_handler(core)); break
        except OSError: continue
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://%s:%d/?pin=%s" % (lan_ip(), srv.server_address[1], core.pin)
