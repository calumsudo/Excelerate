import customtkinter as ctk
from tkinter import filedialog
from datetime import datetime, timedelta
import os
import json
from tkcalendar import Calendar
from ml_models.funder_classifer import FunderClassifier


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

        # Add a button for CSV upload
        self.upload_button = ctk.CTkButton(self.main_container, text="Upload CSV", command=self.upload_csv, width=200, height=50, font=("Arial", 16))
        self.upload_button.pack(pady=(20, 0))

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
        selected_date = self.calendar.get_date()
        if not self.is_friday(selected_date):
            self.show_date_warning(selected_date)
        else:
            self.selected_date = selected_date

    def get_last_friday(self):
        today = datetime.now()
        if today.weekday() == 4:  # If today is Friday
            return today
        days_since_friday = (today.weekday() - 4) % 7
        last_friday = today - timedelta(days=days_since_friday)
        return last_friday

    def navigate_to_portfolio(self, portfolio):
        if not self.output_dir:
            self.error_label.configure(text="Please select an output directory first.")
            return

        if not self.selected_date:
            last_friday = self.get_last_friday()
            self.selected_date = last_friday.strftime("%Y-%m-%d")
            self.calendar.selection_set(last_friday)
            self.error_label.configure(text="Date automatically set to last Friday.")

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

    def is_friday(self, date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.weekday() == 4

    def get_nearest_friday(self, date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        days_until_friday = (4 - date_obj.weekday()) % 7
        nearest_friday = date_obj + timedelta(days=days_until_friday)
        return nearest_friday.strftime("%Y-%m-%d")

    def show_date_warning(self, selected_date):
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
        day_of_week = date_obj.strftime("%A")
        nearest_friday = self.get_nearest_friday(selected_date)

        warning_window = ctk.CTkToplevel(self.master)
        warning_window.title("Date Selection Warning")
        warning_window.geometry("400x200")

        warning_label = ctk.CTkLabel(warning_window, text="The selected date is not a Friday.", font=("Arial", 16, "bold"))
        warning_label.pack(pady=(20, 10))

        question_label = ctk.CTkLabel(warning_window, text="Did you mean to select:", font=("Arial", 14))
        question_label.pack()

        yes_button = ctk.CTkButton(warning_window, text=f"Yes, I meant to select ({day_of_week}, {selected_date})", 
                                   command=lambda: self.confirm_date_selection(warning_window, selected_date))
        yes_button.pack(pady=(10, 5))

        no_button = ctk.CTkButton(warning_window, text=f"No, I meant to select (Friday, {nearest_friday})", 
                                  command=lambda: self.correct_date_selection(warning_window, nearest_friday))
        no_button.pack(pady=5)

    def confirm_date_selection(self, warning_window, selected_date):
        self.selected_date = selected_date
        warning_window.destroy()

    def correct_date_selection(self, warning_window, nearest_friday):
        self.selected_date = nearest_friday
        self.calendar.selection_set(nearest_friday)
        warning_window.destroy()

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            predicted_funder, confidence = FunderClassifier(file_path)
            self.show_prediction_popup(predicted_funder, confidence, file_path)

    def show_prediction_popup(self, predicted_funder, confidence, file_path):
        popup = ctk.CTkToplevel(self)
        popup.title("Funder Prediction")
        popup.geometry("400x250")

        message = f"The uploaded file:\n{os.path.basename(file_path)}\n\nPredicted Funder: {predicted_funder}\nConfidence: {confidence:.2f}"
        label = ctk.CTkLabel(popup, text=message, font=("Arial", 14))
        label.pack(pady=(20, 30))

        question = ctk.CTkLabel(popup, text="Is this prediction correct?", font=("Arial", 16, "bold"))
        question.pack(pady=(0, 20))

        button_frame = ctk.CTkFrame(popup)
        button_frame.pack()

        confirm_button = ctk.CTkButton(button_frame, text="Yes", command=lambda: self.handle_prediction_response(popup, True, predicted_funder, file_path), width=100)
        confirm_button.pack(side="left", padx=10)

        deny_button = ctk.CTkButton(button_frame, text="No", command=lambda: self.handle_prediction_response(popup, False, predicted_funder, file_path), width=100)
        deny_button.pack(side="left", padx=10)

    def handle_prediction_response(self, popup, is_correct, predicted_funder, file_path):
        popup.destroy()
        if is_correct:
            self.show_success_message(f"Prediction confirmed: {predicted_funder}")
        else:
            self.show_correction_popup(predicted_funder, file_path)

    def show_success_message(self, message):
        success_popup = ctk.CTkToplevel(self)
        success_popup.title("Success")
        success_popup.geometry("300x150")

        label = ctk.CTkLabel(success_popup, text=message, font=("Arial", 14))
        label.pack(pady=20)

        ok_button = ctk.CTkButton(success_popup, text="OK", command=success_popup.destroy, width=100)
        ok_button.pack(pady=10)

    def show_correction_popup(self, predicted_funder, file_path):
        correction_popup = ctk.CTkToplevel(self)
        correction_popup.title("Correction")
        correction_popup.geometry("400x200")

        label = ctk.CTkLabel(correction_popup, text="Please select the correct funder:", font=("Arial", 14))
        label.pack(pady=(20, 10))

        funder_var = ctk.StringVar(value=predicted_funder)
        funder_dropdown = ctk.CTkOptionMenu(correction_popup, variable=funder_var, values=["ACS", "BHB", "Boom", "Kings", "Vesper", "Clear View", "Other"])
        funder_dropdown.pack(pady=10)

        submit_button = ctk.CTkButton(correction_popup, text="Submit", command=lambda: self.submit_correction(correction_popup, funder_var.get(), file_path), width=100)
        submit_button.pack(pady=10)

    def submit_correction(self, popup, corrected_funder, file_path):
        popup.destroy()
        # Here you can add logic to update your training data or log the correction
        self.show_success_message(f"Correction submitted: {corrected_funder}")

    # Add any additional methods you need for logging, error handling, etc.
