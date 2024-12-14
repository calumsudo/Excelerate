import os
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from ui.authenticate_ui import AuthenticateUI
from ui.dashboard_ui import DashboardUI
from ui.alder_ui import AlderPortfolioUI
from ui.alder_ui2 import AlderPortfolioUI2
from ui.white_rabbit_ui import WhiteRabbitPortfolioUI
import json
from services.authentication_manager import AuthenticationManager
import requests

TOKEN_FILE = "access_token.json"
CONFIG_FILE = "config.json"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Excelerate")
        self.geometry("800x800")  # Increased size
        print("App initialization started")

        # Variables to store authentication data
        self.access_token = None
        self.user_name = None
        self.data = None

        # Initialize the authentication manager
        self.auth_manager = AuthenticationManager()
        print("AuthenticationManager initialized")

        # Try loading the access token on start
        self.load_access_token()
        print(f"Access token loaded: {'Yes' if self.access_token else 'No'}")

        self.current_frame = None

        try:
            # Check internet connectivity
            requests.get("https://www.google.com", timeout=5)
            
            if self.access_token:
                print("Access token found, checking if expired")
                if not self.auth_manager.is_token_expired():
                    print("Token is valid, showing dashboard")
                    self.show_dashboard()
                else:
                    print("Token is expired, refreshing")
                    self.auth_manager.refresh_access_token(self.authentication_callback)
            else:
                print("No access token, showing authentication UI")
                self.show_authentication()
        except requests.exceptions.RequestException:
            print("No internet connection")
            self.show_error("No internet connection. Please check your network and try again.")

        self.config = self.load_config()
        print("App initialization completed")

    def show_error(self, message):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ctk.CTkFrame(self)
        self.current_frame.pack(pady=20, fill="both", expand=True)
        
        error_label = ctk.CTkLabel(self.current_frame, text=message, text_color="red", font=("Arial", 16))
        error_label.pack(pady=20)
        
        retry_button = ctk.CTkButton(self.current_frame, text="Retry", command=self.retry_connection)
        retry_button.pack(pady=10)

    def retry_connection(self):
        # Remove the current error frame
        if self.current_frame:
            self.current_frame.destroy()

        try:
            # Check internet connectivity
            requests.get("https://www.google.com", timeout=5)
            
            if self.access_token:
                print("Access token found, checking if expired")
                if not self.auth_manager.is_token_expired():
                    print("Token is valid, showing dashboard")
                    self.show_dashboard()
                else:
                    print("Token is expired, refreshing")
                    self.auth_manager.refresh_access_token(self.authentication_callback)
            else:
                print("No access token, showing authentication UI")
                self.show_authentication()
        except requests.exceptions.RequestException:
            print("No internet connection")
            self.show_error("No internet connection. Please check your network and try again.")

    def show_authentication(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = AuthenticateUI(self, self.authentication_callback)
        self.current_frame.pack(pady=20)

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

            # Remove the authentication UI (if it exists) and show the dashboard
            self.show_dashboard()
        else:
            # If authentication failed, show the authentication UI again
            self.show_authentication()

    def save_access_token(self):
        """Saves the access token and expiry to a file."""
        token_data = {
            "access_token": self.access_token,
            "user_name": self.user_name,
            "token_expiry": self.auth_manager.token_expiry,
            "refresh_token": self.auth_manager.refresh_token
        }

        with open(TOKEN_FILE, "w") as token_file:
            json.dump(token_data, token_file)
        print("Access token saved.")

    def load_access_token(self):
        """Loads the access token and expiry from a file if it exists."""
        if os.path.exists(TOKEN_FILE):
            print(f"Token file found: {TOKEN_FILE}")
            with open(TOKEN_FILE, "r") as token_file:
                token_data = json.load(token_file)
                self.access_token = token_data.get("access_token")
                self.user_name = token_data.get("user_name")

                self.auth_manager.access_token = self.access_token
                self.auth_manager.refresh_token = token_data.get("refresh_token")
                self.auth_manager.token_expiry = token_data.get("token_expiry")
            print(f"Access token loaded: {'Yes' if self.access_token else 'No'}")
        else:
            print(f"Token file not found: {TOKEN_FILE}")

    def show_dashboard(self):
        """Display the dashboard UI after successful authentication."""
        if self.current_frame:
            self.current_frame.destroy()
        if self.user_name:
            self.dashboard = DashboardUI(self, self.user_name, self.navigate, self.save_output_directory)
            self.dashboard.pack(expand=True, fill="both")
        else:
            print("Error: User is not authenticated. Cannot show dashboard.")

    def navigate(self, portfolio, output_dir, selected_date, dashboard_ui=None):
        if self.dashboard:
            self.dashboard.pack_forget()
        if portfolio == "Alder":
            self.current_frame = AlderPortfolioUI2(self, output_dir, selected_date, self.process_portfolio, self.show_dashboard, dashboard_ui or self.dashboard)
            self.current_frame.pack(expand=True, fill="both")
        elif portfolio == "White Rabbit":
            self.current_frame = WhiteRabbitPortfolioUI(self, output_dir, selected_date, self.process_portfolio, self.show_dashboard)
            self.current_frame.pack(expand=True, fill="both")


    def save_output_directory(self, directory):
        self.config['output_directory'] = directory
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def process_portfolio(self, csv_paths, output_dir):
        # Implement your CSV processing logic here
        print(f"Processing {len(csv_paths)} CSV files in {output_dir}")
        # After processing, you might want to show a success message or return to the dashboard
        self.show_dashboard()

if __name__ == "__main__":
    app = App()
    app.mainloop()
