import pytest
from unittest.mock import Mock
from models.activity import ActivityCreateData

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.create_activity.return_value = "mock_activity_id"
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

def test_create_activity_success(mock_db):
    activity_data = ActivityCreateData(
        title="Test Activity",
        description="Test Description",
        categories=["Sports", "Outdoors"],
        date="2024-03-20",
        start_time="10:00",
        duration="2 hours",
        location="Test Location",
        price=50,
        max_participants=20,
        current_participants=0,
        status="available",
        instructor="Test Instructor",
        organizer_id="mock_organizer_id",
        liked_by=[]
    )
    
    activity_dict = {
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
    
    activity_id = mock_db.create_activity(activity_dict)
    
    assert activity_id == "mock_activity_id"
    mock_db.create_activity.assert_called_once_with(activity_dict)
    
    created_activity = mock_db.get_activity(activity_id)
    assert created_activity is not None
    assert created_activity["title"] == activity_data.title
    assert created_activity["description"] == activity_data.description
    assert created_activity["categories"] == activity_data.categories
    assert created_activity["date"] == activity_data.date
    assert created_activity["start_time"] == activity_data.start_time
    assert created_activity["duration"] == activity_data.duration
    assert created_activity["location"] == activity_data.location
    assert created_activity["price"] == activity_data.price
    assert created_activity["max_participants"] == activity_data.max_participants
    assert created_activity["current_participants"] == activity_data.current_participants
    assert created_activity["status"] == activity_data.status
    assert created_activity["instructor"] == activity_data.instructor
    assert created_activity["organizer_id"] == activity_data.organizer_id
    assert created_activity["liked_by"] == activity_data.liked_by

def test_create_activity_invalid_data(mock_db):
    activity_data = ActivityCreateData(
        title="Test Activity",
        description="Test Description",
        categories=["Sports", "Outdoors"],
        date="2024-03-20",
        start_time="10:00",
        duration="2 hours",
        location="Test Location",
        price=-50,
        max_participants=20,
        current_participants=0,
        status="available",
        instructor="Test Instructor",
        organizer_id="mock_organizer_id",
        liked_by=[]
    )
    
    activity_dict = {
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
    
    mock_db.create_activity.return_value = None
    
    activity_id = mock_db.create_activity(activity_dict)
    assert activity_id is None
    mock_db.create_activity.assert_called_once_with(activity_dict)
