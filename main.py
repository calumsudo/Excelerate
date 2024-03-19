from auth import initiate_device_flow, authenticate
import tkinter as tk
import customtkinter as ctk
import threading


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Excelerate")
        self.geometry("400x200")

        self.label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.label.pack(pady=20)

        self.authenticate_button = ctk.CTkButton(self, text="Authenticate", command=self.authenticate)
        self.authenticate_button.pack(pady=10)

    def authenticate(self):
        self.label.configure(text="Initiating device flow...")
        flow = initiate_device_flow()
        self.label.configure(text=f"User code: {flow['user_code']}")
        # No need to start a separate thread here
        authenticate(flow, self.authentication_callback)

    def authentication_callback(self, success, response):
        if success:
            self.label.configure(text="Authentication successful!")
            print("Response:", response)
        else:
            self.label.configure(text="Authentication failed.")

if __name__ == "__main__":
    app = App()
    app.mainloop()