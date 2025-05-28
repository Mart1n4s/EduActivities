from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import Database
from .auth import get_current_user, get_password_hash
from models.activity import ActivityCreateData, ActivityUpdateData
from models.user import UserCreateData, UserUpdateData
from utils.validators import (
    ERROR_MESSAGES,
    create_success_response,
    validate_user_data,
    validate_activity_data
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

async def check_admin(request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES["not_authenticated"])
    
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail=ERROR_MESSAGES["not_admin"]
        )
    return current_user

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    if not request.user.is_authenticated:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    current_user = await check_admin(request)
    
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": current_user
        }
    )

@router.get("/api/admin/users")
async def get_all_users(request: Request):
    await check_admin(request)
    users = Database.get_all_users()
    return users

@router.get("/api/admin/users/{user_id}")
async def get_user(user_id: str, request: Request):
    await check_admin(request)
    
    user = Database.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    return user

@router.post("/api/admin/users")
async def create_user(user_data: UserCreateData, request: Request):
    await check_admin(request)
    
    validation_error = validate_user_data(
        user_data.username,
        user_data.name,
        user_data.surname,
        user_data.email,
        user_data.telephone_number,
        user_data.password,
        user_data.role,
        is_update=False
    )
    
    if validation_error:
        return validation_error
        
    new_user = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role,
        "hashed_password": get_password_hash(user_data.password)
    }
    
    if not Database.create_user(new_user):
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return create_success_response("User created successfully")

@router.put("/api/admin/users/{user_id}")
async def update_user(user_id: str, user_data: UserUpdateData, request: Request):
    await check_admin(request)
    
    validation_error = validate_user_data(
        user_data.username,
        user_data.name,
        user_data.surname,
        user_data.email,
        user_data.telephone_number,
        user_data.password,
        user_data.role,
        is_update=True,
        current_user_id=user_id
    )
    
    if validation_error:
        return validation_error
    
    update_data = {
        "username": user_data.username,
        "name": user_data.name,
        "surname": user_data.surname,
        "email": user_data.email,
        "telephone_number": user_data.telephone_number,
        "role": user_data.role
    }
    
    if user_data.password:
        update_data["hashed_password"] = get_password_hash(user_data.password)
    
    if not Database.update_user(user_id, update_data):
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    return create_success_response("User updated successfully")

@router.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, request: Request):
    
    await check_admin(request)
    
    if not Database.delete_user(user_id):
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    return create_success_response("User deleted successfully")

@router.get("/api/admin/activities")
async def get_all_activities(request: Request):
    await check_admin(request)
    
    activities = Database.get_all_activities()
    for activity in activities:
        organizer = Database.get_user(activity["organizer_id"])
        if organizer:
            activity["organizer_name"] = f"{organizer.get('name', '')} {organizer.get('surname', '')}"
    return activities

@router.get("/api/admin/activities/{activity_id}")
async def get_activity(activity_id: str, request: Request):
    await check_admin(request)
    
    activity = Database.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    return activity

@router.post("/api/admin/activities")
async def create_activity(activity_data: ActivityCreateData, request: Request):
    await check_admin(request)
    
    validation_error = validate_activity_data(
        activity_data.title,
        activity_data.description,
        activity_data.categories,
        activity_data.date,
        activity_data.start_time,
        activity_data.duration,
        activity_data.location,
        activity_data.price,
        activity_data.max_participants,
        activity_data.current_participants,
        activity_data.status,
        activity_data.instructor,
        activity_data.organizer_id,
        is_update=False
    )
    
    if validation_error:
        return validation_error
    
    new_activity = {
        "title": activity_data.title,
        "description": activity_data.description,
        "categories": activity_data.categories,
        "date": activity_data.date,
        "start_time": activity_data.start_time,
        "duration": activity_data.duration,
        "location": activity_data.location,
        "price": activity_data.price,
        "max_participants": activity_data.max_participants,
        "current_participants": 0,
        "status": activity_data.status,
        "instructor": activity_data.instructor,
        "organizer_id": activity_data.organizer_id,
        "liked_by": []
    }
    
    if not Database.create_activity(new_activity):
        raise HTTPException(status_code=500, detail="Failed to create activity")
    
    return create_success_response("Activity created successfully", 201)

@router.put("/api/admin/activities/{activity_id}")
async def update_activity(activity_id: str, activity_data: ActivityUpdateData, request: Request):
    await check_admin(request)
    
    current_activity = Database.get_activity(activity_id)
    if not current_activity:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    validation_error = validate_activity_data(
        activity_data.title,
        activity_data.description,
        activity_data.categories,
        activity_data.date,
        activity_data.start_time,
        activity_data.duration,
        activity_data.location,
        activity_data.price,
        activity_data.max_participants,
        activity_data.current_participants,
        activity_data.status,
        activity_data.instructor,
        activity_data.organizer_id,
        is_update=True
    )
    
    if validation_error:
        return validation_error
    
    update_data = {
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
    
    if not Database.update_activity(activity_id, update_data):
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    return create_success_response("Activity updated successfully")

@router.delete("/api/admin/activities/{activity_id}")
async def delete_activity(activity_id: str, request: Request):
    await check_admin(request)
    
    if not Database.delete_activity(activity_id):
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    return create_success_response("Activity deleted successfully") 