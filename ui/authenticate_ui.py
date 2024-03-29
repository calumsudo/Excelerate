# authenticate_ui.py
import customtkinter as ctk
from auth import initiate_device_flow, authenticate
from PIL import Image
import os


class AuthenticateUI(ctk.CTkFrame):
    def __init__(self, master, authentication_callback):
        super().__init__(master)
        self.authentication_callback = authentication_callback

        self.label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.label.pack(pady=20)

        # Add a new label for displaying the authentication status
        self.auth_status_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.auth_status_label.pack(pady=20)

        self.authenticate_button = ctk.CTkButton(self, text="Authenticate", command=self.authenticate)
        self.authenticate_button.pack(pady=10)

        current_path = os.path.dirname(os.path.realpath(__file__))
        self.logo_image = ctk.CTkImage(Image.open(current_path + "/ExcelerateLogo.png"), size=(400, 400))
        self.image_label = ctk.CTkLabel(self, image=self.logo_image, text="")
        self.image_label.pack()        

    def authenticate(self):
        self.label.configure(text="Initiating device flow...")
        flow = initiate_device_flow()
        self.label.configure(text=f"User code: {flow['user_code']}")

        # Update the authentication status label
        self.auth_status_label.configure(text="Checking for authentication...")

        # No need to start a separate thread here
        authenticate(flow, self.authentication_callback)