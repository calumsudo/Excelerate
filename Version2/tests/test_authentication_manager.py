import pytest
from unittest.mock import patch, MagicMock
from services.authentication_manager import AuthenticationManager

@pytest.fixture
def auth_manager():
    """Fixture for creating an instance of the AuthenticationManager."""
    return AuthenticationManager()

def test_initiate_device_flow(mocker, auth_manager):
    """Test initiating the device flow."""
    # Mock msal.PublicClientApplication.initiate_device_flow
    mock_initiate_device_flow = mocker.patch('msal.PublicClientApplication.initiate_device_flow')
    mock_initiate_device_flow.return_value = {
        "user_code": "12345",
        "verification_uri": "https://microsoft.com/device"
    }
    
    flow = auth_manager.initiate_device_flow()
    
    assert flow["user_code"] == "12345"
    assert flow["verification_uri"] == "https://microsoft.com/device"

def test_authenticate_success(mocker, auth_manager):
    """Test successful authentication."""
    # Mock msal.PublicClientApplication.acquire_token_by_device_flow
    mock_acquire_token = mocker.patch('msal.PublicClientApplication.acquire_token_by_device_flow')
    mock_acquire_token.return_value = {
        "access_token": "fake_access_token",
        "refresh_token": "fake_refresh_token",
        "expires_in": 3600
    }

    mock_requests = mocker.patch('requests.get')
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = {"displayName": "Calum Siemer"}

    # Mock callback
    callback = MagicMock()

    # Mock the threading so that the callback is called synchronously
    mocker.patch('threading.Thread.start', lambda x: x.run())

    flow = {"user_code": "12345"}
    auth_manager.authenticate(flow, callback)

    callback.assert_called_with(True, {"displayName": "Calum Siemer"}, "fake_access_token")


    assert auth_manager.access_token == "fake_access_token"
    assert auth_manager.refresh_token == "fake_refresh_token"
    assert auth_manager.token_expiry > 0

def test_authenticate_failure(mocker, auth_manager):
    """Test authentication failure."""
    # Mock msal.PublicClientApplication.acquire_token_by_device_flow
    mock_acquire_token = mocker.patch('msal.PublicClientApplication.acquire_token_by_device_flow')
    mock_acquire_token.return_value = {}

    # Mock callback
    callback = MagicMock()

    flow = {"user_code": "12345"}
    auth_manager.authenticate(flow, callback)

    callback.assert_called_with(False, None, None)

def test_refresh_token_success(mocker, auth_manager):
    """Test successful token refresh."""
    # Mock msal.PublicClientApplication.acquire_token_by_refresh_token
    mock_refresh_token = mocker.patch('msal.PublicClientApplication.acquire_token_by_refresh_token')
    mock_refresh_token.return_value = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 3600
    }

    callback = MagicMock()
    auth_manager.refresh_token = "old_refresh_token"

    auth_manager.refresh_access_token(callback)

    callback.assert_called_with(True, None, "new_access_token", "new_refresh_token", mocker.ANY)

def test_refresh_token_failure(mocker, auth_manager):
    """Test failure to refresh token."""
    # Mock msal.PublicClientApplication.acquire_token_by_refresh_token
    mock_refresh_token = mocker.patch('msal.PublicClientApplication.acquire_token_by_refresh_token')
    mock_refresh_token.return_value = {}

    callback = MagicMock()
    auth_manager.refresh_token = "old_refresh_token"

    auth_manager.refresh_access_token(callback)

    callback.assert_called_with(False, None, None, None, None)

def test_is_token_expired(auth_manager):
    """Test token expiration logic."""
    auth_manager.token_expiry = 1  # Expired token (time in the past)
    assert auth_manager.is_token_expired() == True

    auth_manager.token_expiry = 9999999999  # Valid token (time in the future)
    assert auth_manager.is_token_expired() == False
