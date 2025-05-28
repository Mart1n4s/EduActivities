import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.delete_user.return_value = True
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

def test_delete_user_success(mock_db):
    user_id = "mock_user_id"
    
    user = mock_db.get_user(user_id)
    assert user is not None
    
    result = mock_db.delete_user(user_id)
    
    assert result is True
    mock_db.delete_user.assert_called_once_with(user_id)
    
    mock_db.get_user.return_value = None
    deleted_user = mock_db.get_user(user_id)
    assert deleted_user is None

def test_delete_nonexistent_user(mock_db):
    user_id = "nonexistent_id"
    
    mock_db.get_user.return_value = None
    mock_db.delete_user.return_value = False
    
    result = mock_db.delete_user(user_id)
    
    assert result is False
    mock_db.delete_user.assert_called_once_with(user_id)
    
    deleted_user = mock_db.get_user(user_id)
    assert deleted_user is None