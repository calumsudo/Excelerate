import customtkinter as ctk
from tkinter import filedialog
from parsers.kings_parser import parse_kings
from parsers.boom_parser import parse_boom
from parsers.bhb_parser import parse_bhb
from parsers.cv_parser import parse_cv
from parsers.acs_parser import parse_acs
from pdf_reporter import generate_report


class WorkbookUI(ctk.CTkFrame):
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
        
        # Workbook selection
        workbook_label = ctk.CTkLabel(self, text=f"Welcome, {name}. Please select your workbook:")
        workbook_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.workbook_dropdown = ctk.CTkComboBox(self, values=excel_file_names, width=400, command=self.on_select)
        self.workbook_dropdown.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.workbook_dropdown.set("Select Workbook")
        

        # CSV file input
        csv_label = ctk.CTkLabel(self, text="Add CSV files:")
        csv_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # KINGS
        self.kings_entry = ctk.CTkEntry(self, width=100, placeholder_text="Kings CSV File Path")
        self.kings_entry.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        kings_button = ctk.CTkButton(self, text="Browse for Kings CSV", command=lambda: self.browse_csv("Kings"), width=250)
        kings_button.grid(row=4, column=1, padx=10, pady=5)

        # BOOM
        self.boom_entry = ctk.CTkEntry(self, width=100, placeholder_text="Boom CSV File Path")
        self.boom_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        boom_button = ctk.CTkButton(self, text="Browse for Boom CSV", command=lambda: self.browse_csv("Boom"), width=250)
        boom_button.grid(row=5, column=1, padx=10, pady=5)

        # BHB
        self.bhb_entry = ctk.CTkEntry(self, width=100, placeholder_text="BHB CSV File Path")
        self.bhb_entry.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        bhb_button = ctk.CTkButton(self, text="Browse for BHB CSV", command=lambda: self.browse_csv("BHB"), width=250)
        bhb_button.grid(row=6, column=1, padx=10, pady=5)

        # ACS
        self.acs_entry = ctk.CTkEntry(self, width=100, placeholder_text="ACS CSV File Path")
        self.acs_entry.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

        acs_button = ctk.CTkButton(self, text="Browse for ACS CSV", command=lambda: self.browse_csv("ACS"), width=250)
        acs_button.grid(row=7, column=1, padx=10, pady=5)

        # ClearView

        clearview_label = ctk.CTkLabel(self, text="ClearView:")
        clearview_label.grid(row=8, column=0, padx=10, pady=10, sticky="w")

        self.clearview_entries = []
        self.clearview_buttons = []

        for i in range(5):

            entry = ctk.CTkEntry(self, width=100, placeholder_text=(f"{['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][i]} ClearView CSV File Path"))
            entry.grid(row=9+i, column=0, padx=10, pady=5, sticky="ew")
            self.clearview_entries.append(entry)

            button = ctk.CTkButton(self, text=(f"Browse for ClearView {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][i]}"), command=lambda day=i: self.browse_csv(f"ClearView_{day}"), width=250)
            button.grid(row=9+i, column=1, padx=10, pady=5)
            self.clearview_buttons.append(button)

        self.grid_columnconfigure(1, weight=1)

        # Add an error message label to your UI
        self.error_message_label = ctk.CTkLabel(self, text="", font=("Arial", 10, "bold"), text_color="red")
        self.error_message_label.grid(row=15, column=0, columnspan=2, sticky="ew")

        # Process button
        process_button = ctk.CTkButton(self, text="Process CSV Files", command=self.process_csv_files, width=250)
        process_button.grid(row=14, column=0, columnspan=2, padx=10, pady=10)

    def on_select(self, event):
        # Get the name of the selected item
        selected_name = self.workbook_dropdown.get()

        # Find the index of this name in the excel_file_names list
        index = next(i for i, (name, _) in enumerate(self.excel_files) if name == selected_name)

        # Get the corresponding tuple from the excel_files list
        self.selected_file = self.excel_files[index]

    def process_csv_files(self):
        # Retrieve paths from the entries
        problem_files = []
        kings_csv = self.csv_paths["Kings"]
        if kings_csv:
            try:
                kings_pivot_table, kings_total_gross_amount, kings_total_net_amount, kings_total_fee = parse_kings(kings_csv)
            except Exception as e:
                problem_files.append(f"Kings CSV: No Column named{e} in CSV")
                print("Error in Kings CSV")
                print(e)
                print(problem_files)
            
        boom_csv = self.csv_paths["Boom"]
        if boom_csv:
            try:
                boom_pivot_table, boom_total_gross_amount, boom_total_net_amount, boom_total_fee = parse_boom(boom_csv)
            except Exception as e:
                problem_files.append(f"Boom CSV: No Column named {e} in CSV")
                print("Error in Boom CSV")
                print(e)
                print(problem_files)
            
        bhb_csv = self.csv_paths["BHB"]
        if bhb_csv:
            try:
                bhb_pivot_table, bhb_total_gross_amount, bhb_total_net_amount, bhb_total_fee = parse_bhb(bhb_csv)
            except Exception as e:
                problem_files.append(f"BHB CSV: No Column named {e} in CSV")
                print("Error in BHB CSV")
                print(e)
                print(problem_files)
        
        acs_csv = self.csv_paths["ACS"]
        if acs_csv:
            try:
                acs_pivot_table, acs_total_gross_amount, acs_total_net_amount, acs_total_fee = parse_acs(acs_csv)
            except Exception as e:
                problem_files.append(f"ACS CSV: No Column named {e} in CSV")
                print("Error in ACS CSV")
                print(e)
                print(problem_files)
            
        cv_csvs = self.csv_paths["ClearView"]
        if cv_csvs:
            try:
                cv_pivot_table, cv_total_gross_amount, cv_total_net_amount, cv_total_fee = parse_cv(cv_csvs)
            except Exception as e:
                problem_files.append(f"ClearView CSV: No Column named {e} in CSV")
                print("Error in ClearView CSV")
                print(e)
                print(problem_files)

        if problem_files:
            files_str = ", ".join(problem_files)
            print(files_str)
            self.display_error(f"Problem with {files_str}")
        else:
            self.display_error("")


        # Check if any of the required paths are missing
        missing_files = [key for key, value in self.csv_paths.items() if not value or any(v is None for v in value) if isinstance(value, list)]
        if missing_files:
            self.display_error(f"Missing CSV files for: {', '.join(missing_files)}")
            return

        # Otherwise, call the processing function
        self.display_error("")
        generate_report(kings_pivot_table, kings_total_gross_amount, kings_total_net_amount, kings_total_fee,
                        boom_pivot_table, boom_total_gross_amount, boom_total_net_amount, boom_total_fee,
                        bhb_pivot_table, bhb_total_gross_amount, bhb_total_net_amount, bhb_total_fee,
                        cv_pivot_table, cv_total_gross_amount, cv_total_net_amount, cv_total_fee,
                        acs_pivot_table, acs_total_gross_amount, acs_total_net_amount, acs_total_fee,
                        self.selected_file, self.workbook_path, "Excelerator_Report")

        # return {
        #     "kings_pivot_table": kings_pivot_table,
        #     "kings_total_gross_amount": kings_total_gross_amount,
        #     "kings_total_net_amount": kings_total_net_amount,
        #     "kings_total_fee": kings_total_fee,
        #     "boom_pivot_table": boom_pivot_table,
        #     "boom_total_gross_amount": boom_total_gross_amount,
        #     "boom_total_net_amount": boom_total_net_amount,
        #     "boom_total_fee": boom_total_fee,
        #     "bhb_pivot_table": bhb_pivot_table,
        #     "bhb_total_gross_amount": bhb_total_gross_amount,
        #     "bhb_total_net_amount": bhb_total_net_amount,
        #     "bhb_total_fee": bhb_total_fee,
        #     "cv_pivot_table": cv_pivot_table,
        #     "cv_total_gross_amount": cv_total_gross_amount,
        #     "cv_total_net_amount": cv_total_net_amount,
        #     "cv_total_fee": cv_total_fee,
        #     "acs_pivot_table": acs_pivot_table,
        #     "acs_total_gross_amount": acs_total_gross_amount,
        #     "acs_total_net_amount": acs_total_net_amount,
        #     "acs_total_fee": acs_total_fee        
        # }


    def display_error(self, message):
        """Utility method to display error messages on the UI."""
        if not hasattr(self, 'error_label'):
            self.error_label = ctk.CTkLabel(self, text="", font=("Arial", 12, "bold"), text_color="red")
            self.error_label.grid(row=15, column=0, columnspan=2, sticky="ew")
        
        self.error_label.configure(text=message)

    def browse_csv(self, entity):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            if entity == "Kings":
                self.csv_paths["Kings"] = file_path
                self.kings_entry.delete(0, "end")
                self.kings_entry.insert(0, file_path)
            elif entity == "Boom":
                self.csv_paths["Boom"] = file_path
                self.boom_entry.delete(0, "end")
                self.boom_entry.insert(0, file_path)
            elif entity == "BHB":
                self.csv_paths["BHB"] = file_path
                self.bhb_entry.delete(0, "end")
                self.bhb_entry.insert(0, file_path)
            elif entity == "ACS":
                self.csv_paths["ACS"] = file_path
                self.acs_entry.delete(0, "end")
                self.acs_entry.insert(0, file_path)
            elif entity.startswith("ClearView_"):
                day = int(entity.split("_")[1])
                self.csv_paths["ClearView"][day] = file_path
                self.clearview_entries[day].delete(0, "end")
                self.clearview_entries[day].insert(0, file_path)

    def set_workbook_paths(self, workbook_paths):
        self.workbook_dropdown.configure(values=workbook_paths)
