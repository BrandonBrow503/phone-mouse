import tkinter as tk
import qrcode
from PIL import ImageTk

def show(url, core):
    root = tk.Tk(); root.title("Phone Mouse"); root.configure(bg="#0f1115"); root.resizable(False, False)
    tk.Label(root, text="Phone Mouse", fg="#ffffff", bg="#0f1115", font=("Segoe UI", 18, "bold")).pack(pady=(16, 2))
    tk.Label(root, text="Scan with your phone camera (same Wi-Fi)", fg="#9aa3b2", bg="#0f1115", font=("Segoe UI", 10)).pack()
    qr = qrcode.QRCode(border=2, box_size=7); qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color="#0f1115", back_color="white").convert("RGB")
    ph = ImageTk.PhotoImage(img)
    tk.Label(root, image=ph, bg="#0f1115").pack(padx=24, pady=12); root._ph = ph
    e = tk.Entry(root, width=34, justify="center", font=("Consolas", 11), relief="flat", bg="#1b1f27", fg="#7cc4ff", readonlybackground="#1b1f27")
    e.insert(0, url); e.configure(state="readonly"); e.pack(padx=20, ipady=6)
    tk.Label(root, text="PIN  " + core.pin, fg="#ffffff", bg="#0f1115", font=("Segoe UI", 14, "bold")).pack(pady=(10, 0))
    st = tk.Label(root, text="", fg="#5ee38b", bg="#0f1115", font=("Segoe UI", 10)); st.pack(pady=(4, 16))
    def tick():
        st.config(text=("● %d phone(s) connected" % core.clients) if core.clients else "Waiting for phone…", fg="#5ee38b" if core.clients else "#9aa3b2")
        root.after(700, tick)
    tick(); return root
