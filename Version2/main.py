# import customtkinter as ctk
# from ui.authenticate_ui import AuthenticateUI
# from services.authentication_manager import AuthenticationManager

# TOKEN_FILE = "access_token.json"

# ctk.set_appearance_mode("System")
# ctk.set_default_color_theme("blue")


# class App(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         self.title("Excelerate")
#         self.geometry("1200x1000")

#         # Initialize the authentication manager
#         self.auth_manager = AuthenticationManager()

#         # Determine if we need to authenticate
#         if self.auth_manager.access_token and not self.auth_manager.is_token_expired():
#             self.show_success_ui()
#         elif self.auth_manager.access_token and self.auth_manager.is_token_expired():
#             self.auth_manager.refresh_access_token(self.authentication_callback)
#         else:
#             self.show_authentication_ui()

#     # def authentication_callback(self, success, response, access_token, refresh_token, token_expiry):
#     #     if success:
#     #         # Only update user_name if response is not None (initial authentication case)
#     #         if response:
#     #             self.user_name = response.get("displayName", "Unknown User")

#     #         # Always update access_token, refresh_token, and token_expiry
#     #         self.access_token = access_token
#     #         self.auth_manager.refresh_token = refresh_token
#     #         self.auth_manager.token_expiry = token_expiry

#     #         # Save the token for future use
#     #         self.save_access_token()

#     #         # Remove the authentication UI (if it exists) and show the success UI
#     #         if hasattr(self, 'authenticate_ui'):
#     #             self.authenticate_ui.pack_forget()
#     #         self.show_success_ui()

#     #     else:
#     #         # If authentication failed, show the authentication UI again
#     #         if hasattr(self, 'authenticate_ui'):
#     #             self.authenticate_ui.label.configure(text="Authentication failed. Please try again.")
#     #         else:
#     #             # If we're trying to refresh and it fails, bring back the authentication UI
#     #             self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
#     #             self.authenticate_ui.pack(pady=20)
#     def authentication_callback(self, success, user_info, access_token, refresh_token, token_expiry):
#         if success:
#             if user_info:
#                 self.user_name = user_info.get("displayName", "Unknown User")
#             self.auth_manager.access_token = access_token
#             self.auth_manager.refresh_token = refresh_token
#             self.auth_manager.token_expiry = token_expiry
#             self.auth_manager.save_access_token()

#             # Remove the authentication UI and show success UI
#             if hasattr(self, 'authenticate_ui'):
#                 self.authenticate_ui.pack_forget()
#             self.show_success_ui()
#         else:
#             self.show_authentication_ui(failure=True)



#     def show_authentication_ui(self, failure=False):
#         """Displays the authentication UI."""
#         self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
#         if failure:
#             self.authenticate_ui.label.configure(text="Authentication failed. Please try again.")
#         self.authenticate_ui.pack(pady=20)

#     def show_success_ui(self):
#         """Displays the UI for successful authentication."""
#         success_label = ctk.CTkLabel(self, text=f"Welcome {self.auth_manager.user_name}!", font=("Arial", 18))
#         success_label.pack(pady=20)


# if __name__ == "__main__":
#     app = App()
#     app.mainloop()


import customtkinter as ctk
from ui.authenticate_ui import AuthenticateUI
from services.authentication_manager import AuthenticationManager

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Excelerate")
        self.geometry("1200x1000")
        
        # Initialize the authentication manager
        self.auth_manager = AuthenticationManager()

        # Determine if we need to authenticate
        if self.auth_manager.access_token and not self.auth_manager.is_token_expired():
            self.show_success_ui()
        elif self.auth_manager.access_token and self.auth_manager.is_token_expired():
            self.auth_manager.refresh_access_token(self.authentication_callback)
        else:
            self.show_authentication_ui()

    def authentication_callback(self, success, user_info, access_token, refresh_token, token_expiry):
        if success:
            # Only update user_name if response is not None (initial authentication case)
            if user_info:
                self.auth_manager.user_name = user_info.get("displayName", "Unknown User")

            # Always update access_token, refresh_token, and token_expiry
            self.auth_manager.access_token = access_token
            self.auth_manager.refresh_token = refresh_token
            self.auth_manager.token_expiry = token_expiry
            self.auth_manager.save_access_token()

            # Remove the authentication UI and show success UI
            if hasattr(self, 'authenticate_ui'):
                self.authenticate_ui.pack_forget()
            self.show_success_ui()
        else:
            self.show_authentication_ui(failure=True)

    def show_authentication_ui(self, failure=False):
        """Displays the authentication UI."""
        self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
        if failure:
            self.authenticate_ui.label.configure(text="Authentication failed. Please try again.")
        self.authenticate_ui.pack(pady=20)

    def show_success_ui(self):
        """Displays the UI for successful authentication."""
        success_label = ctk.CTkLabel(self, text=f"Welcome {self.auth_manager.user_name}!", font=("Arial", 18))
        success_label.pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
