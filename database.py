from pymongo import MongoClient
import os
from bson import ObjectId

class Database:
    client = None
    db = None

    @classmethod
    def connect_db(cls):
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        cls.client = MongoClient(mongo_uri)
        cls.db = cls.client["EduActivities"]

    @classmethod
    def close_db(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_db(cls):
        return cls.db

    @classmethod
    def create_user(cls, user_data: dict) -> str:
        result = cls.db.users.insert_one(user_data)
        return str(result.inserted_id)

    @classmethod
    def get_user(cls, user_id: str) -> dict:
        user = cls.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    @classmethod
    def get_all_users(cls) -> list:
        users = list(cls.db.users.find({}, {"hashed_password": 0}))
        return [
            {
                **user,
                "_id": str(user["_id"])
            }
            for user in users
        ]

    @classmethod
    def update_user(cls, user_id: str, user_data: dict) -> bool:
        if "_id" in user_data:
            del user_data["_id"]
        
        user = cls.get_user(user_id)
        if not user:
            return False
            
        cls.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": user_data}
        )
        return True 

    @classmethod
    def delete_user(cls, user_id: str) -> bool:
        user = cls.get_user(user_id)
        if not user:
            return False
            
        if user.get("role") == "organizer":
            activities = cls.get_activities_by_organizer(user_id)
            activity_ids = [activity["_id"] for activity in activities]
            
            if activity_ids:
                cls.db.reservations.delete_many({"activity_id": {"$in": activity_ids}})
            
            cls.db.activities.delete_many({"organizer_id": user_id})
        else:
            reservations = list(cls.db.reservations.find({"user_id": user_id}))
            for reservation in reservations:
                activity = cls.get_activity(reservation["activity_id"])
                if activity:
                    if reservation.get("status") == "Pending":
                        new_current = max(0, activity.get("current_participants", 0) - 1)
                        new_status = "available" if new_current < activity.get("max_participants", 0) else "full"
                        cls.update_activity(reservation["activity_id"], {
                            "current_participants": new_current,
                            "status": new_status
                        })
        
        cls.db.activities.update_many(
            {"liked_by": user_id},
            {"$pull": {"liked_by": user_id}}
        )
        
        cls.db.reservations.delete_many({"user_id": user_id})
        
        result = cls.db.users.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    @classmethod
    async def get_user_by_username(cls, username: str) -> dict:
        return cls.db.users.find_one({"username": username})

    @classmethod
    async def update_user_profile(cls, username: str, profile_data: dict) -> bool:
        user_fields = ["name", "surname", "email", "telephone_number"]
        update_data = {}
        
        for field in user_fields:
            if field in profile_data:
                update_data[field] = profile_data[field]
        
        if "password" in profile_data and profile_data["password"]:
            from views.auth import get_password_hash
            update_data["hashed_password"] = get_password_hash(
                profile_data["password"]
            )
        
        result = cls.db.users.update_one(
            {"username": username},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @classmethod
    def create_activity(cls, activity: dict) -> str:
        result = cls.db.activities.insert_one(activity)
        return str(result.inserted_id)

    @classmethod
    def get_activities_by_organizer(cls, organizer_id: str) -> list:
        activities = list(cls.db.activities.find({"organizer_id": organizer_id}))
        return [
            {
                **activity,
                "_id": str(activity["_id"])
            }
            for activity in activities
        ]

    @classmethod
    def get_all_activities(cls) -> list:
        activities = cls.db.activities.find()
        return [
            {
                **activity,
                "_id": str(activity["_id"])
            }
            for activity in activities
        ]

    @classmethod
    def get_activity(cls, activity_id: str) -> dict:
        activity = cls.db.activities.find_one(
            {"_id": ObjectId(activity_id)}
        )
        if activity:
            activity["_id"] = str(activity["_id"])
        return activity

    @classmethod
    def update_activity(cls, activity_id: str, activity_data: dict) -> bool:
        if "_id" in activity_data:
            del activity_data["_id"]
        
        activity = cls.get_activity(activity_id)
        if not activity:
            return False
            
        cls.db.activities.update_one(
            {"_id": ObjectId(activity_id)},
            {"$set": activity_data}
        )
        return True

    @classmethod
    def delete_activity(cls, activity_id: str) -> bool: 
        cls.db.reservations.delete_many({"activity_id": activity_id})
        result = cls.db.activities.delete_one({"_id": ObjectId(activity_id)})
        return result.deleted_count > 0

    @classmethod
    def create_reservation(cls, reservation_data: dict) -> str:
        result = cls.db.reservations.insert_one(reservation_data)
        return str(result.inserted_id)

    @classmethod
    def get_reservation(cls, reservation_id: str) -> dict:
        reservation = cls.db.reservations.find_one({"_id": ObjectId(reservation_id)})
        if reservation:
            reservation["_id"] = str(reservation["_id"])
        return reservation

    @classmethod
    def update_reservation_status(cls, reservation_id: str, new_status: str) -> bool:
        result = cls.db.reservations.update_one(
            {"_id": ObjectId(reservation_id)},
            {"$set": {"status": new_status}}
        )
        return result.modified_count > 0
