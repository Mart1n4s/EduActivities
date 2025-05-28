from fastapi.responses import JSONResponse
import re
from typing import Optional

ERROR_MESSAGES = {
    "empty_field": "No fields can be empty",
    "invalid_email": "Invalid email format",
    "invalid_phone": "Invalid phone number format",
    "password_too_short": "Password must be at least 6 characters long",
    "username_taken": "Username is already taken",
    "passwords_dont_match": "Passwords do not match",
    "invalid_credentials": "Incorrect username or password",
    "not_authenticated": "Not authenticated",
    "user_not_found": "User not found",
    "not_admin": "Access denied. Admin role required.",
    "activity_not_found": "Activity not found",
    "no_categories": "At least one category must be selected",
    "negative_price": "Price cannot be negative",
    "invalid_max_participants": "Maximum participants must be greater than 0",
    "negative_participants": "Current participants cannot be negative",
    "exceeded_participants": "Current participants cannot exceed maximum participants",
    "invalid_status": "Invalid activity status"
}

PATTERNS = {
    "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "phone": r'^\+?[0-9]{10,15}$'
}

def create_error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "status": "error"}
    )

def create_success_response(message: str, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "status": "success"}
    )

def validate_user_data(
    username: str,
    name: str,
    surname: str,
    email: str,
    telephone_number: str,
    password: Optional[str],
    role: str,
    is_update: bool = False,
    current_user_id: Optional[str] = None,
    confirm_password: Optional[str] = None
) -> Optional[JSONResponse]:
    for field in [username, name, surname, email, telephone_number, role]:
        if not field or not field.strip():
            return create_error_response(ERROR_MESSAGES["empty_field"])
    
    if not re.match(PATTERNS["email"], email):
        return create_error_response(ERROR_MESSAGES["invalid_email"])
    
    if not re.match(PATTERNS["phone"], telephone_number):
        return create_error_response(ERROR_MESSAGES["invalid_phone"])
    
    if password:
        if len(password) < 6:
            return create_error_response(ERROR_MESSAGES["password_too_short"])
        
        if not is_update and confirm_password is not None and password != confirm_password:
            return create_error_response(ERROR_MESSAGES["passwords_dont_match"])
    
    return None

def validate_activity_data(
    title: str,
    description: str,
    categories: list[str],
    date: str,
    start_time: str,
    duration: str,
    location: str,
    price: int,
    max_participants: int,
    current_participants: int,
    status: str,
    instructor: str,
    organizer_id: str,
    is_update: bool = False
) -> Optional[JSONResponse]:
    for field in [title, description, date, start_time, duration, location, instructor, organizer_id, status]:
        if not field or not field.strip():
            return create_error_response(ERROR_MESSAGES["empty_field"])
    
    if not categories or len(categories) == 0:
        return create_error_response(ERROR_MESSAGES["no_categories"])
    
    if price < 0:
        return create_error_response(ERROR_MESSAGES["negative_price"])
    
    if max_participants <= 0:
        return create_error_response(ERROR_MESSAGES["invalid_max_participants"])
    
    if status not in ["available", "full"]:
        return create_error_response(ERROR_MESSAGES["invalid_status"])
    
    if is_update:
        if current_participants < 0:
            return create_error_response(ERROR_MESSAGES["negative_participants"])
        if current_participants > max_participants:
            return create_error_response(ERROR_MESSAGES["exceeded_participants"])
    
    return None 