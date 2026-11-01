#!/usr/bin/env bash
set -e; cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv; . .venv/bin/activate
pip install -q qrcode pillow pyinstaller python-xlib six && pip install -q --no-deps pynput
pyinstaller --noconfirm --clean --onefile --name PhoneMouse-linux --add-data "phonemouse/index.html:phonemouse" \
  --hidden-import pynput.mouse._xorg --hidden-import pynput.keyboard._xorg --hidden-import PIL.ImageTk --hidden-import PIL._tkinter_finder main.py
