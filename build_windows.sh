#!/usr/bin/env bash
# Cross-build PhoneMouse.exe with PyInstaller under Wine 10 (Python 3.12 prefix from wallet-finder build).
# If apt's TLS is broken on this box: run tools/apt_shim.py and point debian.sources at http://127.0.0.1:8899
# (sudo apt-get install wine wine64). Wine's pip is broken here, so pure-python wheels are unzipped into site-packages.
set -e; cd "$(dirname "$0")"
export WINEPREFIX=${WINEPREFIX:-/workspace/wbuild/wpy} WINEDEBUG=-all
wine 'C:\Python312\python.exe' -m PyInstaller --noconfirm --clean --onefile --windowed --name PhoneMouse \
  --add-data "phonemouse/index.html;phonemouse" --hidden-import pynput.mouse._win32 --hidden-import pynput.keyboard._win32 \
  --hidden-import PIL.ImageTk --hidden-import PIL._tkinter_finder main.py
