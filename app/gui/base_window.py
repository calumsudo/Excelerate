# app/gui/base_window.py

import customtkinter as ctk
from abc import abstractmethod
from managers.portfolio import Portfolio
import tkinter.messagebox as tkmb


class BasePage(ctk.CTkFrame):
    """Base class for all pages in the application"""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.portfolio = self.get_portfolio()  # Each page knows its portfolio
        self.setup_ui()

    @abstractmethod
    def setup_ui(self):
        """Setup the UI elements for this page"""
        pass

    @abstractmethod
    def get_portfolio(self) -> Portfolio:
        """Return the Portfolio enum for this page"""
        pass

    def on_enter(self):
        """Called when page is shown"""
        pass

    def on_leave(self):
        """Called when page is hidden"""
        pass
    
    def export_portfolio_to_desktop(self):
        """Export portfolio workbook to desktop"""
        if self.portfolio is None:
            tkmb.showerror("Error", "No portfolio selected")
            return
            
        try:
            # Use file_manager to export the file
            exported_path = self.controller.file_manager.export_portfolio_workbook(self.portfolio)
            
            if exported_path:
                tkmb.showinfo("Success", f"Portfolio workbook exported to:\n{exported_path}")
            else:
                tkmb.showerror("Error", "Failed to export portfolio workbook")
                
        except Exception as e:
            tkmb.showerror("Error", f"Error exporting portfolio: {str(e)}")