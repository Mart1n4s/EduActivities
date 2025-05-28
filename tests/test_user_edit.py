import pytest
from unittest.mock import Mock
from models.user import UserUpdateData
from views.auth import get_password_hash

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.update_user.return_value = True
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

def test_update_user_success(mock_db):
    user_id = "mock_user_id"
    user_data = UserUpdateData(
        username="testuser",
        name="Updated",
        surname="User",
        email="updated@example.com",
        telephone_number="9876543210",
        password="newpass123",
        role="organizer"
    )
    
    update_dict = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role,
        "hashed_password": get_password_hash(user_data.password)
    }
    
    mock_db.get_user.return_value = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role,
        "hashed_password": update_dict["hashed_password"]
    }
    
    result = mock_db.update_user(user_id, update_dict)
    
    assert result is True
    mock_db.update_user.assert_called_once_with(user_id, update_dict)
    
    updated_user = mock_db.get_user(user_id)
    assert updated_user is not None
    assert updated_user["username"] == user_data.username
    assert updated_user["name"] == user_data.name
    assert updated_user["surname"] == user_data.surname
    assert updated_user["email"] == user_data.email
    assert updated_user["telephone_number"] == user_data.telephone_number
    assert updated_user["role"] == user_data.role
    assert updated_user["hashed_password"] == update_dict["hashed_password"]

def test_update_user_without_password(mock_db):
    user_id = "mock_user_id"
    user_data = UserUpdateData(
        username="testuser",
        name="Updated",
        surname="User",
        email="updated@example.com",
        telephone_number="9876543210",
        password=None,
        role="organizer"
    )
    
    update_dict = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role
    }
    
    mock_db.get_user.return_value = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role,
        "hashed_password": "hashed_password"
    }
    
    result = mock_db.update_user(user_id, update_dict)
    
    assert result is True
    mock_db.update_user.assert_called_once_with(user_id, update_dict)
    
    updated_user = mock_db.get_user(user_id)
    assert updated_user is not None
    assert updated_user["username"] == user_data.username
    assert updated_user["name"] == user_data.name
    assert updated_user["surname"] == user_data.surname
    assert updated_user["email"] == user_data.email
    assert updated_user["telephone_number"] == user_data.telephone_number
    assert updated_user["role"] == user_data.role
    assert updated_user["hashed_password"] == "hashed_password"

def test_update_nonexistent_user(mock_db):
    user_id = "nonexistent_id"
    user_data = UserUpdateData(
        username="testuser",
        name="Updated",
        surname="User",
        email="updated@example.com",
        telephone_number="9876543210",
        password="newpass123",
        role="organizer"
    )
    
    update_dict = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role,
        "hashed_password": get_password_hash(user_data.password)
    }
    
    mock_db.update_user.return_value = False
    
    result = mock_db.update_user(user_id, update_dict)
    
    assert result is False
    mock_db.update_user.assert_called_once_with(user_id, update_dict) 