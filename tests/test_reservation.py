import pytest
from unittest.mock import Mock
from datetime import datetime
from models.reservation import ReservationStatus

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.create_reservation.return_value = {
        "_id": "mock_reservation_id",
        "activity_id": "mock_activity_id",
        "user_id": "mock_user_id",
        "status": ReservationStatus.PENDING,
        "created_at": datetime.utcnow()
    }
    return mock

def test_create_reservation_success(mock_db):
    activity_id = "mock_activity_id"
    user_id = "mock_user_id"
    
    reservation = mock_db.create_reservation(activity_id, user_id)
    
    assert reservation is not None
    assert reservation["activity_id"] == activity_id
    assert reservation["user_id"] == user_id
    assert reservation["status"] == ReservationStatus.PENDING
    assert "created_at" in reservation
    
    mock_db.create_reservation.assert_called_once_with(activity_id, user_id)

def test_update_reservation_status(mock_db):
    reservation_id = "mock_reservation_id"
    new_status = ReservationStatus.COMPLETED
    
    mock_db.update_reservation_status.return_value = {
        "_id": reservation_id,
        "status": new_status
    }
    
    updated_reservation = mock_db.update_reservation_status(reservation_id, new_status)
    
    assert updated_reservation is not None
    assert updated_reservation["_id"] == reservation_id
    assert updated_reservation["status"] == new_status
    
    mock_db.update_reservation_status.assert_called_once_with(reservation_id, new_status)
