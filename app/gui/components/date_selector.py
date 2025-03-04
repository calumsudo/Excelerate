# app/gui/components/date_selector.py

import customtkinter as ctk
from datetime import datetime
from typing import Callable, Optional
from utils.date_utils import (
    get_available_fridays,
    format_date_for_display,
)


class DateSelector(ctk.CTkFrame):
    def __init__(
        self, parent, date_changed_callback: Optional[Callable[[datetime], None]] = None
    ):
        super().__init__(parent)
        self.date_changed_callback = date_changed_callback

        # Get available dates
        self.available_dates = get_available_fridays(4)
        self.formatted_dates = [
            format_date_for_display(d) for d in self.available_dates
        ]

        # Default to most recent Friday
        self.current_date = self.available_dates[0]

        self.setup_ui()

    def setup_ui(self):
        # Label
        self.label = ctk.CTkLabel(
            self, text="Select Processing Date (Fridays Only):", font=("Arial", 12)
        )
        self.label.pack(side="left", padx=5)

        # Combobox for date selection
        self.date_var = ctk.StringVar(value=self.formatted_dates[0])
        self.date_dropdown = ctk.CTkComboBox(
            self,
            values=self.formatted_dates,
            variable=self.date_var,
            command=self._on_date_changed,
            width=200,
        )
        self.date_dropdown.pack(side="left", padx=5)

    def _on_date_changed(self, _):
        """Handle date selection change"""
        selected_index = self.formatted_dates.index(self.date_var.get())
        self.current_date = self.available_dates[selected_index]

        if self.date_changed_callback:
            self.date_changed_callback(self.current_date)

    def get_selected_date(self) -> datetime:
        """Get the currently selected date"""
        return self.current_date
