import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from parsers.kings_parser import parse_kings
from parsers.boom_parser import parse_boom
from parsers.bhb_parser import parse_bhb
from parsers.acs_parser import parse_acs
from parsers.cv_parser import parse_cv

class DashboardUI(ctk.CTkFrame):
    def __init__(self, master, excel_files, name, workbook_callback):
        super().__init__(master)
        self.workbook_callback = workbook_callback
        self.excel_files = excel_files

        excel_file_names = [name for name, _ in excel_files]

        self.workbook_path = None
        self.csv_paths = {
            "Kings": None,
            "Boom": None,
            "BHB": None,
            "ACS": None,
            "ClearView": [None] * 5
        }     

        # create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=140)
        self.sidebar_frame.grid(row=0, column=0, rowspan=20, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Sidebar label
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Excelerate", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(16, 10))

        # Sidebar Welcome User label
        self.username_label = ctk.CTkLabel(self.sidebar_frame, text=f"Welcome, {name}")
        self.username_label.grid(row=1, column=0, padx=20, pady=10)

        # Sidebar Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # Sidebar UI Scaling
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=15, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=16, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.workbook_optionmenu = ctk.CTkComboBox(self, values=excel_file_names, width=600, command=self.on_select_workbook)
        self.workbook_optionmenu.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        self.workbook_optionmenu.set("Select Workbook")

        self.fetch_workbook_button = ctk.CTkButton(master=self, fg_color=("#129635"), hover_color="#22b348", text="Fetch Workbook")
        self.fetch_workbook_button.grid(row=0, padx=10, pady=10, column=2, sticky="w") 


        # Adjust the row weights according to how you want the rows to expand
        self.grid_rowconfigure(0, weight=0)  # Header row, might not need to expand
        self.grid_rowconfigure(1, weight=0)  # Kings row, doesn't need to expand
        self.grid_rowconfigure(2, weight=0)  # Boom row, doesn't need to expand
        self.grid_rowconfigure(3, weight=0)  # BHB row, doesn't need to expand
        self.grid_rowconfigure(4, weight=0)  # ACS row, doesn't need to expand
        self.grid_rowconfigure(5, weight=0)  # ClearView row, should expand

        # create kings file upload frame, entry, button, and error message
        self.kings_upload_frame = ctk.CTkFrame(self)
        self.kings_entry = ctk.CTkEntry(self.kings_upload_frame, width=600, placeholder_text="Kings CSV File Path")
        self.kings_button = ctk.CTkButton(self.kings_upload_frame, text="Browse for Kings CSV", command=lambda: self.browse_csv("Kings"), width=250)
        self.kings_error_label = ctk.CTkLabel(self.kings_upload_frame, text="")

        # create boom file upload frame, entry and button
        self.boom_upload_frame = ctk.CTkFrame(self)
        self.boom_entry = ctk.CTkEntry(self.boom_upload_frame, width=600, placeholder_text="Boom CSV File Path")
        self.boom_button = ctk.CTkButton(self.boom_upload_frame, text="Browse for Boom CSV", command=lambda: self.browse_csv("Boom"), width=250)
        self.boom_error_label = ctk.CTkLabel(self.boom_upload_frame, text="")

        # create bhb file upload frame, entry and button
        self.bhb_upload_frame = ctk.CTkFrame(self)
        self.bhb_entry = ctk.CTkEntry(self.bhb_upload_frame, width=600, placeholder_text="BHB CSV File Path")
        self.bhb_button = ctk.CTkButton(self.bhb_upload_frame, text="Browse for BHB CSV", command=lambda: self.browse_csv("BHB"), width=250)
        self.bhb_error_label = ctk.CTkLabel(self.bhb_upload_frame, text="")

        # create acs file upload frame, entry and button
        self.acs_upload_frame = ctk.CTkFrame(self)
        self.acs_entry = ctk.CTkEntry(self.acs_upload_frame, width=600, placeholder_text="ACS CSV File Path")
        self.acs_button = ctk.CTkButton(self.acs_upload_frame, text="Browse for ACS CSV", command=lambda: self.browse_csv("ACS"), width=250)
        self.acs_error_label = ctk.CTkLabel(self.acs_upload_frame, text="")

        # create clearview file upload frame, entry and button
        self.clearview_upload_frame = ctk.CTkFrame(self)
        self.clearview_button = ctk.CTkButton(self.clearview_upload_frame, text="Browse for ClearView CSV", command=lambda: self.browse_csv("ClearView"), width=250)
        self.clearview_listbox = tk.Listbox(self.clearview_upload_frame, width=50, height=5)  # Adjust the height as needed
        self.clearview_button = ctk.CTkButton(self.clearview_upload_frame, text="Browse for ClearView CSVs",
                                      command=lambda: self.browse_csv("ClearView"), width=250)
        self.clearview_error_label = ctk.CTkLabel(self.clearview_upload_frame, text="")

        # Call this method for each file upload section
        self.setup_file_upload_frame(self.kings_upload_frame, self.kings_entry, self.kings_button, self.kings_error_label, "Kings CSV File Path", 1)
        self.setup_file_upload_frame(self.boom_upload_frame, self.boom_entry, self.boom_button, self.boom_error_label, "Boom CSV File Path", 2)
        self.setup_file_upload_frame(self.bhb_upload_frame, self.bhb_entry, self.bhb_button, self.bhb_error_label, "BHB CSV File Path", 3)
        self.setup_file_upload_frame(self.acs_upload_frame, self.acs_entry, self.acs_button, self.acs_error_label, "ACS CSV File Path", 4)
        self.setup_file_upload_frame(self.clearview_upload_frame, self.clearview_listbox, self.clearview_button, self.clearview_error_label, "ClearView CSV File Path", 5)

        self.process_button = ctk.CTkButton(self, text="Process CSV files and Generate Excel Workbook", command=self.process_all_csv_files)
        self.process_button.grid(row=6, column=1, columnspan=2, padx=10, pady=10, sticky="ew")


    def setup_file_upload_frame(self, frame, widget, button, error, text, row):
        frame.grid(row=row, column=1, padx=10, pady=10, columnspan=2, sticky="nswe")
        frame.grid_columnconfigure(0, weight=1)  # Make sure the entry/button expands to fill the frame
        if isinstance(widget, ctk.CTkEntry):
            widget.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        elif isinstance(widget, tk.Listbox):
            widget.grid(row=0, column=0, padx=10, pady=10, sticky="ew")  # Set sticky to "ew" to fill the width of the frame
        button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        error.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)     


    def on_select_workbook(self, event):
        # Get the name of the selected item
        selected_name = self.workbook_optionmenu.get()

        # Find the index of this name in the excel_file_names list
        index = next(i for i, (name, _) in enumerate(self.excel_files) if name == selected_name)

        # Get the corresponding tuple from the excel_files list
        self.selected_file = self.excel_files[index]

    def browse_csv(self, section):
        if section == "ClearView":
            # Use filedialog.askopenfilenames to allow selecting multiple files
            file_paths = filedialog.askopenfilenames(title=f"Select files for {section}")
            if file_paths:
                self.csv_paths[section] = file_paths
                # You might need to refresh a listbox or entries that show the selected file paths.
                # For example, update a Listbox:
                self.clearview_listbox.delete(0, tk.END)
                for path in file_paths:
                    self.clearview_listbox.insert(tk.END, path)
        else:
            # This is for other sections where only one file is expected.
            file_path = filedialog.askopenfilename(title=f"Select file for {section}")
            if file_path:
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
                elif section == "ClearView":
                    self.csv_paths["ClearView"] = file_path
                    self.clearview_entry.delete(0, "end")
                    self.clearview_entry.insert(0, file_path)
                else:
                    # Handle unrecognized section
                    pass
  

    def process_all_csv_files(self):
        errors = []

        # Initialize the error labels to be empty initially
        self.kings_error_label.configure(text="")
        self.boom_error_label.configure(text="")
        self.bhb_error_label.configure(text="")
        self.acs_error_label.configure(text="")
        self.clearview_error_label.configure(text="")

        # Process Kings CSV
        if self.csv_paths["Kings"]:
            kings_pivot_table, kings_total_gross_amount, kings_total_net_amount, kings_total_fee, error = self.parse_and_handle_csv("Kings")
            if error:
                self.kings_error_label.configure(text=f"Error with {error} in Kings CSV File. Ensure proper CSV was uploaded.", text_color="red")
                errors.append(error)

        # Process Boom CSV
        if self.csv_paths["Boom"]:
            boom_pivot_table, boom_total_gross_amount, boom_total_net_amount, boom_total_fee, error = self.parse_and_handle_csv("Boom")
            if error:
                self.boom_error_label.configure(text=f"Error with {error} in Boom CSV File. Ensure proper CSV was uploaded.", text_color="red")
                errors.append(error)

        # Process BHB CSV
        if self.csv_paths["BHB"]:
            bhb_pivot_table, bhb_total_gross_amount, bhb_total_net_amount, bhb_total_fee, error = self.parse_and_handle_csv("BHB")
            if error:
                self.bhb_error_label.configure(text=f"Error with {error} in BHB CSV File. Ensure proper CSV was uploaded.", text_color="red")
                errors.append(error)

        # Process ACS CSV
        if self.csv_paths["ACS"]:
            acs_pivot_table, acs_total_gross_amount, acs_total_net_amount, acs_total_fee, error = self.parse_and_handle_csv("ACS")
            if error:
                self.acs_error_label.configure(text=f"Error with {error}. Ensure proper CSV was uploaded.", text_color="red")
                errors.append(error)

        # Process ClearView CSV
        if self.csv_paths["ClearView"]:
            # Check if there are exactly 5 CSV files, raise the error if not
            if len(self.csv_paths["ClearView"]) != 5:
                error = "There should be exactly 5 CSV files for ClearView."
                self.clearview_error_label.configure(text=error, text_color="red")
                errors.append(error)
            if len(self.csv_paths["ClearView"]) != len(set(self.csv_paths["ClearView"])):
                error = "Duplicate files detected for ClearView."
                self.clearview_error_label.configure(text=error, text_color="red")
                errors.append(error)
            else:
                # Process each ClearView CSV file
                for csv_path in self.csv_paths["ClearView"]:
                    clearview_pivot_table, clearview_total_gross_amount, clearview_total_net_amount, clearview_total_fee, error = self.parse_and_handle_csv("ClearView", csv_path)
                    if error:
                        errors.append(error)

                # If there are errors specific to ClearView, display them
                if errors:
                    clearview_error_message = " | ".join(errors)
                    truncated_error_message = (clearview_error_message[:47] + '...') if len(clearview_error_message) > 50 else clearview_error_message
                    self.clearview_error_label.configure(text=f"Errors with ClearView files: {truncated_error_message}", text_color="red")

    def parse_and_handle_csv(self, section, csv_path=None):
        csv_path = self.csv_paths[section]
        if section == "Kings":
            return parse_kings(csv_path)
        elif section == "Boom":
            return parse_boom(csv_path)
        elif section == "BHB":
            return parse_bhb(csv_path)
        elif section == "ACS":
            return parse_acs(csv_path)
        elif section == "ClearView":
            return parse_cv(csv_path)
        else:
            # It might be useful to return an error if the section isn't recognized
            return (None, None, None, None, f"Unrecognized section: {section}")


