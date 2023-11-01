from fastapi import APIRouter, status, UploadFile, Query, Depends
from app.utils.response_utils import response
from app.db import db
from app.utils.cloudinary import media_upload, media_deletion
from app.schema import Status, PrivacyEnum, UserProfile
from app.serializer import status_serializer
from app.api.user import userTable
from bson import ObjectId
from datetime import datetime, timedelta
from app.utils import oauth2

router = APIRouter(
    tags=['Status'],
    prefix='/api'
)

statusTable = db['status']

@router.post('/status', response_description="Upload status")
async def add_status(media_file: UploadFile, caption:str='', current_user: dict = Depends(oauth2.get_current_user)):
    try:
        user_id = current_user['id']

        user = await userTable.find_one({'_id': ObjectId(user_id)})
        if not user:
            return response(status_code=404, message="No such user!")
        
        content = await media_upload(media_file)
        created_at = datetime.utcnow()
        expired_at = datetime.utcnow() + timedelta(hours=24)
        is_expired =  datetime.utcnow() >= expired_at
       
        status_instance = Status(
            user_id=user_id, 
            content=content, 
            caption=caption, 
            created_at=created_at, 
            expired_at=expired_at, 
            privacy=PrivacyEnum.public, 
            is_expired=is_expired
        )

        new_status_id_ref = await statusTable.insert_one(status_instance.dict())
        new_status = await statusTable.find_one({'_id': new_status_id_ref.inserted_id})

        return response(status_code=201, message="Status has been added!", data=status_serializer(new_status))
    except Exception as e:
        return response(status_code=500, message=str(e))
    

@router.delete('/status/{status_id}', response_description="Remove status")
async def remove_status(status_id: str, current_user: dict = Depends(oauth2.get_current_user)):
    try:
        status_obj = await statusTable.find_one({"_id": ObjectId(status_id)})
        if not status_obj:
            return response(status_code=404, message="Status not found!")
        
        if status_obj['user_id'] != current_user['user_id']:
            return response(status_code=442, message="This status does not belong to this user!")
        
        deleted_media = await media_deletion(status_obj['content']['public_id'])
        if deleted_media: 
            await statusTable.delete_one({"_id": ObjectId(status_id)})
            return response(status_code=200, message="Status has been deleted")
        else:
            return response(status_code=500, message="Failed to delete media")
    except Exception as e:
        return response(status_code=500, message=str(e))


@router.get('/status/{user_id}', response_description="Get all statuses for a user")
async def get_all_statuses(
    user_id: str, 
    page: int=Query(default=1,  description='Page number to fatch', ge=1),
    limit: int=Query(default=10, description='Number of documents per page', le=100),
    current_user: dict = Depends(oauth2.get_current_user)
):
    try:
        query = {'user_id': user_id, 'is_expired': False}
        total_status_count = await statusTable.count_documents(query)

        if total_status_count == 0:
            return response(status_code=404, message="Status not found!")
        
        status_list = await statusTable.find({'user_id':user_id, 'is_expired': False}).skip((page - 1) * limit).limit(limit).to_list(limit)

        res = {
            "status_list": [status_serializer(s) for s in status_list],
            "page": page,
            "limit": limit,
            "total_status": total_status_count
        }
        
        return response(status_code=200, message="All status fetched for this user", data=res)
    except Exception as e:
        return response(status_code=500, message=str(e))
