from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from database import Database
from models.activity import ActivityCreateData, ActivityUpdateData
from views.auth import get_current_user
from utils.validators import validate_activity_data, create_success_response, ERROR_MESSAGES
from bson import ObjectId

router = APIRouter()
templates = Jinja2Templates(directory="templates")

async def check_organizer(request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES["not_authenticated"])
    
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role != "organizer":
        raise HTTPException(
            status_code=403,
            detail=ERROR_MESSAGES["not_organizer"]
        )
    return current_user

@router.get("/organizer")
async def organizer_dashboard(request: Request):
    if not request.user.is_authenticated:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    await check_organizer(request)
    
    return templates.TemplateResponse(
        "organizer.html",
        {"request": request}
    )

@router.get("/organizer/reservations")
async def organizer_reservations(request: Request):
    if not request.user.is_authenticated:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    await check_organizer(request)
    
    return templates.TemplateResponse(
        "organizer_reservations.html",
        {"request": request}
    )

@router.get("/api/activities/organizer")
async def get_organizer_activities(request: Request):
    await check_organizer(request)
    
    user_doc = await Database.get_user_by_username(request.user.username)
    if not user_doc:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    activities = Database.get_activities_by_organizer(str(user_doc["_id"]))
    return activities

@router.post("/api/organizer/activities")
async def create_activity(activity_data: ActivityCreateData, request: Request):
    await check_organizer(request)
    
    user_doc = await Database.get_user_by_username(request.user.username)
    if not user_doc:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
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
        0,
        "available",
        activity_data.instructor,
        str(user_doc["_id"]),
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
        "status": "available",
        "instructor": activity_data.instructor,
        "organizer_id": str(user_doc["_id"]),
        "liked_by": []
    }
    
    activity_id = Database.create_activity(new_activity)
    if not activity_id:
        raise HTTPException(status_code=500, detail="Failed to create activity")
    
    return create_success_response("Activity created successfully", 201)

@router.get("/api/activities/{activity_id}")
async def get_activity(activity_id: str, request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES["not_authenticated"])
    
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role not in ["viewer", "organizer"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Viewer or Organizer role required."
        )
    
    user_doc = await Database.get_user_by_username(current_user.username)
    if not user_doc:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    activity = Database.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    active_reservations = list(Database.db.reservations.find({
        "activity_id": activity_id,
        "user_id": str(user_doc["_id"]),
        "status": {"$in": ["Pending", "Completed"]}
    }))
    
    if active_reservations:
        activity["has_reserved"] = True
        activity["reservation_id"] = str(active_reservations[0]["_id"])
    else:
        activity["has_reserved"] = False
    
    return activity

@router.put("/api/organizer/activities/{activity_id}")
async def update_activity(activity_id: str, activity_data: ActivityUpdateData, request: Request):
    await check_organizer(request)
    
    existing_activity = Database.get_activity(activity_id)
    if not existing_activity:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    user_doc = await Database.get_user_by_username(request.user.username)
    if not user_doc:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    if str(existing_activity["organizer_id"]) != str(user_doc["_id"]):
        raise HTTPException(
            status_code=403,
            detail=ERROR_MESSAGES["not_authorized"]
        )
    
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
        str(user_doc["_id"]),
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
        "organizer_id": str(user_doc["_id"]),
        "liked_by": activity_data.liked_by
    }
    
    if not Database.update_activity(activity_id, update_data):
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    return create_success_response("Activity updated successfully")

@router.delete("/api/activities/{activity_id}")
async def delete_activity(activity_id: str, request: Request):
    
    await check_organizer(request)
    
    existing_activity = Database.get_activity(activity_id)
    if not existing_activity:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    user_doc = await Database.get_user_by_username(request.user.username)
    if not user_doc:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    if str(existing_activity["organizer_id"]) != str(user_doc["_id"]):
        raise HTTPException(
            status_code=403,
            detail=ERROR_MESSAGES["not_authorized"]
        )
    
    if not Database.delete_activity(activity_id):
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    return create_success_response("Activity deleted successfully")

@router.get("/api/organizer/reservations")
async def get_organizer_reservations(request: Request):
    try:
        await check_organizer(request)
        
        user_doc = await Database.get_user_by_username(request.user.username)
        if not user_doc:
            raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
        
        activities = Database.get_activities_by_organizer(str(user_doc["_id"]))
        activity_ids = [str(activity["_id"]) for activity in activities]
        
        reservations = list(Database.db.reservations.find({
            "activity_id": {"$in": activity_ids}
        }))
        
        reservation_details = []
        for reservation in reservations:
            reservation["_id"] = str(reservation["_id"])
            activity = Database.get_activity(reservation["activity_id"])
            user_info = Database.db.users.find_one({"_id": ObjectId(reservation["user_id"])})
            
            if activity and user_info:
                reservation_details.append({
                    "_id": str(reservation["_id"]),
                    "status": reservation["status"],
                    "created_at": reservation.get("created_at"),
                    "activity": {
                        "title": activity["title"]
                    },
                    "user": {
                        "name": user_info.get("name", "N/A"),
                        "surname": user_info.get("surname", ""),
                        "email": user_info.get("email", "N/A"),
                        "telephone_number": user_info.get("telephone_number", "N/A")
                    }
                })
        
        return {"reservations": reservation_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/reservations/{reservation_id}/status")
async def update_reservation_status(reservation_id: str, status_update: dict, request: Request):
    await check_organizer(request)
    
    reservation = Database.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["reservation_not_found"])
    
    activity = Database.get_activity(reservation["activity_id"])
    if not activity:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["activity_not_found"])
    
    user_doc = await Database.get_user_by_username(request.user.username)
    if not user_doc:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    if str(activity["organizer_id"]) != str(user_doc["_id"]):
        raise HTTPException(
            status_code=403,
            detail=ERROR_MESSAGES["not_authorized"]
        )
    
    new_status = status_update.get("status")
    if not new_status or new_status not in ["Pending", "Completed", "Cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    if not Database.update_reservation_status(reservation_id, new_status):
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["reservation_not_found"])
    
    
    if new_status == "Cancelled" and reservation.get("status") == "Pending":
        new_current = max(0, activity.get("current_participants", 0) - 1)
        new_activity_status = "available" if new_current < activity.get("max_participants", 0) else "full"
        Database.update_activity(reservation["activity_id"], {
            "current_participants": new_current,
            "status": new_activity_status
        })
    
    return create_success_response("Reservation status updated successfully") 