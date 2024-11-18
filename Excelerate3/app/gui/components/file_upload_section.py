import customtkinter as ctk
from pathlib import Path
from typing import List, Callable

class FileUploadSection(ctk.CTkFrame):
    def __init__(self, parent, funder: str, multi_file: bool = False, 
                 controller=None, portfolio=None):
        super().__init__(parent)
        self.funder = funder
        self.controller = controller
        self.portfolio = portfolio
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(
            self,
            text=f"{funder} Files",
            font=("Helvetica", 14, "bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(5,2))
        
        # File list - smaller fixed height
        self.file_list = ctk.CTkTextbox(self, height=60)
        self.file_list.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        
        # Button
        ctk.CTkButton(
            self,
            text="Select Files" if multi_file else "Select File",
            command=self.select_files
        ).grid(row=2, column=0, sticky="w", padx=10, pady=(2,5))
        
        self.multi_file = multi_file
        
    def select_files(self):
        filetypes = [('CSV files', '*.csv'), ('Excel files', '*.xlsx')]
        if self.multi_file:
            files = ctk.filedialog.askopenfilenames(filetypes=filetypes)
            for file in files:
                self.process_file(Path(file))
        else:
            file = ctk.filedialog.askopenfilename(filetypes=filetypes)
            if file:
                self.process_file(Path(file))
                
    def process_file(self, file_path: Path):
        self.file_list.insert('end', f"Processing: {file_path}\n")
        success, results, error = self.controller.coordinator.process_uploaded_file(
            file_path,
            portfolio=self.portfolio,
            manual_funder=self.funder  # Add this parameter
        )
        
        if success:
            self.file_list.insert('end', 
                f"✓ Success: {results['funder']}\n"
                f"  Gross Total: ${results['totals']['gross']:,.2f}\n"
                f"  Net Total: ${results['totals']['net']:,.2f}\n\n"
            )
        else:
            self.file_list.insert('end', f"✗ Error: {error}\n\n")
        
        self.file_list.see('end')