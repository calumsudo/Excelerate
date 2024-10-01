import os
import customtkinter as ctk
from ui.authenticate_ui import AuthenticateUI
import json
from services.authentication_manager import AuthenticationManager

TOKEN_FILE = "access_token.json"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Excelerate")
        self.geometry("1200x1000")

        # Variables to store authentication data
        self.access_token = None
        self.user_name = None

        # Initialize the authentication manager
        self.auth_manager = AuthenticationManager()

        # Try loading the access token on start
        self.load_access_token()

        if self.access_token and not self.auth_manager.is_token_expired():
            # If we have a valid token, skip authentication
            self.show_success_ui()
        elif self.access_token and self.auth_manager.is_token_expired():
            # If the token is expired, refresh it
            self.auth_manager.refresh_access_token(self.authentication_callback)
        else:
            # If no token, show authentication UI
            self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
            self.authenticate_ui.pack(pady=20)

    def authentication_callback(self, success, response, access_token, refresh_token, token_expiry):
        if success:
            # Only update user_name if response is not None (initial authentication case)
            if response:
                self.user_name = response.get("displayName", "Unknown User")

            # Always update access_token, refresh_token, and token_expiry
            self.access_token = access_token
            self.auth_manager.refresh_token = refresh_token
            self.auth_manager.token_expiry = token_expiry

            # Save the token for future use
            self.save_access_token()

            # Remove the authentication UI (if it exists) and show the success UI
            if hasattr(self, 'authenticate_ui'):
                self.authenticate_ui.pack_forget()
            self.show_success_ui()

        else:
            # If authentication failed, show the authentication UI again
            if hasattr(self, 'authenticate_ui'):
                self.authenticate_ui.label.configure(text="Authentication failed. Please try again.")
            else:
                # If we're trying to refresh and it fails, bring back the authentication UI
                self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
                self.authenticate_ui.pack(pady=20)



    def save_access_token(self):
        """Saves the access token and expiry to a file."""
        # Explicitly retrieve refresh_token and token_expiry from self.auth_manager
        token_data = {
            "access_token": self.access_token,
            "user_name": self.user_name,
            "token_expiry": self.auth_manager.token_expiry,
            "refresh_token": self.auth_manager.refresh_token
        }

        # Debugging: Print the token data that will be saved
        print(f"Saving token data: {token_data}")

        # Save the token data to the JSON file
        with open(TOKEN_FILE, "w") as token_file:
            json.dump(token_data, token_file)
        print("Access token saved.")

    def load_access_token(self):
        """Loads the access token and expiry from a file if it exists."""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as token_file:
                token_data = json.load(token_file)
                self.access_token = token_data.get("access_token")
                self.user_name = token_data.get("user_name")

                # Initialize auth_manager and set the token details
                self.auth_manager.access_token = self.access_token
                self.auth_manager.refresh_token = token_data.get("refresh_token")
                self.auth_manager.token_expiry = token_data.get("token_expiry")
                
                # Debugging: Print the loaded token data
                print(f"Loaded token data: {token_data}")

    def show_success_ui(self):
        """Displays the UI for successful authentication."""
        success_label = ctk.CTkLabel(
            self, text=f"Welcome {self.user_name}!", font=("Arial", 18)
        )
        success_label.pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()
