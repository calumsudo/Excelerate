import customtkinter as ctk

class DashboardUI(ctk.CTkFrame):
    def __init__(self, master, user_name, data):
        super().__init__(master)
        self.user_name = user_name
        self.data = data

        # Welcome Label
        self.welcome_label = ctk.CTkLabel(self, text=f"Welcome, {self.user_name}", font=("Arial", 18))
        self.welcome_label.pack(pady=10)

        # Data Display (just a placeholder for now)
        self.data_label = ctk.CTkLabel(self, text="Your Data will be displayed here.", font=("Arial", 14))
        self.data_label.pack(pady=10)

        # Action Buttons
        self.refresh_button = ctk.CTkButton(self, text="Refresh Data", command=self.refresh_data)
        self.refresh_button.pack(pady=10)

        self.generate_report_button = ctk.CTkButton(self, text="Generate Report", command=self.generate_report)
        self.generate_report_button.pack(pady=10)

    def refresh_data(self):
        # Placeholder function for refreshing data
        print("Refreshing data...")

    def generate_report(self):
        # Placeholder function for generating a report
        print("Generating report...")
