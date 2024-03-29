from ui.authenticate_ui import AuthenticateUI
from ui.workbook_ui import WorkbookUI
from ui.dashboard_ui import DashboardUI
import tkinter as tk
import customtkinter as ctk
from auth import global_access_token
from api_calls import get_excel_files
from tkinterdnd2 import TkinterDnD, DND_FILES


ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Excelerate")
        self.geometry("1100x750")
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)


        # self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(0, weight=1)  
        # self.grid_rowconfigure(1, weight=1)
        # self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
        # self.authenticate_ui.pack(pady=20)

        #self.workbook_ui = None
        # self.dashboard_ui = None

        self.dashboard_ui = DashboardUI(self, get_excel_files("access_token"), "Calum", self.workbook_callback)
        self.dashboard_ui.pack(pady=20)



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
        self.dashboard_ui = DashboardUI(self, excel_files, name, self.workbook_callback)
        self.dashboard_ui.pack(pady=20)
        # self.workbook_ui = WorkbookUI(self, excel_files, name, self.workbook_callback)
        # self.workbook_ui.pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()