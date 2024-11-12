import customtkinter as ctk
from abc import ABC, abstractmethod
from managers.portfolio import Portfolio

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