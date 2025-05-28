from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .auth import get_current_user
from database import Database
from models.reservation import ReservationModel, ReservationStatus
from bson import ObjectId
from utils.recommendations import get_activity_recommendations


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/viewer", response_class=HTMLResponse)
async def viewer_page(request: Request):
    if not request.user.is_authenticated:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role not in ["viewer", "organizer"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Viewer or Organizer role required."
        )
    
    user_doc = Database.db.users.find_one({"username": current_user.username})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse(
        "viewer.html",
        {
            "request": request,
            "user": {
                "role": current_user.role,
                "id": str(user_doc["_id"])
            }
        }
    )


@router.get("/api/activities")
async def get_all_activities(request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role not in ["viewer", "organizer"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Viewer or Organizer role required."
        )
    
    user_doc = Database.db.users.find_one({"username": current_user.username})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = str(user_doc["_id"])
    
    all_activities = Database.get_all_activities()
    
    active_reservations = list(Database.db.reservations.find({
        "user_id": user_id,
        "status": {"$in": ["Pending", "Completed"]}
    }))
    reserved_activity_ids = {
        reservation["activity_id"] 
        for reservation in active_reservations
    }

    recommended_activities = get_activity_recommendations(user_id, all_activities)
    
    for activity in recommended_activities:
        activity["has_reserved"] = str(activity["_id"]) in reserved_activity_ids

    return {
        "activities": recommended_activities,
        "user_role": current_user.role
    }


@router.post("/api/activities/{activity_id}/like")
async def toggle_activity_like(activity_id: str, request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role not in ["viewer", "organizer"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Viewer or Organizer role required."
        )
    
    activity = Database.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    if "liked_by" not in activity:
        activity["liked_by"] = []
    
    user = Database.get_db().users.find_one({"username": current_user.username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    print(f"User ID: {user_id}")
    
    if user_id in activity["liked_by"]:
        activity["liked_by"].remove(user_id)
    else:
        activity["liked_by"].append(user_id)
    
    update_data = {"liked_by": activity["liked_by"]}
    
    success = Database.update_activity(activity_id, update_data)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to update activity like status"
        )
    
    return {
        "message": "Like toggled successfully",
        "liked": user_id in activity["liked_by"]
    }


@router.get("/api/organizers/{organizer_id}")
async def get_organizer(organizer_id: str, request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role not in ["viewer", "organizer"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Viewer or Organizer role required."
        )
    organizer = Database.get_db().users.find_one({
        "_id": ObjectId(organizer_id)
    })
    if not organizer:
        raise HTTPException(status_code=404, detail="Organizer not found")
    return {
        "name": organizer.get("name", "N/A"),
        "surname": organizer.get("surname", ""),
        "email": organizer.get("email", "N/A"),
        "telephone_number": organizer.get("telephone_number", "N/A"),
    }


@router.post("/reserve/{activity_id}")
async def reserve_activity(activity_id: str, request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = await get_current_user(request.cookies.get("access_token"))
    user_doc = Database.db.users.find_one({"username": user.username})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    activity = Database.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if activity.get("current_participants", 0) >= activity.get("max_participants", 0):
        raise HTTPException(status_code=400, detail="Activity is full")

    reservation = ReservationModel(
        activity_id=activity_id,
        user_id=str(user_doc["_id"]),
        status=ReservationStatus.PENDING
    )
    
    reservation_id = Database.create_reservation(reservation.dict())

    new_current = activity.get("current_participants", 0) + 1
    new_status = "full" if new_current >= activity.get("max_participants", 0) else "available"
    Database.update_activity(activity_id, {
        "current_participants": new_current,
        "status": new_status
    })

    return {"message": "Reservation created successfully", "reservation_id": reservation_id}


@router.get("/my-reservations", response_class=HTMLResponse)
async def my_reservations_page(request: Request):
    if not request.user.is_authenticated:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role != "viewer":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Viewer role required."
        )
    
    return templates.TemplateResponse(
        "my_reservations.html",
        {
            "request": request,
            "user": current_user
        }
    )


@router.get("/api/my-reservations")
async def get_my_reservations(request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    current_user = await get_current_user(request.cookies.get("access_token"))
    if current_user.role != "viewer":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Viewer role required."
        )
    
    user_doc = Database.db.users.find_one({"username": current_user.username})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    reservations = list(Database.db.reservations.find({
        "user_id": str(user_doc["_id"])
    }))
    
    reservation_details = []
    for reservation in reservations:
        activity = Database.get_activity(reservation["activity_id"])
        if activity:
            organizer = Database.db.users.find_one({"_id": ObjectId(activity["organizer_id"])})
            if organizer:
                reservation_details.append({
                    "_id": str(reservation["_id"]),
                    "status": reservation["status"],
                    "created_at": reservation.get("created_at", 0),
                    "activity": {
                        "title": activity["title"],
                        "description": activity["description"],
                        "date": activity["date"],
                        "start_time": activity["start_time"],
                        "location": activity["location"]
                    },
                    "organizer": {
                        "name": organizer.get("name", "N/A"),
                        "surname": organizer.get("surname", ""),
                        "email": organizer.get("email", "N/A"),
                        "telephone_number": organizer.get("telephone_number", "N/A")
                    }
                })
    
    reservation_details.sort(key=lambda r: r["created_at"] or 0, reverse=True)
    
    return {
        "reservations": reservation_details,
        "is_organizer": False
    }


