import customtkinter as ctk
from tkinter import filedialog
from datetime import datetime
import os
import json
from tkcalendar import Calendar

class DashboardUI(ctk.CTkFrame):
    def __init__(self, master, user_name, navigate_callback, save_output_dir_callback):
        super().__init__(master)
        self.user_name = user_name
        self.navigate_callback = navigate_callback
        self.save_output_dir_callback = save_output_dir_callback
        self.output_dir = ""
        self.selected_date = None

        self.setup_ui()

    def setup_ui(self):
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(expand=True, fill="both", padx=50, pady=50)

        # Welcome label
        self.welcome_label = ctk.CTkLabel(self.main_container, text=f"Welcome, {self.user_name}", font=("Arial", 24, "bold"))
        self.welcome_label.pack(pady=(0, 30))

        # Output directory selection
        self.output_dir_frame = ctk.CTkFrame(self.main_container)
        self.output_dir_frame.pack(pady=(0, 30), anchor="center")

        self.output_dir_label = ctk.CTkLabel(self.output_dir_frame, text="Output Directory:", font=("Arial", 16))
        self.output_dir_label.pack(side="left", padx=(0, 10))

        self.output_dir_entry = ctk.CTkEntry(self.output_dir_frame, width=400, height=40, font=("Arial", 14))
        self.output_dir_entry.pack(side="left", padx=(0, 10))
        
        # Load the saved output directory if it exists
        saved_dir = self.load_output_directory()
        if saved_dir:
            self.output_dir = saved_dir
            self.output_dir_entry.insert(0, saved_dir)

        self.output_dir_button = ctk.CTkButton(self.output_dir_frame, text="Browse", command=self.select_output_directory, width=100, height=40, font=("Arial", 14))
        self.output_dir_button.pack(side="left")

        # Date selection
        self.date_frame = ctk.CTkFrame(self.main_container)
        self.date_frame.pack(pady=(0, 30), anchor="center")
        
        self.date_label = ctk.CTkLabel(self.date_frame, text="Select Friday Date:", font=("Arial", 18, "bold"))
        self.date_label.pack(pady=(0, 10))

        self.calendar = Calendar(self.date_frame, selectmode="day", date_pattern="y-mm-dd", font=("Arial", 14), selectforeground="white", selectbackground="#3a7ebf")
        self.calendar.pack()
        self.calendar.bind("<<CalendarSelected>>", self.on_date_select)

        # Portfolio selection buttons
        self.portfolio_label = ctk.CTkLabel(self.main_container, text="Select Portfolio:", font=("Arial", 18, "bold"))
        self.portfolio_label.pack(pady=(0, 10))

        self.button_frame = ctk.CTkFrame(self.main_container)
        self.button_frame.pack(pady=(0, 20))

        self.alder_button = ctk.CTkButton(self.button_frame, text="Alder", command=lambda: self.navigate_to_portfolio("Alder"), width=200, height=50, font=("Arial", 16))
        self.alder_button.pack(side="left", padx=10)

        self.white_rabbit_button = ctk.CTkButton(self.button_frame, text="White Rabbit", command=lambda: self.navigate_to_portfolio("White Rabbit"), width=200, height=50, font=("Arial", 16))
        self.white_rabbit_button.pack(side="left", padx=10)

        # Error label
        self.error_label = ctk.CTkLabel(self.main_container, text="", text_color="red", font=("Arial", 14))
        self.error_label.pack(pady=10)

    def select_output_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir = directory
            self.output_dir_entry.delete(0, "end")
            self.output_dir_entry.insert(0, directory)
            self.save_output_dir_callback(directory)  # Save the selected directory

    def load_output_directory(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                return config.get('output_directory', '')
        except FileNotFoundError:
            return ''

    def on_date_select(self, event):
        self.selected_date = self.calendar.get_date()

    def navigate_to_portfolio(self, portfolio):
        if not self.output_dir:
            self.error_label.configure(text="Please select an output directory first.")
            return

        if not self.selected_date:
            self.error_label.configure(text="Please select a date.")
            return

        # Convert the selected date to the required format
        date_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%m-%d-%y")

        # Create the date subdirectory
        date_dir = os.path.join(self.output_dir, formatted_date)
        os.makedirs(date_dir, exist_ok=True)

        # Create Alder and White Rabbit subdirectories
        alder_dir = os.path.join(date_dir, "Alder")
        white_rabbit_dir = os.path.join(date_dir, "White Rabbit")
        os.makedirs(alder_dir, exist_ok=True)
        os.makedirs(white_rabbit_dir, exist_ok=True)

        # Determine which subdirectory to use based on the selected portfolio
        if portfolio == "Alder":
            portfolio_dir = alder_dir
        else:  # White Rabbit
            portfolio_dir = white_rabbit_dir

        # Call the navigate callback with the portfolio-specific directory
        self.navigate_callback(portfolio, portfolio_dir, self.selected_date)

    # Add any additional methods you need for logging, error handling, etc.