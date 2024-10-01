import customtkinter as ctk
import tkinter as tk
from tkcalendar import Calendar
from tkinter import filedialog
from parsers.kings_parser import parse_kings
from parsers.boom_parser import parse_boom
from parsers.bhb_parser import parse_bhb
from parsers.acs_parser import parse_acs
from parsers.vesper_parser import parse_VSPR
from parsers.cv_parser import parse_cv
from log import log_to_file
from datetime import datetime
from pdf_reporter import generate_report
import os


class DashboardUI(ctk.CTkFrame):
    def __init__(
        self, master, excel_files, user_name, workbook_callback, data_processed_callback
    ):
        super().__init__(master)
        self.workbook_callback = workbook_callback
        self.excel_files = excel_files
        self.data_processed_callback = data_processed_callback
        self.workbook_optionmenu_var = tk.StringVar(self)
        self.output_dir_var = tk.StringVar(self)
        self.unmatched_rows = []
        self.selected_date = None

        excel_file_names = [user_name for user_name, _ in excel_files]

        self.workbook_path = None
        self.csv_paths = {
            "Kings": None,
            "Boom": None,
            "BHB": None,
            "ACS": None,
            "VSPR": None,
            "CV": [],
        }

        # create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=140)
        self.sidebar_frame.grid(row=0, column=0, rowspan=20, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)

        # Sidebar label
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Excelerate",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(16, 10))

        # Sidebar Welcome User label
        self.username_label = ctk.CTkLabel(
            self.sidebar_frame, text=f"Welcome, {user_name}"
        )
        self.username_label.grid(row=1, column=0, padx=20, pady=10)

        # Add an output directory label
        self.output_dir_label = ctk.CTkLabel(
            self.sidebar_frame, text="Output Directory:", anchor="w"
        )
        self.output_dir_label.grid(row=4, column=0, padx=20, pady=(10, 0))

        # Add an entry widget linked to the StringVar
        self.output_dir_entry = ctk.CTkEntry(
            self.sidebar_frame,
            textvariable=self.output_dir_var,
            width=120,
            placeholder_text="Select Folder",
        )
        self.output_dir_entry.grid(row=5, column=0, padx=20, pady=(10, 0))

        # Add a button to browse for a directory
        self.output_dir_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Browse",
            command=self.select_output_directory,
            width=120,
        )
        self.output_dir_button.grid(row=6, column=0, padx=20, pady=(10, 0))

        # Add an empty label to act as a spacer
        self.spacer_label = ctk.CTkLabel(self.sidebar_frame, text="")
        self.spacer_label.grid(row=8, column=0, sticky="nsew")

        self.portfolio_label = ctk.CTkLabel(
            self.sidebar_frame, text="Portfolio:", anchor="w"
        )
        self.portfolio_label.grid(row=9, column=0, padx=20, pady=(10, 0))

        # Define the event handler for the radio buttons
        def portfolio_selection_event():
            log_to_file(
                f"Portfolio selection changed to {self.portfolio_var.get()}",
                self.output_dir_var.get(),
                self.portfolio_var.get(),
            )

        # Create a tkinter variable to hold the value of the selected radio button
        self.portfolio_var = tk.IntVar(value=1)

        # Create the radio buttons
        self.alder_rhcm_button = ctk.CTkRadioButton(
            self.sidebar_frame,
            text="Alder",
            command=portfolio_selection_event,
            variable=self.portfolio_var,
            value=1,
        )
        self.white_rabbit_button = ctk.CTkRadioButton(
            self.sidebar_frame,
            text="White Rabbit",
            command=portfolio_selection_event,
            variable=self.portfolio_var,
            value=2,
        )

        # Position the radio buttons in the grid
        self.alder_rhcm_button.grid(row=10, column=0, padx=20, pady=(10, 0))
        self.white_rabbit_button.grid(row=11, column=0, padx=20, pady=(10, 0))
        self.alder_rhcm_button.configure(state="disabled")
        self.white_rabbit_button.configure(state="disabled")

        # Add a selection for which Friday (Date) to use
        self.date_label = ctk.CTkLabel(
            self.sidebar_frame, text="Select Friday Date:", anchor="w"
        )
        self.date_label.grid(row=12, column=0, padx=20, pady=(10, 0))
        self.calendar = Calendar(
            self.sidebar_frame,
            selectmode="day",
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
        )
        self.calendar.grid(row=13, column=0, padx=20, pady=(10, 0))
        self.calendar.bind("<<CalendarSelected>>", self.on_date_select)
        self.calendar.configure(state="disabled")

        # Sidebar Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=16, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionmenu.grid(row=17, column=0, padx=20, pady=(10, 10))

        # Sidebar UI Scaling
        self.scaling_label = ctk.CTkLabel(
            self.sidebar_frame, text="UI Scaling:", anchor="w"
        )
        self.scaling_label.grid(row=18, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event,
        )
        self.scaling_optionmenu.grid(row=19, column=0, padx=20, pady=(10, 20))

        # Now, set the rowconfigure to the last row to push everything up
        self.sidebar_frame.grid_rowconfigure(20, weight=1)

        # create main entry and button
        self.workbook_optionmenu = ctk.CTkComboBox(
            self,
            values=excel_file_names,
            width=600,
            variable=self.workbook_optionmenu_var,
        )
        self.workbook_optionmenu.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        self.workbook_optionmenu.set(
            "Select Workbook - (Choose an Output Directory First)"
        )
        self.workbook_optionmenu.configure(state="disabled")
        self.output_dir_var.trace_add("write", self.check_output_directory)

        # Initialize fetch_workbook_button (Initially disabled)
        self.fetch_workbook_button = ctk.CTkButton(
            master=self,
            fg_color=("#129635"),
            hover_color="#22b348",
            text="Fetch Workbook",
            command=self.on_select_workbook,
        )
        self.fetch_workbook_button.grid(row=0, padx=10, pady=10, column=2, sticky="w")
        self.fetch_workbook_button.configure(state="disabled")
        self.workbook_optionmenu_var.trace_add(
            "write", self.enable_fetch_workbook_button
        )

        # Adjust the row weights according to how you want the rows to expand
        self.grid_rowconfigure(0, weight=0)  # Header row, might not need to expand
        self.grid_rowconfigure(1, weight=0)  # Kings row, doesn't need to expand
        self.grid_rowconfigure(2, weight=0)  # Boom row, doesn't need to expand
        self.grid_rowconfigure(3, weight=0)  # BHB row, doesn't need to expand
        self.grid_rowconfigure(4, weight=0)  # ACS row, doesn't need to expand
        self.grid_rowconfigure(5, weight=0)  # Vesper row, doesn't need to expand
        self.grid_rowconfigure(6, weight=0)  # CV row, should expand


        # create kings file upload frame, entry, button, and error message
        self.kings_upload_frame = ctk.CTkFrame(self)
        self.kings_entry = ctk.CTkEntry(
            self.kings_upload_frame, width=600, placeholder_text="Kings CSV File Path"
        )
        self.kings_button = ctk.CTkButton(
            self.kings_upload_frame,
            text="Browse for Kings CSV",
            command=lambda: self.browse_csv("Kings"),
            width=250,
        )
        self.kings_error_label = ctk.CTkLabel(self.kings_upload_frame, text="")

        # create boom file upload frame, entry, button, and error message
        self.boom_upload_frame = ctk.CTkFrame(self)
        self.boom_entry = ctk.CTkEntry(
            self.boom_upload_frame, width=600, placeholder_text="Boom CSV File Path"
        )
        self.boom_button = ctk.CTkButton(
            self.boom_upload_frame,
            text="Browse for Boom CSV",
            command=lambda: self.browse_csv("Boom"),
            width=250,
        )
        self.boom_error_label = ctk.CTkLabel(self.boom_upload_frame, text="")

        # create bhb file upload frame, entry, button, and error message
        self.bhb_upload_frame = ctk.CTkFrame(self)
        self.bhb_entry = ctk.CTkEntry(
            self.bhb_upload_frame, width=600, placeholder_text="BHB CSV File Path"
        )
        self.bhb_button = ctk.CTkButton(
            self.bhb_upload_frame,
            text="Browse for BHB CSV",
            command=lambda: self.browse_csv("BHB"),
            width=250,
        )
        self.bhb_error_label = ctk.CTkLabel(self.bhb_upload_frame, text="")

        # create acs file upload frame, entry, button, and error message
        self.acs_upload_frame = ctk.CTkFrame(self)
        self.acs_entry = ctk.CTkEntry(
            self.acs_upload_frame, width=600, placeholder_text="ACS CSV File Path"
        )
        self.acs_button = ctk.CTkButton(
            self.acs_upload_frame,
            text="Browse for ACS CSV",
            command=lambda: self.browse_csv("ACS"),
            width=250,
        )
        self.acs_error_label = ctk.CTkLabel(self.acs_upload_frame, text="")

        # create vesper file upload frame, entry, button, and error message
        self.VSPR_upload_frame = ctk.CTkFrame(self)
        self.VSPR_entry = ctk.CTkEntry(
            self.VSPR_upload_frame, width=600, placeholder_text="Vesper CSV File Path"
        )
        self.VSPR_button = ctk.CTkButton(
            self.VSPR_upload_frame,
            text="Browse for Vesper CSV",
            command=lambda: self.browse_csv("VSPR"),
            width=250,
        )
        self.VSPR_error_label = ctk.CTkLabel(self.VSPR_upload_frame, text="")

        # create CV file upload frame, listbox, button, and error message
        self.clearview_upload_frame = ctk.CTkFrame(self)
        self.clearview_listbox = tk.Listbox(
            self.clearview_upload_frame, width=50, height=5
        )  # Adjust the height as needed
        self.clearview_button = ctk.CTkButton(
            self.clearview_upload_frame,
            text="Browse for CV CSVs",
            command=lambda: self.browse_csv("CV"),
            width=250,
        )
        self.clearview_error_label = ctk.CTkLabel(self.clearview_upload_frame, text="")

        # Call this method for each file upload section
        self.setup_file_upload_frame(
            self.kings_upload_frame,
            self.kings_entry,
            self.kings_button,
            self.kings_error_label,
            "Kings CSV File Path",
            1,
        )
        self.setup_file_upload_frame(
            self.boom_upload_frame,
            self.boom_entry,
            self.boom_button,
            self.boom_error_label,
            "Boom CSV File Path",
            2,
        )
        self.setup_file_upload_frame(
            self.bhb_upload_frame,
            self.bhb_entry,
            self.bhb_button,
            self.bhb_error_label,
            "BHB CSV File Path",
            3,
        )
        self.setup_file_upload_frame(
            self.acs_upload_frame,
            self.acs_entry,
            self.acs_button,
            self.acs_error_label,
            "ACS CSV File Path",
            4,
        )
        self.setup_file_upload_frame(
            self.VSPR_upload_frame,
            self.VSPR_entry,
            self.VSPR_button,
            self.VSPR_error_label,
            "Vesper CSV File Path",
            5,  # Vesper is at row 5
        )
        self.setup_file_upload_frame(
            self.clearview_upload_frame,
            self.clearview_listbox,
            self.clearview_button,
            self.clearview_error_label,
            "CV CSV File Path",
            6,  # CV moves to row 6
        )

        self.process_button = ctk.CTkButton(
            self,
            text="Process CSV files and Generate Excel Workbook",
            command=self.process_all_csv_files,
        )
        self.process_button.grid(
            row=7, column=1, columnspan=2, padx=10, pady=10, sticky="ew"
        )

        # Error label for the entire frame
        self.error_label = ctk.CTkLabel(self, text="")
        self.error_label.grid(row=8, column=1, columnspan=2, padx=10, pady=(0, 10))

        # Disable all buttons until workbook is selected
        self.kings_button.configure(state="disabled")
        self.boom_button.configure(state="disabled")
        self.bhb_button.configure(state="disabled")
        self.acs_button.configure(state="disabled")
        self.VSPR_button.configure(state="disabled")  # Added Vesper button
        self.clearview_button.configure(state="disabled")
        self.process_button.configure(state="disabled")

