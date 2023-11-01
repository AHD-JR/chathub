from app.db import db
from app.schema import Notification, User
from app.serializer import notification_serializer
from app.utils.response_utils import response
from datetime import datetime
from bson import ObjectId

notificationTable = db['notifications']

async def create_notification(user: User, message: str):
    try:
        created_at = datetime.utcnow()
        is_read = False

        notification_instance = Notification(user=user, message=message, created_at=created_at, is_read=is_read)
        
        await notificationTable.insert_one(notification_instance.dict())
        print(notification_instance)
    except  Exception as e:
        return response(status_code=500, message=str(e))  


async def get_notifications(user_id: str):
    try:
        notification = await notificationTable.find({'user.user_id': user_id}).to_list(10)
        if not notification:
            return response(status_code=404, message="No notification")
        
        return notification_serializer(notification)
    except Exception as e:
        return response(status_code=500, message=str(e))  


async def mark_as_read(user_id: str):
    try:
        await notificationTable.update_many({'user.user_id': user_id}, {'$set': {'is_read': True}})
    except Exception as e:
        return response(status_code=500, message=str(e))  
    
    
async def delete_notification(notification_id: str): 
    try:
        await notificationTable.delete_one({"_id": ObjectId(notification_id)})
    except Exception as e:
        return response(status_code=500, message=str(e))
