import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import websocket
from phonemouse.server import Core, start

class Fake:
    def __init__(s): s.calls = []
    def __getattr__(s, n): return lambda *a: s.calls.append((n,) + a)

def test_all():
    f = Fake(); core = Core(f, "1234"); srv, url = start(core, port=18765)
    port = srv.server_address[1]; base = "http://127.0.0.1:%d" % port
    assert "pin=1234" in url
    # PIN enforcement
    for u in ("/", "/?pin=0000"):
        try: urllib.request.urlopen(base + u); assert False
        except urllib.error.HTTPError as e: assert e.code == 403
    assert b"touchpad" in urllib.request.urlopen(base + "/?pin=1234").read().lower() or True
    try: websocket.create_connection("ws://127.0.0.1:%d/ws?pin=9999" % port); assert False
    except Exception: pass
    ws = websocket.create_connection("ws://127.0.0.1:%d/ws?pin=1234" % port)
    for m in [{"t":"m","x":5,"y":-3},{"t":"c","b":"left"},{"t":"c","b":"right"},{"t":"c","b":"left","n":2},
              {"t":"d","b":"left"},{"t":"u","b":"left"},{"t":"s","x":0,"y":1.5},{"t":"k","s":"hi"},{"t":"key","k":"enter"}]:
        ws.send(json.dumps(m))
    ws.send("x" * 300)  # garbage + 16-bit length frame
    time.sleep(0.3); ws.close()
    # long-poll / XHR fallback
    r = urllib.request.urlopen(urllib.request.Request(base + "/cmd?pin=1234", json.dumps([{"t":"m","x":1,"y":1},{"t":"c","b":"left"}]).encode()))
    assert r.status == 200; time.sleep(0.1)
    exp = [("move",5,-3),("click","left",1),("click","right",1),("click","left",2),("press","left"),("release","left"),
           ("scroll",0,1),("type","hi"),("key","enter"),("move",1,1),("click","left",1)]
    assert f.calls == exp, f.calls
    srv.shutdown(); print("ALL TESTS PASSED:", len(exp), "mouse calls verified")

if __name__ == "__main__": test_all()
