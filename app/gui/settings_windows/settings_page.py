# app/gui/settings_windows/settings_page.py

from ..base_window import BasePage
from managers.portfolio import Portfolio
import customtkinter as ctk


class SettingsPage(BasePage):
    def get_portfolio(self) -> Portfolio:
        return None

    def setup_ui(self):
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(header, text="Settings", font=("Helvetica", 24, "bold")).pack(
            side="left", padx=10
        )

        # Sidebar - remove width parameter and add grid configuration
        sidebar = ctk.CTkFrame(self)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        sidebar.grid_columnconfigure(0, weight=1)

        # Content area
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.content.grid_columnconfigure(0, weight=1)

        self.setup_sidebar(sidebar)
        self.setup_panels()
        self.show_panel("appearance")

    def setup_sidebar(self, sidebar):
        button_style = {
            "anchor": "w",
            "height": 40,
            "corner_radius": 0,
            "fg_color": "transparent",
            "text_color": ("gray10", "gray90"),
            "hover_color": ("gray75", "gray28"),
        }

        buttons = [
            ("appearance", "Appearance"),
            ("storage", "Storage"),
            ("auth", "Authentication"),
            ("about", "About"),
        ]

        self.sidebar_buttons = {}
        for i, (panel_id, text) in enumerate(buttons):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=lambda p=panel_id: self.show_panel(p),
                **button_style,
            )
            btn.grid(row=i, column=0, sticky="nsew")
            self.sidebar_buttons[panel_id] = btn

    def setup_panels(self):
        self.panels = {
            "appearance": self.create_appearance_panel(),
            "storage": self.create_storage_panel(),
            "auth": self.create_auth_panel(),
            "about": self.create_about_panel(),
        }

    def create_appearance_panel(self):
        panel = ctk.CTkFrame(self.content)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Theme Mode", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )

        self.theme_var = ctk.StringVar(
            value=self.controller.file_manager.preferences.theme_mode
        )

        themes = ["System", "Light", "Dark"]
        for i, theme in enumerate(themes):
            ctk.CTkRadioButton(
                panel,
                text=theme,
                variable=self.theme_var,
                value=theme,
                command=self.apply_theme,
            ).grid(row=i + 1, column=0, padx=40, pady=5, sticky="w")

        return panel

    def create_storage_panel(self):
        panel = ctk.CTkFrame(self.content)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Storage Location", font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        storage_path = ctk.CTkEntry(panel, width=300)
        storage_path.insert(0, str(self.controller.file_manager.base_dir))
        storage_path.configure(state="readonly")
        storage_path.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(panel, text="Recent Files", font=("Helvetica", 16, "bold")).grid(
            row=2, column=0, padx=20, pady=(20, 10), sticky="w"
        )

        ctk.CTkButton(
            panel, text="Clear Recent Files", command=self.clear_recent_files
        ).grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")

        return panel

    def create_auth_panel(self):
        panel = ctk.CTkFrame(self.content)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Authentication Token", font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.auth_token = ctk.CTkEntry(panel, width=300, show="•")
        if self.controller.file_manager.preferences.auth_token:
            self.auth_token.insert(
                0, self.controller.file_manager.preferences.auth_token
            )
        self.auth_token.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkButton(panel, text="Save Token", command=self.save_auth_token).grid(
            row=2, column=0, padx=20, pady=(0, 20), sticky="w"
        )

        return panel

    def create_about_panel(self):
        panel = ctk.CTkFrame(self.content)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Excelerate", font=("Helvetica", 24, "bold")).grid(
            row=0, column=0, padx=20, pady=(20, 5)
        )

        ctk.CTkLabel(panel, text="Version 1.0.0").grid(
            row=1, column=0, padx=20, pady=(0, 20)
        )

        ctk.CTkLabel(
            panel,
            text="A portfolio management and analysis tool\nfor processing syndicate data.",
            justify="center",
        ).grid(row=2, column=0, padx=20, pady=(0, 20))

        return panel

    def show_panel(self, panel_name: str):
        for panel in self.panels.values():
            panel.grid_remove()

        self.panels[panel_name].grid(row=0, column=0, sticky="nsew")

        for name, button in self.sidebar_buttons.items():
            button.configure(
                fg_color="transparent" if name != panel_name else ("gray75", "gray28")
            )

    def apply_theme(self):
        new_theme = self.theme_var.get()
        ctk.set_appearance_mode(new_theme)
        self.controller.file_manager.preferences.theme_mode = new_theme
        self.controller.file_manager.save_preferences()

    def clear_recent_files(self):
        self.controller.file_manager.clear_recent_files()
        self.show_temp_message("storage", "Recent files cleared!")

    def save_auth_token(self):
        token = self.auth_token.get()
        self.controller.file_manager.preferences.auth_token = token
        self.controller.file_manager.save_preferences()
        self.show_temp_message("auth", "Token saved!")

    def show_temp_message(self, panel_name: str, message: str):
        label = ctk.CTkLabel(self.panels[panel_name], text=message, text_color="green")
        label.grid(row=10, column=0, padx=20, pady=(0, 20))
        self.after(2000, label.destroy)
