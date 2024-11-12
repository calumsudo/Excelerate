import platform
import os
from pathlib import Path
from typing import Dict

class SystemConfig:
    @staticmethod
    def get_system_info() -> Dict:
        return {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine()
        }

    @staticmethod
    def get_app_directory() -> Path:
        system = platform.system()
        home = Path.home()

        if system == "Windows":
            app_dir = Path(os.getenv('APPDATA')) / "Excelerate"
        elif system == "Darwin":  # macOS
            app_dir = home / "Library/Application Support/Excelerate"
        else:  # Linux
            app_dir = home / ".excelerate"

        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
