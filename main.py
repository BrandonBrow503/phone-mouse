import argparse, sys, time
from phonemouse.server import Core, Mouse, start

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--headless", action="store_true")
    ap.add_argument("--port", type=int, default=8765); ap.add_argument("--pin")
    a = ap.parse_args()
    core = Core(Mouse(), a.pin); srv, url = start(core, port=a.port)
    print("Phone Mouse running. Open on your phone:", url, flush=True)
    if a.headless:
        while True: time.sleep(3600)
    try:
        from phonemouse.gui import show
        show(url, core).mainloop()
    except Exception as e:  # no display / Tk problem: keep serving
        print("Window unavailable (%s); still running. Ctrl+C to quit." % e, flush=True)
        while True: time.sleep(3600)

if __name__ == "__main__": main()
