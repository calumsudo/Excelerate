from ui.authenticate_ui import AuthenticateUI
from ui.dashboard_ui import DashboardUI
from workbook import get_workbook_data, add_data_to_sheet
import customtkinter as ctk
from api_calls import get_excel_files, download_excel_workbook, update_workbook
from log import log_to_file
from io import BytesIO

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Excelerate")
        self.geometry("1200x1000")
        # configure grid layout
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.access_token = None
        self.excel_files = None
        self.user_name = None
        self.workbook = None
        self.selected_workbook = None  # Ensure this is initialized
        self.output_path = None
        self.portfolio_name = None
        self.selected_date = None

        self.authenticate_ui = AuthenticateUI(self, self.authentication_callback)
        self.authenticate_ui.pack(pady=20)

    def authentication_callback(self, success, response, access_token):
        if success:
            self.user_name = response["displayName"]
            self.access_token = access_token

            self.authenticate_ui.pack_forget()  # Remove the authenticate UI

            # Retrieve excel files and store them
            self.excel_files = get_excel_files(access_token)

            # Now you can show the workbook UI
            self.show_workbook_ui(self.excel_files, self.user_name)
        else:
            self.authenticate_ui.label.configure(text="Authentication failed.")

    def show_workbook_ui(self, excel_files, user_name):
        self.dashboard_ui = DashboardUI(
            self,
            excel_files,
            user_name,
            self.workbook_callback,
            self.handle_data_processed,
        )
        self.dashboard_ui.pack(pady=20)

    def workbook_callback(
        self, selected_workbook, output_path, portfolio_name, selected_date
    ):
        self.output_path = output_path
        self.portfolio_name = portfolio_name
        self.selected_date = selected_date
        self.selected_workbook = selected_workbook  # Store selected workbook

        log_to_file(
            "Selected workbook: " + str(selected_workbook), output_path, portfolio_name
        )
        if self.access_token:
            try:
                log_to_file("Downloading workbook...", output_path, portfolio_name)
                workbook_bytes = download_excel_workbook(
                    self.access_token, selected_workbook[1], output_path, portfolio_name
                )
                self.workbook = get_workbook_data(
                    workbook_bytes, selected_workbook[0], output_path, portfolio_name
                )

            except Exception as e:
                print(f"Error downloading workbook: {str(e)}")
                self.dashboard_ui.handle_errors(str(e))
        else:
            log_to_file("Access token is not available.", output_path, portfolio_name)

    def handle_data_processed(self, data, output_path, portfolio_name, selected_date):
        # Initialize a variable to hold the final workbook bytes
        final_workbook_bytes = None

        for (
            sheet_name,
            (
                df,
                total_gross,
                total_net,
                total_fee,
                detailed_unmatched_info,
            ),
        ) in data.items():
            if df is None:
                continue

            print(f"Processing {sheet_name} data...")
            print(f"Total Gross Amount in {sheet_name}: {total_gross}")
            print(f"Total Net Amount in {sheet_name}: {total_net}")
            print(f"Total Fee in {sheet_name}: {total_fee}")

            final_bytes, unmatched_info = add_data_to_sheet(
                self.workbook,
                df,
                sheet_name,
                output_path,
                portfolio_name,
                selected_date,
            )
            if final_bytes:
                print(f"Successfully processed {sheet_name} data.")
            else:
                print(f"Error processing {sheet_name} data: final_bytes is None or empty")
                return  # Exit if processing failed

        # After all sheets have been processed, save the modified workbook to bytes
        if self.access_token and self.workbook:
            try:
                # Save the modified workbook to bytes
                output_stream = BytesIO()
                self.workbook.save(output_stream)
                output_stream.seek(0)
                final_workbook_bytes = output_stream.read()

                update_workbook(
                    self.access_token,
                    final_workbook_bytes,
                    self.output_path,
                    self.portfolio_name,
                    self.selected_workbook[1]
                )
                print("Workbook updated successfully.")
            except Exception as e:
                print(f"Error updating workbook: {str(e)}")
                self.dashboard_ui.handle_errors(str(e))

        self.dashboard_ui.reset_input_fields()


if __name__ == "__main__":
    app = App()
    app.mainloop()
