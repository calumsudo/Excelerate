# gui/file_explorer.py

import customtkinter as ctk
from pathlib import Path
import pandas as pd
from tkinter import ttk
import shutil
from .base_window import BasePage
from managers.portfolio import Portfolio
import os
from datetime import datetime
import tkinter.messagebox as tkmb

class FileExplorer(BasePage):
    def get_portfolio(self) -> Portfolio:
        return None  # Not portfolio-specific
        
    def setup_ui(self):
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(
            header,
            text="File Explorer",
            font=("Helvetica", 24, "bold")
        ).pack(side="left", padx=10)
        
        # Sidebar for navigation tree
        sidebar = ctk.CTkFrame(self)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(0, weight=1)
        
        # Create Treeview for file navigation
        self.tree = ttk.Treeview(sidebar)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add scrollbar to tree
        tree_scroll = ttk.Scrollbar(sidebar, orient="vertical", command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Main content area
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)
        
        # File preview header
        self.preview_header = ctk.CTkFrame(self.content)
        self.preview_header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.file_label = ctk.CTkLabel(
            self.preview_header,
            text="No file selected",
            font=("Helvetica", 16)
        )
        self.file_label.pack(side="left", padx=10)
        
        # Export button
        self.export_button = ctk.CTkButton(
            self.preview_header,
            text="Export File",
            command=self.export_file,
            state="disabled"
        )
        self.export_button.pack(side="right", padx=10)
        
        # Preview area
        self.preview_frame = ctk.CTkFrame(self.content)
        self.preview_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)
        
        # Create data preview table
        self.preview_table = ttk.Treeview(self.preview_frame, show="headings")
        self.preview_table.grid(row=0, column=0, sticky="nsew")

        
        # Add scrollbars to preview table
        y_scroll = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.preview_table.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.preview_table.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        self.preview_table.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Populate file tree
        self.populate_file_tree()
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_file_selected)
        
    def populate_file_tree(self):
        """Populate the file tree with portfolio directories and files"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        base_dir = self.controller.file_manager.base_dir
        
        # Add portfolio directories
        for portfolio in Portfolio:
            portfolio_dir = base_dir / portfolio.value
            if not portfolio_dir.exists():
                continue
                
            # Add portfolio node
            portfolio_id = self.tree.insert("", "end", text=portfolio.value, open=True)
            
            # Add main subdirectories
            for subdir in ["uploads", "outputs"]:
                dir_path = portfolio_dir / subdir
                if not dir_path.exists():
                    continue
                    
                dir_id = self.tree.insert(portfolio_id, "end", text=subdir.capitalize(), open=True)
                
                # Add funder directories
                for funder_dir in dir_path.iterdir():
                    if funder_dir.is_dir():
                        funder_id = self.tree.insert(dir_id, "end", text=funder_dir.name)
                        
                        # Add files
                        for file_path in funder_dir.glob("*.*"):
                            if file_path.suffix.lower() in [".csv", ".xlsx"]:
                                # Format date from filename or file modification time
                                try:
                                    file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                                    date_str = file_date.strftime("%Y-%m-%d")
                                except:
                                    date_str = "Unknown Date"
                                    
                                self.tree.insert(
                                    funder_id, 
                                    "end",
                                    text=file_path.name,
                                    values=(str(file_path), date_str)
                                )
    
    def on_file_selected(self, event):
        """Handle file selection in tree"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        if not item["values"]:  # Directory selected
            self.clear_preview()
            return
            
        file_path = Path(item["values"][0])
        self.current_file = file_path
        self.file_label.configure(text=file_path.name)
        self.export_button.configure(state="normal")
        
        self.preview_file(file_path)
    
    def preview_file(self, file_path: Path):
        """Preview CSV or Excel file content"""
        try:
            # Clear existing preview
            for item in self.preview_table.get_children():
                self.preview_table.delete(item)
            self.preview_table["columns"] = ()
            
            # Read file based on type
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() == ".xlsx":
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file type")
                
            # Configure columns
            columns = list(df.columns)
            self.preview_table["columns"] = columns
            
            # Hide the default first column (tree column)
            self.preview_table["show"] = "headings"
            
            # Configure column headings
            for col in columns:
                self.preview_table.heading(col, text=col)
                self.preview_table.column(col, width=100)  # Default width
                
            # Add data rows (limit to first 1000 rows for performance)
            for idx, row in df.head(1000).iterrows():
                values = [str(val) for val in row]
                self.preview_table.insert("", "end", values=values)
                
        except Exception as e:
            self.show_error(f"Error previewing file: {str(e)}")
    
    def export_file(self):
        """Export selected file to user-chosen location"""
        if not hasattr(self, 'current_file'):
            return
            
        # Get destination path
        file_types = [("All Files", "*.*")]
        if self.current_file.suffix.lower() == ".csv":
            file_types = [("CSV Files", "*.csv")] + file_types
        elif self.current_file.suffix.lower() == ".xlsx":
            file_types = [("Excel Files", "*.xlsx")] + file_types
            
        dest_path = ctk.filedialog.asksaveasfilename(
            defaultextension=self.current_file.suffix,
            filetypes=file_types,
            initialfile=self.current_file.name
        )
        
        if dest_path:
            try:
                shutil.copy2(self.current_file, dest_path)
                self.show_info("File exported successfully!")
            except Exception as e:
                self.show_error(f"Error exporting file: {str(e)}")
    
    def clear_preview(self):
        """Clear the preview area"""
        self.file_label.configure(text="No file selected")
        self.export_button.configure(state="disabled")
        for item in self.preview_table.get_children():
            self.preview_table.delete(item)
        self.preview_table["columns"] = ()
    
    def show_error(self, message: str):
        """Show error message"""
        tkmb.showerror("Error", message)
    
    def show_info(self, message: str):
        """Show info message"""
        tkmb.showinfo("Information", message)