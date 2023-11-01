from fastapi import APIRouter, status, Depends, UploadFile, Query
from app.db import db
from app.schema import Post, Comment, UserProfile
from app.utils.cloudinary import media_upload, media_deletion
from app.utils.oauth2 import get_current_user
from app.utils.response_utils import response
from datetime import datetime
from app.serializer import post_serializer
from app.utils import oauth2
from bson import ObjectId

router = APIRouter(
    tags=['Post'],
    prefix='/auth'
)

postTable = db['posts']

@router.post('/post', response_description='Upload a post', response_model=Post)
async def add_post(media_file: UploadFile, caption:str = Query(default='', max_length=1000), current_user: dict = Depends(get_current_user)):
    try:
        content = await media_upload(media_file)
        if not content:
            return response(status_code=500, message="Media file not uploaded!")
        
        user = {
            "user_id": current_user['id'],
            "username": current_user['username']  
        }
        likes=[]
        comments=[]
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()
        
        post_instance = Post(
            user=user,
            content=content,
            caption=caption,
            likes=likes,
            comments=comments,
            created_at=created_at,
            updated_at=updated_at
        )

        post_id_ref = await postTable.insert_one(post_instance.dict())
        new_post = await postTable.find_one({"_id": post_id_ref.inserted_id}) 

        return response(status_code=200, message="Posted uploaded!", data=post_serializer(new_post))
    except Exception as e:
        return response(status_code=500, message=str(e))
    

@router.get('/posts', response_description="Get all user's posts plus that of of the users he/she follows")
async def get_posts(
    current_user: UserProfile=Depends(oauth2.get_current_user),
    page: int=Query(default=1, description='Page number to fatch', ge=1),
    limit: int=Query(default=10, description='Number of documents per page', le=100)
):
    try:
        followings = current_user['followings']

        users_id_list = [following.get('user_id') for following in followings]
        users_id_list.append(current_user['id'])

        posts = await postTable.find({'user.user_id': {"$in": users_id_list}}).skip((page - 1) * limit).limit(limit).to_list(limit)
        if not posts: 
            return response(status_code=404, message="No post found!")
        
        #total_count = len(posts)
        total_count = await postTable.count_documents({'user.user_id': {"$in": users_id_list}})
        
        res = {
            "data": [post_serializer(post) for post in posts],
            "page": page,
            "limit": limit,
            "total_related_posts": total_count
        }

        return response(status_code=200, message="User related posts fetched!", data=res)
    except Exception as e:
        return response(status_code=500, message=str(e))
        

@router.delete("/post/{post_id}")
async def delete_post(post_id: str, current_user: dict=Depends(oauth2.get_current_user)):
    try:
        post = await postTable.find_one({'_id': ObjectId(post_id)})
        if not post:
            return response(status_code=404, message="Post not found!")
        
        if post['user']['user_id'] != current_user['id']:
            return response(status_code=442, message="This post does not belong to this user!")

        deleted_media = await media_deletion(post['content']["public_id"])
        if deleted_media:
            await postTable.delete_one({'_id': ObjectId(post_id)})
            return response(status_code=200, message="Post file deleted!")
        else:
            return response(status_code=500, message="Failed to delete media")
    except Exception as e:
        return response(status_code=500, message=str(e))

        
    