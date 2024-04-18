from ui.authenticate_ui import AuthenticateUI
from ui.dashboard_ui import DashboardUI
from workbook import get_workbook_data, add_data_to_sheet
import customtkinter as ctk
from api_calls import get_excel_files, download_excel_workbook, update_workbook
from log import log_to_file

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

    def workbook_callback(self, selected_workbook, output_path):
        # Define what should happen when a workbook is selected
        self.output_path = output_path
        print("Selected workbook:", selected_workbook)
        log_to_file("Selected workbook: " + str(selected_workbook), output_path)
        if self.access_token:  # Check if the access token is available
            print("Downloading workbook...")
            log_to_file("Downloading workbook...", output_path)
            # Use the stored access_token
            workbook_bytes = download_excel_workbook(self.access_token, selected_workbook[1])
            self.selected_workbook = selected_workbook

            # workbook = load_workbook(filename=io.BytesIO(workbook_bytes))
            workbook = get_workbook_data(workbook_bytes, selected_workbook[0], output_path)
            self.workbook = workbook

            # The rest of your code to handle the workbook...
        else:
            print("Access token is not available.")
            log_to_file("Access token is not available.", output_path)


    def show_workbook_ui(self, excel_files, user_name):
        # Assuming 'excel_files' contains a list of workbook paths
        self.dashboard_ui = DashboardUI(self, excel_files, user_name, self.workbook_callback, self.handle_data_processed)
        self.dashboard_ui.pack(pady=20)
        # self.workbook_ui = WorkbookUI(self, excel_files, name, self.workbook_callback)
        # self.workbook_ui.pack(pady=20)


    def handle_data_processed(self, data):
        # List of sheets to try
        sheet_names = ["Kings", "Boom", "BHB", "ACS", "CV"]

        print("Data processed:", data)
        log_to_file("Data processed: " + str(data), self.output_path)

        for sheet_name in sheet_names:
            if sheet_name in data:
                sheet_data = data[sheet_name]

                # Unpack the values from sheet_data
                # Note: Ensure that the structure of sheet_data is consistent across different sheets
                pivot_table, total_gross_amount, total_net_amount, total_fee, error = sheet_data
                log_to_file(f"Processing {sheet_name} data...", self.output_path)
                log_to_file(f"Total Gross Amount in {sheet_name}: {total_gross_amount}", self.output_path)
                log_to_file(f"Total Net Amount in {sheet_name}: {total_net_amount}", self.output_path)
                log_to_file(f"Total Fee in {sheet_name}: {total_fee}", self.output_path)

                
                # If there is no error, proceed with adding data to the sheet
                if not error:
                    # Assuming you have a function `add_data_to_sheet` that accepts these parameters
                    # You might need to modify it to handle each sheet's specific data structure
                    updated_bytes = add_data_to_sheet(self.workbook, pivot_table, sheet_name)
                    log_to_file(f"Data added to sheet '{sheet_name}'.", self.output_path)
                    print(f"Data added to sheet '{sheet_name}'.")
                    # Update the workbook with the new data
                    update_workbook(self.access_token, self.selected_workbook[1], updated_bytes)

                else:
                    # Handle the error, maybe log it or show a message to the user
                    print(f"Error processing {sheet_name} data:", error)
                    log_to_file(f"Error processing {sheet_name} data: {error}", self.output_path)

        



if __name__ == "__main__":
    app = App()
    app.mainloop()