import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from typing import Optional, Dict, Type
from pathlib import Path
from .portfolio_windows.alder import AlderPage
from .portfolio_windows.white_rabbit import WhiteRabbitPage
from .components.drag_drop import DropZone
from config.system_config import SystemConfig
from managers.file_manager import PortfolioFileManager
from managers.coordinator import PortfolioCoordinator

class Dashboard(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize the coordinator and file manager first
        self._setup_system_components()
        
        # Basic window setup
        self.title("Excelerate")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize pages dict
        self.pages: Dict[str, BasePage] = {}
        self.current_page: Optional[BasePage] = None
        
        # Create main container
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Create navigation frame
        self.setup_navigation()
        
        # Register pages
        self.setup_pages()
        
        # Show default page
        self.show_page("alder")

    def _setup_system_components(self):
        """Initialize file management and coordination systems"""
        # Get application directory
        self.config_dir = SystemConfig.get_app_directory()
        
        # Initialize file manager
        self.file_manager = PortfolioFileManager(self.config_dir)
        
        # Initialize coordinator
        self.coordinator = PortfolioCoordinator(self.file_manager)
        
        # Set theme based on saved preferences
        ctk.set_appearance_mode(self.file_manager.preferences.theme_mode)
        
    def setup_navigation(self):
        """Create the navigation bar"""
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Portfolio selection
        ctk.CTkLabel(nav_frame, text="Portfolio:").pack(side="left", padx=5)
        
        # Alder button
        ctk.CTkButton(
            nav_frame,
            text="Alder",
            command=lambda: self.show_page("alder")
        ).pack(side="left", padx=5)
        
        # White Rabbit button
        ctk.CTkButton(
            nav_frame,
            text="White Rabbit",
            command=lambda: self.show_page("white_rabbit")
        ).pack(side="left", padx=5)
        
        # Settings button (right-aligned)
        ctk.CTkButton(
            nav_frame,
            text="⚙️ Settings",
            command=self.show_settings
        ).pack(side="right", padx=5)
        
    def setup_pages(self):
        """Initialize all application pages"""
        self.pages = {
            "alder": AlderPage(self.container, self),
            "white_rabbit": WhiteRabbitPage(self.container, self)
        }
        
        # Configure all pages in grid
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
            
    def show_page(self, page_name: str):
        """Switch to specified page"""
        if page_name not in self.pages:
            raise ValueError(f"Unknown page: {page_name}")
            
        # Call on_leave for current page
        if self.current_page:
            self.current_page.on_leave()
            
        # Hide all pages
        for page in self.pages.values():
            page.grid_remove()
            
        # Show and update selected page
        self.pages[page_name].grid()
        self.pages[page_name].on_enter()
        self.current_page = self.pages[page_name]
        
    def show_settings(self):
        """Show settings dialog"""
        # Implement settings dialog
        pass