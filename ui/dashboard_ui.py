import tkinter as tk
import customtkinter as ctk

class DashboardApp(ctk.CTk):
    def __init__(self, master):
        super().__init__(master)
        self.geometry("720x480")
        self.title("AutoExcel")

        self.title_label = ctk.CTkLabel(self, text="Dashboard", font=("Arial", 24))
        self.title_label.pack(padx=10, pady=10)

        