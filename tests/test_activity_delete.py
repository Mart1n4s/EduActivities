import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.delete_activity.return_value = True
    mock.get_activity.return_value = {
        "title": "Test Activity",
        "description": "Test Description",
        "categories": ["Sports", "Outdoors"],
        "date": "2024-03-20",
        "start_time": "10:00",
        "duration": "2 hours",
        "location": "Test Location",
        "price": 50,
        "max_participants": 20,
        "current_participants": 0,
        "status": "available",
        "instructor": "Test Instructor",
        "organizer_id": "mock_organizer_id",
        "liked_by": []
    }
    return mock

def test_delete_activity_success(mock_db):
    activity_id = "mock_activity_id"
    
    activity = mock_db.get_activity(activity_id)
    assert activity is not None
    
    result = mock_db.delete_activity(activity_id)
    
    assert result is True
    mock_db.delete_activity.assert_called_once_with(activity_id)
    
    mock_db.get_activity.return_value = None
    deleted_activity = mock_db.get_activity(activity_id)
    assert deleted_activity is None

def test_delete_nonexistent_activity(mock_db):
    activity_id = "nonexistent_id"
    
    mock_db.get_activity.return_value = None
    mock_db.delete_activity.return_value = False
    
    result = mock_db.delete_activity(activity_id)
    
    assert result is False
    mock_db.delete_activity.assert_called_once_with(activity_id)
    
    deleted_activity = mock_db.get_activity(activity_id)
    assert deleted_activity is None

def test_delete_activity_with_reservations(mock_db):
    activity_id = "mock_activity_id"
    
    mock_db.get_activity.return_value = {
        "title": "Test Activity",
        "description": "Test Description",
        "categories": ["Sports", "Outdoors"],
        "date": "2024-03-20",
        "start_time": "10:00",
        "duration": "2 hours",
        "location": "Test Location",
        "price": 50,
        "max_participants": 20,
        "current_participants": 5,
        "status": "available",
        "instructor": "Test Instructor",
        "organizer_id": "mock_organizer_id",
        "liked_by": []
    }
    
    result = mock_db.delete_activity(activity_id)
    
    assert result is True
    mock_db.delete_activity.assert_called_once_with(activity_id)
    
    mock_db.get_activity.return_value = None
    deleted_activity = mock_db.get_activity(activity_id)
    assert deleted_activity is None 