import customtkinter as ctk
from tkinter import filedialog
import os
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from ml_models.funder_classifer import FunderClassifier
class AlderPortfolioUI2(ctk.CTkFrame):
    def __init__(self, master, output_dir, selected_date, process_callback, back_callback, dashboard_ui):
        if not isinstance(master, TkinterDnD.Tk):
            raise TypeError("master must be an instance of TkinterDnD.Tk")
        super().__init__(master)
        self.output_dir = output_dir
        self.selected_date = selected_date
        self.process_callback = process_callback
        self.back_callback = back_callback
        self.dashboard_ui = dashboard_ui
        self.csv_files = []
        self.setup_ui()

    def setup_ui(self):
        # Back button
        self.back_button = ctk.CTkButton(self, text="Back to Dashboard", command=self.back_callback)
        self.back_button.pack(pady=(20, 10), padx=20, anchor="nw")

        self.title_label = ctk.CTkLabel(self, text="Alder Portfolio", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=20)

        self.date_label = ctk.CTkLabel(self, text=f"Selected Date: {self.selected_date}", font=("Arial", 16))
        self.date_label.pack(pady=10)

        # File upload section
        self.create_file_upload_section()

        # Process button
        self.process_button = ctk.CTkButton(self, text="Process CSV Files", command=self.process_files)
        self.process_button.pack(pady=20)

        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=10)

    def create_file_upload_section(self):
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=20, fill="x")

        label = ctk.CTkLabel(frame, text="Upload CSV Files:")
        label.pack(pady=(10, 5))

        self.file_listbox = tk.Listbox(frame, width=50, height=10)
        self.file_listbox.pack(pady=5, padx=10, fill="x")

        # Set up drag and drop
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.drop_files)

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=5, fill="x")

        upload_button = ctk.CTkButton(button_frame, text="Upload Files", command=self.upload_files)
        upload_button.pack(side="left", padx=5)

        remove_button = ctk.CTkButton(button_frame, text="Remove Selected", command=self.remove_selected_file)
        remove_button.pack(side="left", padx=5)

    def drop_files(self, event):
        files = self.file_listbox.tk.splitlist(event.data)
        for item in files:
            if os.path.isdir(item):
                self.process_folder(item)
            elif item.lower().endswith('.csv'):
                self.add_file(item)
            else:
                messagebox.showwarning("Invalid File", f"{item} is not a CSV file and will be skipped.")

    def process_folder(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.csv'):
                    full_path = os.path.join(root, file)
                    self.add_file(full_path)

    def upload_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        for file_path in file_paths:
            self.add_file(file_path)

    def add_file(self, file_path):
        if file_path not in self.csv_files:
            self.csv_files.append(file_path)
            self.file_listbox.insert(tk.END, os.path.basename(file_path))
            self.process_file(file_path)

    def remove_selected_file(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            file_path = self.csv_files[index]
            del self.csv_files[index]
            self.file_listbox.delete(index)

    def process_file(self, file_path):
        print(f"Processing file: {file_path}")
        try:
            predicted_funder, confidence = FunderClassifier(file_path)
            print(f"Predicted Funder: {predicted_funder}, Confidence: {confidence:.2f}")
            if predicted_funder != "Unknown":
                self.dashboard_ui.show_prediction_popup(predicted_funder, confidence, file_path)
            else:
                print("Unable to make a prediction. The file may be empty or contain no usable data.")
                # You might want to show an error message to the user here
        except Exception as e:
            print(f"Error processing file: {e}")
            # You might want to show an error message to the user here

    def process_files(self):
        if not self.csv_files:
            self.error_label.configure(text="No CSV files uploaded")
            return

        self.error_label.configure(text="")
        self.process_callback(self.csv_files, self.selected_date, self.output_dir)

    def reset(self):
        self.csv_files = []
        self.file_listbox.delete(0, tk.END)
        self.selected_date = None
        self.error_label.configure(text="")