# app/main.py

import customtkinter as ctk
from gui.dashboard import Dashboard

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = Dashboard()
    app.mainloop()