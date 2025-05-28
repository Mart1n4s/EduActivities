import pytest
from unittest.mock import Mock
from models.user import RegisterData
from views.auth import get_password_hash
from utils.validators import validate_user_data

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.create_user.return_value = "mock_user_id"
    mock.get_user.return_value = {
        "username": "testuser",
        "name": "Test",
        "surname": "User",
        "email": "test@example.com",
        "telephone_number": "1234567890",
        "role": "viewer",
        "hashed_password": "hashed_password"
    }
    return mock

def test_register_user_success(mock_db):
    user_data = RegisterData(
        username="testuser",
        name="Test",
        surname="User",
        email="test@example.com",
        telephone_number="1234567890",
        password="password123",
        confirm_password="password123",
        role="viewer"
    )
    
    validation_error = validate_user_data(
        user_data.username,
        user_data.name,
        user_data.surname,
        user_data.email,
        user_data.telephone_number,
        user_data.password,
        user_data.role,
        is_update=False,
        confirm_password=user_data.confirm_password
    )
    assert validation_error is None
    
    user_dict = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role,
        "hashed_password": get_password_hash(user_data.password)
    }
    
    user_id = mock_db.create_user(user_dict)
    assert user_id == "mock_user_id"
    mock_db.create_user.assert_called_once_with(user_dict)
    
    created_user = mock_db.get_user(user_id)
    assert created_user is not None
    assert created_user["username"] == user_data.username
    assert created_user["name"] == user_data.name
    assert created_user["surname"] == user_data.surname
    assert created_user["email"] == user_data.email
    assert created_user["telephone_number"] == user_data.telephone_number
    assert created_user["role"] == user_data.role

def test_register_user_invalid_email():
    user_data = RegisterData(
        username="testuser",
        name="Test",
        surname="User",
        email="invalid-email",
        telephone_number="1234567890",
        password="password123",
        confirm_password="password123",
        role="viewer"
    )
    
    error_response = validate_user_data(
        user_data.username,
        user_data.name,
        user_data.surname,
        user_data.email,
        user_data.telephone_number,
        user_data.password,
        user_data.role,
        is_update=False,
        confirm_password=user_data.confirm_password
    )
    assert error_response is not None
    assert error_response.status_code == 400
    assert "Invalid email format" in error_response.body.decode()

def test_register_user_invalid_phone():
    user_data = RegisterData(
        username="testuser",
        name="Test",
        surname="User",
        email="test@example.com",
        telephone_number="invalid-phone",
        password="password123",
        confirm_password="password123",
        role="viewer"
    )
    
    error_response = validate_user_data(
        user_data.username,
        user_data.name,
        user_data.surname,
        user_data.email,
        user_data.telephone_number,
        user_data.password,
        user_data.role,
        is_update=False,
        confirm_password=user_data.confirm_password
    )
    assert error_response is not None
    assert error_response.status_code == 400
    assert "Invalid phone number format" in error_response.body.decode()

def test_register_user_short_password():
    user_data = RegisterData(
        username="testuser",
        name="Test",
        surname="User",
        email="test@example.com",
        telephone_number="1234567890",
        password="12345",
        confirm_password="12345",
        role="viewer"
    )
    
    error_response = validate_user_data(
        user_data.username,
        user_data.name,
        user_data.surname,
        user_data.email,
        user_data.telephone_number,
        user_data.password,
        user_data.role,
        is_update=False,
        confirm_password=user_data.confirm_password
    )
    assert error_response is not None
    assert error_response.status_code == 400
    assert "Password must be at least 6 characters long" in error_response.body.decode()

def test_register_user_empty_fields():
    user_data = RegisterData(
        username="",
        name="Test",
        surname="User",
        email="test@example.com",
        telephone_number="1234567890",
        password="password123",
        confirm_password="password123",
        role="viewer"
    )
    
    error_response = validate_user_data(
        user_data.username,
        user_data.name,
        user_data.surname,
        user_data.email,
        user_data.telephone_number,
        user_data.password,
        user_data.role,
        is_update=False,
        confirm_password=user_data.confirm_password
    )
    assert error_response is not None
    assert error_response.status_code == 400
    assert "No fields can be empty" in error_response.body.decode()

def test_register_user_password_mismatch():
    user_data = RegisterData(
        username="testuser",
        name="Test",
        surname="User",
        email="test@example.com",
        telephone_number="1234567890",
        password="password123",
        confirm_password="different_password",
        role="viewer"
    )
    
    error_response = validate_user_data(
        user_data.username,
        user_data.name,
        user_data.surname,
        user_data.email,
        user_data.telephone_number,
        user_data.password,
        user_data.role,
        is_update=False,
        confirm_password=user_data.confirm_password
    )
    assert error_response is not None
    assert error_response.status_code == 400
    assert "Passwords do not match" in error_response.body.decode()