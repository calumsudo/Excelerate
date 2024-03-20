import customtkinter as ctk
from tkinter import filedialog
from all_parsed import parse_csv_data

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
        kings_csv = self.csv_paths["Kings"]
        boom_csv = self.csv_paths["Boom"]
        bhb_csv = self.csv_paths["BHB"]
        acs_csv = self.csv_paths["ACS"]
        cv_csvs = self.csv_paths["ClearView"]

        # Check if any of the required paths are missing
        missing_files = [key for key, value in self.csv_paths.items() if not value or any(v is None for v in value) if isinstance(value, list)]
        if missing_files:
            print(f"Missing CSV files for: {', '.join(missing_files)}")
            # You can also show an alert to the user here
            return

        # Otherwise, call the processing function
        parse_csv_data(kings_csv, boom_csv, bhb_csv, acs_csv, cv_csvs, self.selected_file)

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
