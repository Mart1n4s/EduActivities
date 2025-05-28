from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ReservationStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class ReservationModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    activity_id: str
    user_id: str
    status: ReservationStatus = ReservationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
