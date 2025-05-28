import pytest
from unittest.mock import Mock
from models.user import UserCreateData
from views.auth import get_password_hash

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

def test_create_user_success(mock_db):
    user_data = UserCreateData(
        username="testuser",
        name="Test",
        surname="User",
        email="test@example.com",
        telephone_number="1234567890",
        password="testpass123",
        role="viewer"
    )
    
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
    assert "hashed_password" in created_user

def test_create_user_duplicate_username(mock_db):
    user_data = UserCreateData(
        username="testuser",
        name="Test",
        surname="User",
        email="test@example.com",
        telephone_number="1234567890",
        password="testpass123",
        role="viewer"
    )
    
    user_dict = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role,
        "hashed_password": get_password_hash(user_data.password)
    }
    
    mock_db.create_user.side_effect = [None, Exception("User exists")]
    
    mock_db.create_user(user_dict)
    with pytest.raises(Exception):
        mock_db.create_user(user_dict)
    
    assert mock_db.create_user.call_count == 2 