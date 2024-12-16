from typing import Dict, Tuple, Optional, Callable
import msal
import json
from pathlib import Path

class MSAuthManager:
    """Enhanced version of your existing authentication manager"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.token_file = config_dir / "ms_token.json"
        self.config_file = config_dir / "ms_config.json"
        
        # Load Microsoft OAuth configuration
        self.config = self._load_config()
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    def _load_config(self) -> Dict:
        """Load Microsoft OAuth configuration."""
        if not self.config_file.exists():
            default_config = {
                "client_id": "YOUR_CLIENT_ID",
                "authority": "https://login.microsoftonline.com/common",
                "scope": ["Files.ReadWrite.All", "User.Read"]
            }
            self.config_file.write_text(json.dumps(default_config, indent=2))
            return default_config
        return json.loads(self.config_file.read_text())

    def initiate_device_flow(self) -> Dict:
        """Start the device flow authentication process."""
        app = msal.PublicClientApplication(
            self.config["client_id"],
            authority=self.config["authority"]
        )
        
        flow = app.initiate_device_flow(scopes=self.config["scope"])
        if "user_code" not in flow:
            raise ValueError("Failed to create device flow")
        
        return flow

    def authenticate(self, flow: Dict, callback: Callable) -> None:
        """Handle the authentication process."""
        app = msal.PublicClientApplication(
            self.config["client_id"],
            authority=self.config["authority"]
        )
        
        # Try to acquire token with device flow
        result = app.acquire_token_by_device_flow(flow)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token")
            self.token_expiry = result.get("expires_in")
            self._save_token(result)
            callback(True, result.get("id_token_claims"), 
                    self.access_token, self.refresh_token, self.token_expiry)
        else:
            callback(False, None, None, None, None)

    def refresh_access_token(self, callback: Callable) -> None:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            callback(False, None, None, None, None)
            return

        app = msal.PublicClientApplication(
            self.config["client_id"],
            authority=self.config["authority"]
        )
        
        result = app.acquire_token_by_refresh_token(
            self.refresh_token,
            scopes=self.config["scope"]
        )
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token")
            self.token_expiry = result.get("expires_in")
            self._save_token(result)
            callback(True, None, self.access_token, 
                    self.refresh_token, self.token_expiry)
        else:
            callback(False, None, None, None, None)

    def _save_token(self, token_data: Dict) -> None:
        """Save token data to file."""
        self.token_file.write_text(json.dumps(token_data, indent=2))

    def load_saved_token(self) -> Optional[Dict]:
        """Load saved token data if available."""
        if self.token_file.exists():
            token_data = json.loads(self.token_file.read_text())
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            self.token_expiry = token_data.get("expires_in")
            return token_data
        return None

    def is_token_expired(self) -> bool:
        """Check if the current token is expired."""
        # Implementation depends on how you want to handle token expiration
        return False  # Placeholder implementation
