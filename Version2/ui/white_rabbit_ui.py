import customtkinter as ctk
from tkinter import filedialog
import os

class WhiteRabbitPortfolioUI(ctk.CTkFrame):
    def __init__(self, master, output_dir, selected_date, process_callback, back_callback):
        super().__init__(master)
        self.output_dir = output_dir
        self.selected_date = selected_date
        self.process_callback = process_callback
        self.back_callback = back_callback
        self.csv_paths = {
            "Kings": None,
            "Boom": None,
            "BHB": None,
            "ACS": None,
            "CV": []
        }
        self.setup_ui()

    def setup_ui(self):
        # Back button
        self.back_button = ctk.CTkButton(self, text="Back to Dashboard", command=self.back_callback)
        self.back_button.pack(pady=(20, 10), padx=20, anchor="nw")

        self.title_label = ctk.CTkLabel(self, text="White Rabbit Portfolio", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=20)

        self.date_label = ctk.CTkLabel(self, text=f"Selected Date: {self.selected_date}", font=("Arial", 16))
        self.date_label.pack(pady=10)

        # CSV file upload sections
        self.create_file_upload_section("Kings")
        self.create_file_upload_section("Boom")
        self.create_file_upload_section("BHB")
        self.create_file_upload_section("ACS")
        self.create_file_upload_section("CV", multiple=True)

        # Process button
        self.process_button = ctk.CTkButton(self, text="Process CSV Files", command=self.process_files)
        self.process_button.pack(pady=20)

        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=10)

    def create_file_upload_section(self, name, multiple=False):
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=20, fill="x")

        label = ctk.CTkLabel(frame, text=f"{name} CSV:")
        label.pack(side="left", padx=(0, 10))

        if multiple:
            self.csv_paths[name] = []
            listbox = ctk.CTkTextbox(frame, height=60, width=300)
            listbox.pack(side="left", expand=True, fill="x", padx=(0, 10))
            setattr(self, f"{name.lower()}_listbox", listbox)
        else:
            entry = ctk.CTkEntry(frame, width=300)
            entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
            setattr(self, f"{name.lower()}_entry", entry)

        button = ctk.CTkButton(frame, text="Browse", command=lambda: self.browse_csv(name, multiple))
        button.pack(side="right")

    def browse_csv(self, name, multiple):
        if multiple:
            file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
            if file_paths:
                self.csv_paths[name] = list(file_paths)
                listbox = getattr(self, f"{name.lower()}_listbox")
                listbox.delete("1.0", "end")
                for path in file_paths:
                    listbox.insert("end", f"{os.path.basename(path)}\n")
        else:
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if file_path:
                self.csv_paths[name] = file_path
                entry = getattr(self, f"{name.lower()}_entry")
                entry.delete(0, "end")
                entry.insert(0, os.path.basename(file_path))

    def process_files(self):
        missing_files = [name for name, path in self.csv_paths.items() if not path]
        if missing_files:
            self.error_label.configure(text=f"Missing CSV files for: {', '.join(missing_files)}")
            return

        self.error_label.configure(text="")
        self.process_callback(self.csv_paths, self.output_dir)

    def reset(self):
        for name in self.csv_paths:
            self.csv_paths[name] = None if name != "CV" else []
            if name == "CV":
                listbox = getattr(self, f"{name.lower()}_listbox")
                listbox.delete("1.0", "end")
            else:
                entry = getattr(self, f"{name.lower()}_entry")
                entry.delete(0, "end")
        self.error_label.configure(text="")
