# app/gui/dashboard.py

import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from typing import Optional, Dict
from datetime import datetime
from .portfolio_windows.alder import AlderPage
from .portfolio_windows.white_rabbit import WhiteRabbitPage
from .settings_windows.settings_page import SettingsPage
from .file_explorer import FileExplorer
from .components.date_selector import DateSelector
from config.system_config import SystemConfig
from managers.file_manager import PortfolioFileManager
from managers.coordinator import PortfolioCoordinator
from .base_window import BasePage
from managers.portfolio import Portfolio
import logging


class Dashboard(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Initialize the coordinator and file manager first
        self._setup_system_components()

        # Basic window setup
        self.title("Excelerate")
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Add menu
        self.setup_menu()  # Add this line

        # Configure grid
        self.grid_rowconfigure(2, weight=1)  # Updated to account for date selector
        self.grid_columnconfigure(0, weight=1)

        # Initialize pages dict
        self.pages: Dict[str, BasePage] = {}
        self.current_page: Optional[BasePage] = None

        # Create main container
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Create navigation frame
        self.setup_navigation()

        # Create date selector
        self.setup_date_selector()

        # Register pages
        self.setup_pages()

        # Show default page
        self.show_page("alder")

        # Setup logger
        self.logger = logging.getLogger(__name__)

    def setup_menu(self):
        """Create application menu system"""
        # Create menu bar
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Export options
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(
            label="Export Alder Portfolio to Desktop",
            command=lambda: self.export_specific_portfolio(Portfolio.ALDER),
        )
        export_menu.add_command(
            label="Export White Rabbit Portfolio to Desktop",
            command=lambda: self.export_specific_portfolio(Portfolio.WHITE_RABBIT),
        )

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

    def export_specific_portfolio(self, portfolio: Portfolio):
        """Export a specific portfolio workbook to desktop"""
        try:
            result = self.file_manager.export_portfolio_workbook(portfolio)
            if result:
                import tkinter.messagebox as tkmb

                tkmb.showinfo("Success", f"Portfolio workbook exported to:\n{result}")
        except Exception as e:
            import tkinter.messagebox as tkmb

            tkmb.showerror("Error", f"Failed to export portfolio: {str(e)}")
            self.geometry("1200x800")
            self.minsize(800, 600)

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
            nav_frame, text="Alder", command=lambda: self.show_page("alder")
        ).pack(side="left", padx=5)

        # White Rabbit button
        ctk.CTkButton(
            nav_frame,
            text="White Rabbit",
            command=lambda: self.show_page("white_rabbit"),
        ).pack(side="left", padx=5)

        # File Explorer button
        ctk.CTkButton(
            nav_frame,
            text="📁 File Explorer",
            command=lambda: self.show_page("file_explorer"),
        ).pack(side="left", padx=5)

        # Settings button (right-aligned)
        ctk.CTkButton(nav_frame, text="⚙️ Settings", command=self.show_settings).pack(
            side="right", padx=5
        )

    def setup_pages(self):
        """Initialize all application pages"""
        self.pages = {
            "alder": AlderPage(self.container, self),
            "white_rabbit": WhiteRabbitPage(self.container, self),
            "file_explorer": FileExplorer(self.container, self),
            "settings": SettingsPage(self.container, self),
        }

        # Configure all pages in grid
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def setup_date_selector(self):
        """Create the date selector frame"""
        self.date_selector = DateSelector(
            self, date_changed_callback=self._on_date_changed
        )
        self.date_selector.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

    def _on_date_changed(self, new_date: datetime):
        """Handle date selection changes"""
        self.selected_date = new_date
        # Log the selected date
        self.logger.info(f"Date changed to: {new_date.strftime('%Y-%m-%d')}")

        # Update any components that depend on the selected date
        if self.current_page:
            # Notify current page of date change if it has a method for it
            if hasattr(self.current_page, "update_for_date") and callable(
                getattr(self.current_page, "update_for_date")
            ):
                self.current_page.update_for_date(new_date)

    def get_selected_date(self) -> datetime:
        """Get the currently selected processing date"""
        return self.date_selector.get_selected_date()

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
        """Show settings page"""
        self.show_page("settings")
        pass

    def export_current_portfolio(self):
        """Export the currently active portfolio workbook to desktop"""
        if not self.current_page or not hasattr(self.current_page, "portfolio"):
            return

        portfolio = self.current_page.portfolio
        if portfolio:
            self.file_manager.export_portfolio_workbook(portfolio)
