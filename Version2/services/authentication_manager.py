import msal
import os
import json
import webbrowser
import threading
import pyperclip
import time
from services.api_service import ApiService


# Define your constants
APPLICATION_ID = "c5b98c30-7848-4882-8e16-77cb80812d55"
AUTHORITY_URL = "https://login.microsoftonline.com/consumers/"
SCOPES = ["User.Read", "Files.ReadWrite.All"]
BASE_URL = "https://graph.microsoft.com/v1.0/"
TOKEN_FILE = "access_token.json"

class AuthenticationManager:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.app = msal.PublicClientApplication(APPLICATION_ID, authority=AUTHORITY_URL)

        self.load_access_token()

    def initiate_device_flow(self):
        """Initiates the device flow and opens the verification URL in the browser."""
        flow = self.app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise Exception("Failed to create device flow")

        # Open the verification URL in the user's web browser
        webbrowser.open(flow["verification_uri"])
        pyperclip.copy(flow["user_code"])  # Copy the user code to the clipboard
        return flow

    def authenticate(self, flow, callback):
        """Authenticates using the device flow and passes the result to the callback."""
        def run_authentication():
            result = self.app.acquire_token_by_device_flow(flow)

            if "access_token" in result:
                self.access_token = result["access_token"]
                self.refresh_token = result.get("refresh_token")
                self.token_expiry = time.time() + result["expires_in"]

                # Use the ApiService to get the user info
                user_info = ApiService.get_user_info(self.access_token)
                self.user_name = user_info.get("displayName", "Unknown User")

                if user_info:
                    callback(True, user_info, self.access_token, self.refresh_token, self.token_expiry)
                else:
                    callback(False, None, None, None, None)
            else:
                callback(False, None, None, None, None)
        
        threading.Thread(target=run_authentication).start()

    def is_token_expired(self):
        """Check if the token has expired."""
        return time.time() >= self.token_expiry if self.token_expiry else True

    def refresh_access_token(self, callback):
        """Refreshes the access token using the refresh token."""
        def run_refresh_token():
            if self.refresh_token:
                result = self.app.acquire_token_by_refresh_token(self.refresh_token, scopes=SCOPES)

                if "access_token" in result:
                    self.access_token = result["access_token"]
                    self.token_expiry = time.time() + result["expires_in"]
                    self.refresh_token = result.get("refresh_token")  # Update refresh token if provided

                    # Debugging: Print the new access token and refresh token
                    print(f"New Access Token: {self.access_token}")
                    print(f"New Refresh Token: {self.refresh_token}")
                    print(f"New Token Expiry: {self.token_expiry} (in {result['expires_in']} seconds)")

                    callback(True, None, self.access_token, self.refresh_token, self.token_expiry)
                else:
                    print("Error: Could not refresh access token")
                    callback(False, None, None, None, None)  # Indicate failure if refresh fails

        threading.Thread(target=run_refresh_token).start()

    def save_access_token(self):
        """Saves the access token, user name, and expiry to a file."""
        token_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_expiry": self.token_expiry,
            "user_name": self.user_name  # Save the user name as well
        }

        with open(TOKEN_FILE, "w") as token_file:
            json.dump(token_data, token_file)

    def load_access_token(self):
        """Loads the access token and expiry from a file if it exists."""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as token_file:
                token_data = json.load(token_file)
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.token_expiry = token_data.get("token_expiry")
                self.user_name = token_data.get("user_name") 