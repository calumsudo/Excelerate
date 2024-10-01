import pytest
from unittest.mock import MagicMock
from ui.authenticate_ui import AuthenticateUI
from services.authentication_manager import AuthenticationManager
import customtkinter as ctk

@pytest.fixture
def mock_auth_manager(mocker):
    """Mock the AuthenticationManager."""
    return mocker.patch('services.authentication_manager.AuthenticationManager')

def test_authenticate_ui_initialization(mocker):
    """Test that the AuthenticateUI initializes correctly."""
    mock_callback = MagicMock()

    # Mock the AuthenticationManager
    mock_auth_manager = mocker.patch('services.authentication_manager.AuthenticationManager')

    # Mock the customtkinter CTk mainloop to avoid blocking behavior
    mock_mainloop = mocker.patch('customtkinter.CTk.mainloop')

    # Create instance of AuthenticateUI
    root = mocker.MagicMock()  # Mock Tkinter root window
    auth_ui = AuthenticateUI(root, mock_callback)

    assert auth_ui is not None
    assert auth_ui.auth_status_label.cget("text") == ""  # Label should be empty initially

    # Ensure that mainloop was not started during the test
    mock_mainloop.assert_not_called()


def test_authenticate_ui_successful_authentication(mocker):
    """Test successful authentication through the UI."""
    mock_callback = MagicMock()

    # Mock the AuthenticationManager and its methods
    mock_auth_manager = mocker.patch('services.authentication_manager.AuthenticationManager')
    mock_auth_manager.return_value.initiate_device_flow.return_value = {"user_code": "12345"}
    mock_auth_manager.return_value.authenticate.return_value = None

    # Mock the customtkinter CTk mainloop to avoid blocking behavior
    mock_mainloop = mocker.patch('customtkinter.CTk.mainloop')

    # Create instance of AuthenticateUI
    root = mocker.MagicMock()
    auth_ui = AuthenticateUI(root, mock_callback)

    # Trigger authentication
    auth_ui.authenticate()

    assert auth_ui.label.cget("text") == "User code: 12345"
    mock_callback.assert_not_called()  # callback should not be called until device flow completes

    # Ensure that mainloop was not started during the test
    mock_mainloop.assert_not_called()