# Inside the DashboardUI class

    def check_output_directory(self, *args):
        directory = self.output_dir_var.get()
        radio_button_selected = self.portfolio_var.get()

        if directory and radio_button_selected:
            self.workbook_optionmenu.configure(state="normal")
        else:
            self.workbook_optionmenu.configure(state="disabled")
            self.fetch_workbook_button.configure(state="disabled")

    def select_output_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            # If a directory is selected, set it and enable the workbook dropdown
            self.output_dir_var.set(directory)
            self.alder_rhcm_button.configure(state="normal")
            self.white_rabbit_button.configure(state="normal")
            self.calendar.configure(state="normal")
        else:
            # No directory selected, ensure the workbook dropdown is disabled
            self.output_dir_var.set("")
            self.workbook_optionmenu.configure(state="disabled")
            self.fetch_workbook_button.configure(state="disabled")

    def on_date_select(self, event):
        selected_date = self.calendar.get_date()
        self.selected_date = datetime.strptime(selected_date, "%m/%d/%y")

        day_month = self.selected_date.strftime("%d/%m").lstrip("0").replace("/0", "/")
        log_to_file(
            f"Selected date: {day_month}",
            self.output_dir_var.get(),
            self.portfolio_var.get(),
        )

    def setup_file_upload_frame(self, frame, widget, button, error, text, row):
        frame.grid(row=row, column=1, padx=10, pady=10, columnspan=2, sticky="nswe")
        frame.grid_columnconfigure(0, weight=1)  # Make sure the entry/button expands to fill the frame
        if isinstance(widget, ctk.CTkEntry):
            widget.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        elif isinstance(widget, tk.Listbox):
            widget.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        error.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def enable_fetch_workbook_button(self, *args):
        """Enable the fetch_workbook_button when a workbook is selected."""
        selected_value = self.workbook_optionmenu_var.get()
        if (
            selected_value
            and selected_value != "Select Workbook - (Choose an Output Directory First)"
        ):
            self.fetch_workbook_button.configure(state="normal")
        else:
            self.fetch_workbook_button.configure(state="disabled")

    def on_select_workbook(self):
        # Get the name of the selected item
        selected_name = self.workbook_optionmenu.get()
        self.enable_csv_buttons()

        if (
            selected_name
            and selected_name != "Select Workbook - (Choose an Output Directory First)"
        ):
            self.fetch_workbook_button.configure(state="normal")  # Enable the button
        else:
            self.fetch_workbook_button.configure(state="disabled")  # Disable the button

        # Find the index of this name in the excel_file_names list
        index = next(
            (
                i
                for i, (name, _) in enumerate(self.excel_files)
                if name == selected_name
            ),
            None,
        )

        # If a valid workbook is selected, call the workbook callback function
        if index is not None:
            self.selected_file = self.excel_files[index]
            self.workbook_callback(
                self.selected_file,
                self.output_dir_var.get(),
                self.portfolio_var.get(),
                self.selected_date,
            )
            log_to_file(
                "Processing workbook...",
                self.output_dir_var.get(),
                self.portfolio_var.get(),
            )
        else:
            self.selected_file = None

    def enable_csv_buttons(self):
        self.kings_button.configure(state="normal")
        self.boom_button.configure(state="normal")
        self.bhb_button.configure(state="normal")
        self.acs_button.configure(state="normal")
        self.VSPR_button.configure(state="normal")  # Added Vesper button
        self.clearview_button.configure(state="normal")
        self.process_button.configure(state="normal")


    def browse_csv(self, section):
        if section == "CV":
            # Use filedialog.askopenfilenames to allow selecting multiple files
            file_paths = filedialog.askopenfilenames(
                title=f"Select files for {section}",
                filetypes=[("CSV files", "*.csv")],  # Limit to CSV files
            )
            if file_paths:
                # Filter out any directories (shouldn't be necessary, but added for safety)
                file_paths = [path for path in file_paths if os.path.isfile(path)]
                self.csv_paths[section] = file_paths
                # Update the Listbox with selected file paths
                self.clearview_listbox.delete(0, tk.END)
                for path in file_paths:
                    self.clearview_listbox.insert(tk.END, path)
        else:
            # For other sections where only one file is expected.
            file_path = filedialog.askopenfilename(
                title=f"Select file for {section}",
                filetypes=[("CSV files", "*.csv")],  # Limit to CSV files
            )
            if file_path and os.path.isfile(file_path):
                if section == "Kings":
                    self.csv_paths["Kings"] = file_path
                    self.kings_entry.delete(0, "end")
                    self.kings_entry.insert(0, file_path)
                elif section == "Boom":
                    self.csv_paths["Boom"] = file_path
                    self.boom_entry.delete(0, "end")
                    self.boom_entry.insert(0, file_path)
                elif section == "BHB":
                    self.csv_paths["BHB"] = file_path
                    self.bhb_entry.delete(0, "end")
                    self.bhb_entry.insert(0, file_path)
                elif section == "ACS":
                    self.csv_paths["ACS"] = file_path
                    self.acs_entry.delete(0, "end")
                    self.acs_entry.insert(0, file_path)
                elif section == "VSPR":
                    self.csv_paths["VSPR"] = file_path
                    self.VSPR_entry.delete(0, "end")
                    self.VSPR_entry.insert(0, file_path)
                else:
                    # Handle unrecognized section
                    log_to_file(
                        f"Unrecognized section: {section}",
                        self.output_dir_var.get(),
                        self.portfolio_var.get(),
                    )

    def process_all_csv_files(self):
        errors = []

        # Initialize the error labels to be empty initially
        self.kings_error_label.configure(text="")
        self.boom_error_label.configure(text="")
        self.bhb_error_label.configure(text="")
        self.acs_error_label.configure(text="")
        self.VSPR_error_label.configure(text="")
        self.clearview_error_label.configure(text="")

        # Process each section
        sections = ["Kings", "Boom", "BHB", "ACS", "VSPR", "CV"]
        processed_data = {}
        for section in sections:
            if self.csv_paths.get(section):
                result = self.parse_and_handle_csv(section)
                if result[-1]:
                    errors.append(result[-1])
                processed_data[section] = result

        if not errors:
            output_path = self.output_dir_var.get()
            portfolio_name = "Alder" if self.portfolio_var.get() == 1 else "White Rabbit"
            selected_date = self.selected_date

            self.data_processed_callback(
                processed_data,
                output_path,
                portfolio_name,
                selected_date
            )

            # Assuming all pivot tables and totals are in processed_data
            generate_report(
                processed_data["Kings"][0], processed_data["Kings"][1], processed_data["Kings"][2], processed_data["Kings"][3],
                processed_data["Boom"][0], processed_data["Boom"][1], processed_data["Boom"][2], processed_data["Boom"][3],
                processed_data["BHB"][0], processed_data["BHB"][1], processed_data["BHB"][2], processed_data["BHB"][3],
                processed_data["CV"][0], processed_data["CV"][1], processed_data["CV"][2], processed_data["CV"][3],
                processed_data["ACS"][0], processed_data["ACS"][1], processed_data["ACS"][2], processed_data["ACS"][3],
                processed_data["VSPR"][0], processed_data["VSPR"][1], processed_data["VSPR"][2], processed_data["VSPR"][3],
                self.selected_file,
                output_path,
                portfolio_name,
                self.unmatched_rows,
            )
        else:
            error_message = "Errors occurred: " + " | ".join(errors)
            self.error_label.configure(text=error_message, text_color="red")
            log_to_file(error_message, self.output_dir_var.get(), self.portfolio_var.get())


    def parse_and_handle_csv(self, section):
        portfolio = "Alder" if self.portfolio_var.get() == 1 else "White Rabbit"
        try:
            if section == "CV":
                csv_paths = self.csv_paths["CV"]
                return parse_cv(csv_paths, self.output_dir_var.get(), portfolio)
            else:
                csv_path = self.csv_paths[section]
                if section == "Kings":
                    return parse_kings(csv_path, self.output_dir_var.get(), portfolio)
                elif section == "Boom":
                    return parse_boom(csv_path, self.output_dir_var.get(), portfolio)
                elif section == "BHB":
                    return parse_bhb(csv_path, self.output_dir_var.get(), portfolio)
                elif section == "ACS":
                    return parse_acs(csv_path, self.output_dir_var.get(), portfolio)
                elif section == "VSPR":
                    return parse_VSPR(csv_path, self.output_dir_var.get(), portfolio)
                else:
                    return (None, None, None, None, f"Unrecognized section: {section}")
        except Exception as e:
            error_message = f"An error occurred while processing the {section} CSV: {str(e)}"
            log_to_file(error_message, self.output_dir_var.get(), portfolio)
            return (None, None, None, None, error_message)



    def handle_update_response(self, updated_content, detailed_unmatched_info):

        self.unmatched_rows.extend(detailed_unmatched_info)

        # Process the updated content or display messages to the user
        if updated_content:
            log_to_file(
                "Workbook updated successfully.",
                self.output_dir_var.get(),
                self.portfolio_var.get(),
            )
            log_to_file(
                updated_content, self.output_dir_var.get(), self.portfolio_var.get()
            )

            # Reset inputs for new operations
            self.reset_input_fields()
            # Add code to display success message or update UI accordingly
        else:
            log_to_file(
                "Failed to update workbook.",
                self.output_dir_var.get(),
                self.portfolio_var.get(),
            )
            # Add code to display error message or handle the failure scenario

    def reset_input_fields(self):
        # Reset CSV file paths and clear the UI components for file paths
        self.csv_paths = {
            "Kings": None,
            "Boom": None,
            "BHB": None,
            "ACS": None,
            "VSPR": None,
            "CV": [],
        }

        # Clear entries
        self.kings_entry.delete(0, "end")
        self.boom_entry.delete(0, "end")
        self.bhb_entry.delete(0, "end")
        self.acs_entry.delete(0, "end")
        self.VSPR_entry.delete(0, "end")
        self.clearview_listbox.delete(0, tk.END)

        # Disable buttons to prevent actions without valid inputs
        self.kings_button.configure(state="disabled")
        self.boom_button.configure(state="disabled")
        self.bhb_button.configure(state="disabled")
        self.acs_button.configure(state="disabled")
        self.VSPR_button.configure(state="disabled")
        self.clearview_button.configure(state="disabled")
        self.process_button.configure(state="disabled")

        # Clear error labels
        self.kings_error_label.configure(text="")
        self.boom_error_label.configure(text="")
        self.bhb_error_label.configure(text="")
        self.acs_error_label.configure(text="")
        self.VSPR_error_label.configure(text="")
        self.clearview_error_label.configure(text="")
        self.error_label.configure(text="")


    def handle_errors(self, error_message):
        # Handle the error message
        log_to_file(error_message, self.output_dir_var.get(), self.portfolio_var.get())
        if error_message.startswith(
            "Error updating Excel file: 423 Client Error: Locked for url:"
        ):
            error_message = (
                "The Excel Workbook is open somewhere and must be closed first."
            )
        # Add code to display error message or handle the error scenario
        self.error_label.configure(text=error_message, text_color="red")
