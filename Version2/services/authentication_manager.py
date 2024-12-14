import msal
import os
import json
import webbrowser
import threading
import pyperclip
import time
import requests
from requests.exceptions import ConnectionError, RequestException
from services.api_service import ApiService
from msal import PublicClientApplication
import tkinter as tk
from tkinter import messagebox
import logging

# Define your constants
APPLICATION_ID = "c5b98c30-7848-4882-8e16-77cb80812d55"
AUTHORITY_URL = "https://login.microsoftonline.com/consumers/"
SCOPES = ["User.Read", "Files.ReadWrite.All"]
BASE_URL = "https://graph.microsoft.com/v1.0/"
TOKEN_FILE = "access_token.json"

class AuthenticationManager:
    def __init__(self):
        self.app = None
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.initialize_msal()

    def initialize_msal(self):
        # Configure logging
        logging.getLogger('msal').setLevel(logging.DEBUG)
        
        try:
            self.app = PublicClientApplication(
                APPLICATION_ID,
                authority=AUTHORITY_URL
            )
        except requests.exceptions.ConnectionError:
            self.show_connection_error()
            raise
        except Exception as e:
            logging.error(f"Failed to initialize MSAL: {str(e)}")
            raise

    def initialize_app(self, max_retries=3):
        print("Attempting to initialize app")
        for attempt in range(max_retries):
            try:
                if self.check_internet_connection():
                    print("Internet connection detected")
                    self.app = msal.PublicClientApplication(APPLICATION_ID, authority=AUTHORITY_URL)
                    self.error_message = None
                    self.is_authenticated = True
                    print("Authentication successful")
                    logging.debug("Authentication successful")
                    return True
                else:
                    print("No internet connection detected")
                    self.error_message = "No internet connection detected."
            except (ConnectionError, RequestException) as e:
                print(f"Connection error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    self.error_message = f"Failed to initialize authentication after {max_retries} attempts."
                    break
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time} seconds before retrying")
                time.sleep(wait_time)
        
        self.is_authenticated = False
        if not self.error_message:
            self.error_message = "Failed to initialize authentication. Please check your internet connection."
        print(f"Authentication failed. Error message: {self.error_message}")
        return False

    @staticmethod
    def check_internet_connection():
        print("Checking internet connection")
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.RequestException:
            return False

    def get_error_message(self):
        return self.error_message

    def is_auth_successful(self):
        return self.is_authenticated

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
        if not self.app:
            self.initialize_msal()
        
        thread = threading.Thread(target=self.run_refresh_token, args=(callback,))
        thread.start()

    def run_refresh_token(self, callback):
        if not self.app:
            print("MSAL app is not initialized")
            callback(False, None, None, None, None)
            return

        try:
            result = self.app.acquire_token_by_refresh_token(self.refresh_token, scopes=SCOPES)
            if "access_token" in result:
                self.access_token = result["access_token"]
                self.refresh_token = result.get("refresh_token", self.refresh_token)
                self.token_expiry = int(time.time()) + result["expires_in"]
                callback(True, None, self.access_token, self.refresh_token, self.token_expiry)
            else:
                print(f"Token refresh failed: {result.get('error_description', 'Unknown error')}")
                callback(False, None, None, None, None)
        except Exception as e:
            print(f"Exception during token refresh: {str(e)}")
            callback(False, None, None, None, None)

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

    def show_connection_error(self):
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Connection Error", "Unable to connect to the internet. Please check your connection and try again.")
        root.destroy()