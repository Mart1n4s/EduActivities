from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from views.auth import get_current_user
from database import Database
from models.user import ProfileUpdateData, AuthUser
from utils.validators import create_success_response, validate_user_data

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/api/profile")
async def get_profile(current_user: AuthUser = Depends(get_current_user)):
    user = await Database.get_user_by_username(current_user.username)
    
    return {
        "username": user["username"],
        "name": user["name"],
        "surname": user["surname"],
        "email": user["email"],
        "telephone_number": user["telephone_number"]
    }


@router.put("/api/profile")
async def update_profile(
    profile_data: ProfileUpdateData,
    current_user: AuthUser = Depends(get_current_user)
):
    user = await Database.get_user_by_username(current_user.username)

    validation_error = validate_user_data(
        username=current_user.username,
        name=profile_data.name,
        surname=profile_data.surname,
        email=profile_data.email,
        telephone_number=profile_data.telephone_number,
        password=None,
        role=current_user.role,
        is_update=True,
        current_user_id=str(user["_id"])
    )
    
    if validation_error:
        return validation_error

    update_data = {
        "name": profile_data.name,
        "surname": profile_data.surname,
        "email": profile_data.email,
        "telephone_number": profile_data.telephone_number
    }

    await Database.update_user_profile(current_user.username, update_data)
    
    return create_success_response("Profile updated successfully")
