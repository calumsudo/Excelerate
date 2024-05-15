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
        self.geometry("1200x800")
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
        self.authenticate_ui.pack(pady=20)

        self.dashboard_ui = None

    def authentication_callback(self, success, response, access_token):
        if success:
            name = response["displayName"]
            self.access_token = access_token

            self.authenticate_ui.pack_forget()  # Remove the authenticate UI
            self.show_workbook_ui(
                get_excel_files(access_token), name
            )  # Pass the access_token to get_excel_files
        else:
            self.authenticate_ui.label.configure(text="Authentication failed.")

    def workbook_callback(
        self, selected_workbook, output_path, portfolio_name, selected_date
    ):
        # Define what should happen when a workbook is selected
        self.output_path = output_path
        self.portfolio_name = portfolio_name
        self.selected_date = selected_date

        log_to_file(
            "Selected workbook: " + str(selected_workbook), output_path, portfolio_name
        )
        if self.access_token:  # Check if the access token is available
            try:
                log_to_file("Downloading workbook...", output_path, portfolio_name)
                workbook_bytes = download_excel_workbook(
                    self.access_token, selected_workbook[1], output_path, portfolio_name
                )
                self.selected_workbook = selected_workbook

                workbook = get_workbook_data(
                    workbook_bytes, selected_workbook[0], output_path, portfolio_name
                )
                self.workbook = workbook

                # The rest of your code to handle the workbook...
            except Exception as e:
                self.dashboard_ui.handle_errors(str(e))
        else:
            log_to_file("Access token is not available.", output_path, portfolio_name)

    def show_workbook_ui(self, excel_files, user_name):
        # Assuming 'excel_files' contains a list of workbook paths
        self.dashboard_ui = DashboardUI(
            self,
            excel_files,
            user_name,
            self.workbook_callback,
            self.handle_data_processed,
        )
        self.dashboard_ui.pack(pady=20)

    def handle_data_processed(self, data):
        # List of sheets to try
        sheet_names = ["Kings", "Boom", "BHB", "ACS", "CV"]
        log_to_file(
            "Data processed: " + str(data), self.output_path, self.portfolio_name
        )

        for sheet_name in sheet_names:
            if sheet_name in data:
                sheet_data = data[sheet_name]

                pivot_table, total_gross_amount, total_net_amount, total_fee, error = (
                    sheet_data
                )
                log_to_file(
                    f"Processing {sheet_name} data...",
                    self.output_path,
                    self.portfolio_name,
                )
                log_to_file(
                    f"Total Gross Amount in {sheet_name}: {total_gross_amount}",
                    self.output_path,
                    self.portfolio_name,
                )
                log_to_file(
                    f"Total Net Amount in {sheet_name}: {total_net_amount}",
                    self.output_path,
                    self.portfolio_name,
                )
                log_to_file(
                    f"Total Fee in {sheet_name}: {total_fee}",
                    self.output_path,
                    self.portfolio_name,
                )

                if not error:
                    try:
                        final_bytes, detailed_unmatched_info = add_data_to_sheet(
                            self.workbook,
                            pivot_table,
                            sheet_name,
                            self.output_path,
                            self.portfolio_name,
                            self.selected_date,
                        )
                        log_to_file(
                            f"Data added to sheet '{sheet_name}'.",
                            self.output_path,
                            self.portfolio_name,
                        )
                        updated_content = update_workbook(
                            self.access_token,
                            self.selected_workbook[1],
                            final_bytes,
                            self.output_path,
                            self.portfolio_name,
                        )
                        self.dashboard_ui.handle_update_response(
                            updated_content, detailed_unmatched_info
                        )
                    except Exception as e:
                        self.dashboard_ui.handle_errors(str(e))
                else:
                    log_to_file(
                        f"Error processing {sheet_name} data: {error}",
                        self.output_path,
                        self.portfolio_name,
                    )


if __name__ == "__main__":
    app = App()
    app.mainloop()
