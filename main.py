import tkinter as tk
import customtkinter as ctk
from ui.login_ui import LoginApp
from ui.dashboard_ui import DashboardApp

# System Settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainAppController:
    def __init__(self):
        self.root = ctk.CTk()
        self.start_login_ui()

    def start_login_ui(self):
        # Just passing the callback function; no parent needed
        self.login_app = LoginApp(on_success_callback=self.on_login_success)

    def on_login_success(self):
        self.login_app.pack_forget()  # Remove login UI
        self.dashboard_app = DashboardApp(self.root)
        self.dashboard_app.pack()  # Show dashboard UI


if __name__ == "__main__":
    app = MainAppController()
    app.root.mainloop()
