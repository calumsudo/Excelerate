import tkinter as tk
import customtkinter as ctk
import webbrowser
import pyperclip
from threading import Thread
from auth import initiate_device_flow, authenticate

# System Settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("720x480")
        self.title("AutoExcel")
        self.title_label = ctk.CTkLabel(self, text="Log In to Microsoft and Enter Authentication Code", font=("Arial", 24))
        self.title_label.pack(padx=10, pady=10)

        self.login_button = ctk.CTkButton(self, text="Log In", command=self.on_login_pressed)
        self.login_button.pack(pady=20)

        # Placeholder for authentication code display and copy button (added for illustration)
        self.auth_code_label = ctk.CTkLabel(self, text="")
        self.copy_and_open_button = ctk.CTkButton(self, text="Copy Code and Open Log In Portal", command=self.copy_code_and_open_portal)
        
    def on_login_pressed(self):
        self.login_button.configure(state=tk.DISABLED)
        Thread(target=self.authenticate).start()

    def authenticate(self):
        flow = initiate_device_flow()
        print("FLOW: ", flow)
        if flow:
            code = flow.get("user_code")
            self.auth_code_label.configure(text=f"Authentication Code: {code}")
            self.auth_code_label.pack(pady=10)
            self.copy_and_open_button.pack(pady=10)

            # Authenticate
            result = authenticate(flow)
            if result:
                print("Authentication successful")
            else:
                print("Authentication failed")
    
    def copy_code_and_open_portal(self):
        flow = initiate_device_flow()  # You should avoid calling this again if you already have the flow info. Consider refactoring.
        pyperclip.copy(flow.get("user_code"))
        webbrowser.open_new(flow["verification_uri"])

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
