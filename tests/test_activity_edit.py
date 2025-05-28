import pytest
from unittest.mock import Mock
from models.activity import ActivityUpdateData

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.update_activity.return_value = True
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

def test_update_activity_success(mock_db):
    activity_id = "mock_activity_id"
    activity_data = ActivityUpdateData(
        title="Updated Activity",
        description="Updated Description",
        categories=["Music", "Indoors"],
        date="2024-03-21",
        start_time="14:00",
        duration="3 hours",
        location="New Location",
        price=75,
        max_participants=15,
        current_participants=5,
        status="available",
        instructor="New Instructor",
        organizer_id="mock_organizer_id",
        liked_by=[]
    )
    
    update_dict = {
        "title": activity_data.title,
        "description": activity_data.description,
        "categories": activity_data.categories,
        "date": activity_data.date,
        "start_time": activity_data.start_time,
        "duration": activity_data.duration,
        "location": activity_data.location,
        "price": activity_data.price,
        "max_participants": activity_data.max_participants,
        "current_participants": activity_data.current_participants,
        "status": activity_data.status,
        "instructor": activity_data.instructor,
        "organizer_id": activity_data.organizer_id,
        "liked_by": activity_data.liked_by
    }
    
    mock_db.get_activity.return_value = update_dict
    
    result = mock_db.update_activity(activity_id, update_dict)
    
    assert result is True
    mock_db.update_activity.assert_called_once_with(activity_id, update_dict)
    
    updated_activity = mock_db.get_activity(activity_id)
    assert updated_activity is not None
    assert updated_activity["title"] == activity_data.title
    assert updated_activity["description"] == activity_data.description
    assert updated_activity["categories"] == activity_data.categories
    assert updated_activity["date"] == activity_data.date
    assert updated_activity["start_time"] == activity_data.start_time
    assert updated_activity["duration"] == activity_data.duration
    assert updated_activity["location"] == activity_data.location
    assert updated_activity["price"] == activity_data.price
    assert updated_activity["max_participants"] == activity_data.max_participants
    assert updated_activity["current_participants"] == activity_data.current_participants
    assert updated_activity["status"] == activity_data.status
    assert updated_activity["instructor"] == activity_data.instructor
    assert updated_activity["organizer_id"] == activity_data.organizer_id
    assert updated_activity["liked_by"] == activity_data.liked_by

def test_update_activity_invalid_price(mock_db):
    activity_id = "mock_activity_id"
    activity_data = ActivityUpdateData(
        title="Test Activity",
        description="Test Description",
        categories=["Sports", "Outdoors"],
        date="2024-03-20",
        start_time="10:00",
        duration="2 hours",
        location="Test Location",
        price=50,
        max_participants=-20,
        current_participants=5,
        status="available",
        instructor="Test Instructor",
        organizer_id="mock_organizer_id",
        liked_by=[]
    )
    
    update_dict = {
        "title": activity_data.title,
        "description": activity_data.description,
        "categories": activity_data.categories,
        "date": activity_data.date,
        "start_time": activity_data.start_time,
        "duration": activity_data.duration,
        "location": activity_data.location,
        "price": activity_data.price,
        "max_participants": activity_data.max_participants,
        "current_participants": activity_data.current_participants,
        "status": activity_data.status,
        "instructor": activity_data.instructor,
        "organizer_id": activity_data.organizer_id,
        "liked_by": activity_data.liked_by
    }
    
    mock_db.update_activity.return_value = False
    
    result = mock_db.update_activity(activity_id, update_dict)
    
    assert result is False
    mock_db.update_activity.assert_called_once_with(activity_id, update_dict)
 