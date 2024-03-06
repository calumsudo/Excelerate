import tkinter as tk
import customtkinter as ctk
import webbrowser
import pyperclip
from auth import initiate_device_flow, authenticate

class LoginApp(ctk.CTk):
    def __init__(self, on_success_callback=None):
        super().__init__()  # Removed the parent parameter
        self.on_success_callback = on_success_callback
        self.geometry("720x480")
        self.title("AutoExcel")
        self.flow = None  # Store the flow information

        self.title_label = ctk.CTkLabel(self, text="Log In to Microsoft and Enter Authentication Code", font=("Arial", 24))
        self.title_label.pack(padx=10, pady=10)

        self.login_button = ctk.CTkButton(self, text="Log In", command=self.on_login_pressed)
        self.login_button.pack(pady=20)

        self.auth_code_label = ctk.CTkLabel(self, text="")
        self.copy_and_open_button = ctk.CTkButton(self, text="Copy Code and Open Log In Portal", command=self.copy_code_and_open_portal, state=tk.DISABLED)

    def on_login_pressed(self):
        self.login_button.configure(state=tk.DISABLED)
        self.flow = initiate_device_flow()
        if self.flow:
            code = self.flow.get("user_code")
            self.auth_code_label.configure(text=f"Authentication Code: {code}")
            self.auth_code_label.pack(pady=10)
            self.copy_and_open_button.pack(pady=10)
            self.copy_and_open_button.configure(state=tk.NORMAL)  # Enable button once the code is displayed
            authenticate(self.flow, self.authentication_callback)

    def authentication_callback(self, success, response):
        # This method will be called from a background thread.
        # Use `after` to safely update the GUI from the main thread.
        if success:
            self.after(0, self.show_authenticated_state, response)
        else:
            self.after(0, self.show_authentication_failed)

    def show_authenticated_state(self, response):
        # Clear the UI and show authenticated state
        print("Authentication successful", response)
        self.destroy()
        # Here you can clear the GUI or transition to another state
        # For simplicity, we're just printing the response

    def show_authentication_failed(self):
        # Show an error message or revert the UI to allow retry
        print("Authentication failed")
        # Here you could implement logic to allow retrying the authentication

    def copy_code_and_open_portal(self):
        if self.flow:
            pyperclip.copy(self.flow.get("user_code"))
            webbrowser.open_new(self.flow["verification_uri"])
