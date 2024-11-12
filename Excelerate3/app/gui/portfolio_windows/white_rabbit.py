from ..base_window import BasePage
from ..components.drag_drop import DropZone
from managers.portfolio import Portfolio
import customtkinter as ctk

class WhiteRabbitPage(BasePage):
    def get_portfolio(self) -> Portfolio:
        return Portfolio.WHITE_RABBIT
    
    def setup_ui(self):
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(
            header,
            text="White Rabbit Portfolio",
            font=("Helvetica", 24, "bold")
        ).pack(side="left", padx=10)
        
        # Main content area
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        
        # Add drop zone - note the keyword arguments
        self.drop_zone = DropZone(
            parent=content,
            controller=self.controller,
            page=self
        )
        self.drop_zone.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)