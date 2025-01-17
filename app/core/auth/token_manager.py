from pathlib import Path
import json
from datetime import datetime
from typing import Dict


class TokenManager:
    def __init__(self, config_dir: Path):
        self.token_file = config_dir / "ms_token.json"
        self.token_data = self._load_token_data()

    def _load_token_data(self) -> Dict:
        if self.token_file.exists():
            with open(self.token_file, "r") as f:
                return json.load(f)
        return {}

    def save_token(self, token_data: Dict):
        with open(self.token_file, "w") as f:
            json.dump(token_data, f)

    def is_token_valid(self) -> bool:
        if not self.token_data:
            return False
        expiry = datetime.fromisoformat(self.token_data["expires_at"])
        return datetime.now() < expiry
