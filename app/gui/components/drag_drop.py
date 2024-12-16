# app/gui/components/drag_drop.py

import customtkinter as ctk
from typing import Optional
from pathlib import Path
from ..base_window import BasePage

class DropZone(ctk.CTkFrame):
    def __init__(self, parent: Optional[ctk.CTkFrame] = None, *, controller, page):
        super().__init__(parent if parent is not None else controller)
        
        self.controller = controller
        self.page = page
        self.configure(fg_color="transparent")
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create inner frame for drop zone
        self.drop_frame = ctk.CTkFrame(self)
        self.drop_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Center content in drop frame
        self.drop_frame.grid_rowconfigure(1, weight=1)
        self.drop_frame.grid_columnconfigure(0, weight=1)
        
        # Add drag-drop instructions
        ctk.CTkLabel(
            self.drop_frame,
            text=f"Drop {self.page.portfolio.value} Files Here",
            font=("Helvetica", 20)
        ).grid(row=0, column=0, pady=20)
        
        # Add file list
        self.file_list = ctk.CTkTextbox(self.drop_frame, height=200)
        self.file_list.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Add clear button
        ctk.CTkButton(
            self.drop_frame,
            text="Clear List",
            command=self.clear_list
        ).grid(row=2, column=0, pady=(0, 20))
        
        # Register drop zone
        self.drop_target_register('*')
        self.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Make inner frame a drop target too
        self.drop_frame.drop_target_register('*')
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

    def clean_file_path(self, file_path: str) -> str:
        """Clean the file path string from drag and drop event"""
        # Remove curly braces and any extra whitespace
        cleaned = file_path.strip('{}').strip()
        return cleaned
    
    def handle_drop(self, event):
        """Handle file drop event"""
        # Clean the file path
        raw_path = event.data
        file_path = self.clean_file_path(raw_path)
        
        # Update file list with original path
        self.file_list.insert('end', f"Processing: {file_path}\n")
        
        try:
            # Process the file using the cleaned path
            success, results, error = self.controller.coordinator.process_uploaded_file(
                Path(file_path),
                portfolio=self.page.portfolio
            )
            
            if success:
                self.file_list.insert('end', 
                    f"✓ Success: {results['funder']}\n"
                    f"  Gross Total: ${results['totals']['gross']:,.2f}\n"
                    f"  Net Total: ${results['totals']['net']:,.2f}\n\n"
                )
            else:
                self.file_list.insert('end', f"✗ Error: {error}\n\n")
                
        except Exception as e:
            self.file_list.insert('end', f"✗ Error: {str(e)}\n\n")
            
        # Scroll to bottom
        self.file_list.see('end')
        
    def clear_list(self):
        """Clear the file list"""
        self.file_list.delete('1.0', 'end')