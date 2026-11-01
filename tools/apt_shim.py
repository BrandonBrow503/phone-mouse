# Local HTTP->curl(https) shim for apt when apt's own TLS is broken.
import http.server, subprocess
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://deb.debian.org" + self.path
        p = subprocess.run(["curl","-sfL","--retry","3",url],capture_output=True)
        if p.returncode: self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Length",str(len(p.stdout))); self.end_headers(); self.wfile.write(p.stdout)
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(("127.0.0.1",8899),H).serve_forever()
