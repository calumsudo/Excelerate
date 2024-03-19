from ui.authenticate_ui import AuthenticateUI
from ui.workbook_ui import WorkbookUI
import tkinter as tk
import customtkinter as ctk
from auth import global_access_token
from api_calls import get_excel_files

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Excelerate")
        self.geometry("700x700")

        self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
        self.authenticate_ui.pack(pady=20)

        self.workbook_ui = None

    def authentication_callback(self, success, response, access_token):
        if success:
            print("Authentication successful!")
            print("Response:", response)
            name = response['displayName']

            self.authenticate_ui.pack_forget()  # Remove the authenticate UI
            self.show_workbook_ui(get_excel_files(access_token), name)  # Pass the access_token to get_excel_files
        else:
            self.authenticate_ui.label.configure(text="Authentication failed.")

    def workbook_callback(self, selected_workbook):
        # Define what should happen when a workbook is selected
        pass

    def show_workbook_ui(self, excel_files, name):
        # Assuming 'excel_files' contains a list of workbook paths
        self.workbook_ui = WorkbookUI(self, excel_files, name, self.workbook_callback)
        self.workbook_ui.pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()