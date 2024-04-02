from ui.authenticate_ui import AuthenticateUI
from ui.dashboard_ui import DashboardUI
from workbook import get_workbook_data, add_data_to_kings_sheet
import tkinter as tk
import customtkinter as ctk
from auth import global_access_token
from api_calls import get_excel_files, download_excel_workbook
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



        self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
        self.authenticate_ui.pack(pady=20)

        #self.workbook_ui = None
        self.dashboard_ui = None

        # self.dashboard_ui = DashboardUI(self, get_excel_files("access_token"), "Calum", self.workbook_callback)
        # self.dashboard_ui.pack(pady=20)



    def authentication_callback(self, success, response, access_token):
        if success:
            print("Authentication successful!")
            print("Response:", response)
            name = response['displayName']
            self.access_token = access_token

            self.authenticate_ui.pack_forget()  # Remove the authenticate UI
            self.show_workbook_ui(get_excel_files(access_token), name)  # Pass the access_token to get_excel_files
        else:
            self.authenticate_ui.label.configure(text="Authentication failed.")

    def workbook_callback(self, selected_workbook):
        # Define what should happen when a workbook is selected
        print("Selected workbook:", selected_workbook)
        if self.access_token:  # Check if the access token is available
            print("Downloading workbook...")
            # Use the stored access_token
            workbook_bytes = download_excel_workbook(self.access_token, selected_workbook[1])

            # workbook = load_workbook(filename=io.BytesIO(workbook_bytes))
            workbook = get_workbook_data(workbook_bytes, selected_workbook[0])
            self.workbook = workbook

            # The rest of your code to handle the workbook...
        else:
            print("Access token is not available.")


    def show_workbook_ui(self, excel_files, user_name):
        # Assuming 'excel_files' contains a list of workbook paths
        self.dashboard_ui = DashboardUI(self, excel_files, user_name, self.workbook_callback, self.handle_data_processed)
        self.dashboard_ui.pack(pady=20)
        # self.workbook_ui = WorkbookUI(self, excel_files, name, self.workbook_callback)
        # self.workbook_ui.pack(pady=20)

    def handle_data_processed(self, data):
        if "Kings" in data:
            kings_data = data["Kings"]
            # Unpack the values from kings_data
            kings_pivot_table, kings_total_gross_amount, kings_total_net_amount, kings_total_fee, kings_error = kings_data
            
            # If there is no error, proceed with adding data to the Kings sheet
            if not kings_error:
                # Assuming you have a function `add_data_to_kings_sheet` that accepts these parameters
                add_data_to_kings_sheet(self.workbook, kings_pivot_table)
            else:
                # Handle the error, maybe log it or show a message to the user
                print("Error processing Kings data:", kings_error)



if __name__ == "__main__":
    app = App()
    app.mainloop()