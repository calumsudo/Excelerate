# app/gui/portfolio_windows/white_rabbit.py

from ..base_window import BasePage
from ..components.drag_drop import DropZone
from ..components.file_upload_section import FileUploadSection
from managers.portfolio import Portfolio, PortfolioStructure
import customtkinter as ctk
import tkinter.messagebox as tkmb
from pathlib import Path

class WhiteRabbitPage(BasePage):
    def get_portfolio(self) -> Portfolio:
        return Portfolio.WHITE_RABBIT
    
    def setup_ui(self):
        # Configure grid for full height/width usage
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(
            header,
            text=f"{self.portfolio.value} Portfolio",
            font=("Helvetica", 24, "bold")
        ).pack(side="left", padx=10)
        
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=1, column=0, sticky="ns", padx=(10, 5), pady=5)
        
        # Workbook Directory Section
        ctk.CTkLabel(
            sidebar,
            text="Workbook Directory",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # Show current workbook if exists
        current_workbook = self.controller.file_manager.get_portfolio_workbook_path(self.portfolio)
        self.workbook_label = ctk.CTkLabel(
            sidebar,
            text=current_workbook.name if current_workbook else "No workbook selected",
            wraplength=160
        )
        self.workbook_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        
        # Upload button
        ctk.CTkButton(
            sidebar,
            text="Select Workbook",
            command=self.select_workbook
        ).grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Funder Classifier Section
        ctk.CTkLabel(
            sidebar,
            text="Funder Classifier",
            font=("Helvetica", 16, "bold")
        ).grid(row=3, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Radio buttons
        self.classifier_var = ctk.StringVar(value="automatic")
        ctk.CTkRadioButton(
            sidebar,
            text="Automatic",
            variable=self.classifier_var,
            value="automatic",
            command=self.update_content
        ).grid(row=4, column=0, padx=40, pady=5, sticky="w")
        
        ctk.CTkRadioButton(
            sidebar,
            text="Manual",
            variable=self.classifier_var,
            value="manual",
            command=self.update_content
        ).grid(row=5, column=0, padx=40, pady=5, sticky="w")
        
        # Main content area - make it expand fully
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Initialize content
        self.setup_auto_content()
        self.setup_manual_content()
        self.update_content()

    def select_workbook(self):
        """Handle workbook selection and saving"""
        filetypes = [('Excel files', '*.xlsx')]
        file_path = ctk.filedialog.askopenfilename(filetypes=filetypes)
        
        if file_path:
            try:
                # Save workbook to system directory
                self.controller.file_manager.save_portfolio_workbook(
                    self.portfolio,
                    Path(file_path)
                )
                
                # Update label with new workbook name
                self.workbook_label.configure(text=Path(file_path).name)
                
            except Exception as e:
                tkmb.showerror(
                    title="Error",
                    message=f"Failed to save workbook: {str(e)}"
                )
        
    def setup_auto_content(self):
        self.auto_content = DropZone(
            parent=self.content,
            controller=self.controller,
            page=self
        )
            
    def setup_manual_content(self):
        self.manual_content = ctk.CTkFrame(self.content)
        self.manual_content.grid_columnconfigure((0, 1), weight=1)
        
        funders = PortfolioStructure.get_portfolio_funders(self.get_portfolio())
        
        # Divide funders into two columns
        left_funders = funders[:(len(funders) + 1) // 2]
        right_funders = funders[(len(funders) + 1) // 2:]
        
        # Left column
        left_frame = ctk.CTkFrame(self.manual_content)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        left_frame.grid_rowconfigure([i for i in range(len(left_funders))], weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Right column
        right_frame = ctk.CTkFrame(self.manual_content)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.grid_rowconfigure([i for i in range(len(right_funders))], weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Place upload sections
        for i, funder in enumerate(left_funders):
            upload_section = FileUploadSection(
                left_frame,
                funder=funder,
                multi_file=(funder == "ClearView"),
                controller=self.controller,
                portfolio=self.get_portfolio()
            )
            upload_section.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            
        for i, funder in enumerate(right_funders):
            upload_section = FileUploadSection(
                right_frame,
                funder=funder,
                multi_file=(funder == "ClearView"),
                controller=self.controller,
                portfolio=self.get_portfolio()
            )
            upload_section.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            
    def update_content(self):
        # Clear current content
        for widget in self.content.winfo_children():
            widget.grid_remove()
            
        # Show selected content
        if self.classifier_var.get() == "automatic":
            self.auto_content.grid(row=0, column=0, sticky="nsew")
        else:
            self.manual_content.grid(row=0, column=0, sticky="nsew")