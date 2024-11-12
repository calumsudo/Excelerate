import customtkinter as ctk
from PIL import Image
from pathlib import Path
from ..core.auth.ms_auth import MSAuthManager

class AuthWindow(ctk.CTkFrame):
    """Enhanced version of your existing authentication UI"""
    
    def __init__(self, master, config_dir: Path, auth_callback):
        super().__init__(master)
        self.config_dir = config_dir
        self.auth_callback = auth_callback
        self.auth_manager = MSAuthManager(config_dir)
        self.setup_ui()

    def setup_ui(self):
        """Setup authentication UI."""
        self.label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.label.pack(pady=20)

        self.auth_status_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.auth_status_label.pack(pady=20)

        self.authenticate_button = ctk.CTkButton(
            self, 
            text="Authenticate", 
            command=self.authenticate
        )
        self.authenticate_button.pack(pady=10)

        # Load and display logo
        logo_path = self.config_dir / "assets" / "ExcelerateLogo.png"
        if logo_path.exists():
            self.logo_image = ctk.CTkImage(Image.open(logo_path), size=(400, 400))
            self.image_label = ctk.CTkLabel(self, image=self.logo_image, text="")
            self.image_label.pack()

    def authenticate(self):
        """Handle authentication process."""
        self.label.configure(text="Initiating device flow...")
        try:
            flow = self.auth_manager.initiate_device_flow()
            self.label.configure(text=f"User code: {flow['user_code']}")
            self.auth_status_label.configure(text="Checking for authentication...")
            self.auth_manager.authenticate(flow, self.auth_callback)
        except Exception as e:
            self.label.configure(text=f"Error: {str(e)}")
            self.auth_status_label.configure(text="")