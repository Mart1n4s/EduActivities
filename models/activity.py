from pydantic import BaseModel, Field
from typing import Optional

class ActivityCreateData(BaseModel):
    title: str
    description: str
    categories: list[str]
    date: str
    start_time: str
    duration: str
    location: str
    price: int
    max_participants: int
    current_participants: int = 0
    status: str
    instructor: str
    organizer_id: Optional[str] = None
    liked_by: list[str] = Field(default_factory=list)


class ActivityUpdateData(BaseModel):
    title: str
    description: str
    categories: list[str]
    date: str
    start_time: str
    duration: str
    location: str
    price: int
    max_participants: int
    current_participants: int
    status: str
    instructor: str
    organizer_id: str
    liked_by: list[str]

