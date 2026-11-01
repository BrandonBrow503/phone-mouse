# 📱🖱️ Phone Mouse

Use any phone (iPhone, Android, even an old one) as a touchpad for your computer. No app to install on the phone — just scan a QR code.

## Windows (easiest)
1. Download **PhoneMouse.exe** from the [Releases page](https://github.com/BrandonBrow503/phone-mouse/releases/latest).
2. Double-click it. If Windows says *"Windows protected your PC"*, tap **More info → Run anyway** (it's unsigned).
3. When **Windows Firewall** asks, tick **Private networks** and click **Allow access**. (Without this the phone can't connect.)
4. A window shows a **QR code**. Point your phone camera at it and open the link.
5. Phone and computer must be on the **same Wi-Fi**.

## Using the touchpad
| Gesture | Action |
|---|---|
| 1 finger slide | Move pointer (faster swipe = faster pointer) |
| Tap | Left click |
| Double-tap | Double click |
| Double-tap and hold, then slide | Drag (select / move windows) |
| 2-finger tap | Right click |
| 2-finger slide | Scroll |
| LEFT / RIGHT buttons | Hold or tap to click |
| Speed slider | Pointer sensitivity (remembered) |
| ⌨ Keys | Type text on the computer (Enter sends, empty Backspace deletes) |

The link has a 4-digit **PIN** (`?pin=1234`), new each launch, so others on the Wi-Fi can't control your computer.

## Linux
Download **PhoneMouse-linux**, then `chmod +x PhoneMouse-linux && ./PhoneMouse-linux` (X11 session; Wayland may block pointer control). Allow port 8765 in your firewall if you use one.

## Mac (run from source)
```bash
pip3 install pynput qrcode pillow
python3 main.py
```
Then allow your Terminal in **System Settings → Privacy & Security → Accessibility** (needed to move the mouse) and allow incoming connections if macOS asks. Python from python.org includes Tk for the QR window.

## Options
`--port 8765` · `--pin 1234` (fixed PIN) · `--headless` (no window, just prints the URL)

## How it works
Python stdlib HTTP server + tiny built-in WebSocket on port 8765 (falls back to HTTP POST batches if WebSocket fails, for old browsers). Mouse control via `pynput`. The phone page is a single ES5 HTML file.

## Build
`./build_windows.sh` (PyInstaller under Wine) · `./build_linux.sh` · tests: `python tests/test_server.py`
