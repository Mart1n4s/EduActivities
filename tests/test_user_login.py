import pytest
from unittest.mock import Mock
from models.user import LoginData
from views.auth import verify_password, get_password_hash

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.get_user_by_username.return_value = {
        "username": "testuser",
        "name": "Test",
        "surname": "User",
        "email": "test@example.com",
        "telephone_number": "1234567890",
        "role": "viewer",
        "hashed_password": get_password_hash("password123")
    }
    return mock

def test_login_success(mock_db):
    login_data = LoginData(
        username="testuser",
        password="password123"
    )
    
    user = mock_db.get_user_by_username(login_data.username)
    assert user is not None
    assert user["username"] == login_data.username
    assert verify_password(login_data.password, user["hashed_password"]) is True

def test_login_wrong_password(mock_db):
    login_data = LoginData(
        username="testuser",
        password="wrongpassword"
    )
    
    user = mock_db.get_user_by_username(login_data.username)
    assert user is not None
    assert user["username"] == login_data.username
    assert verify_password(login_data.password, user["hashed_password"]) is False

def test_login_nonexistent_user(mock_db):
    login_data = LoginData(
        username="nonexistent",
        password="password123"
    )
    
    mock_db.get_user_by_username.return_value = None
    user = mock_db.get_user_by_username(login_data.username)
    assert user is None 