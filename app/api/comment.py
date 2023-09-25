from fastapi import APIRouter, Depends, status, Query
from app.db import db
from app.schema import Comment
from app.serializer import comment_serializer
from app.utils import oauth2
from app.api.post import postTable
from bson import ObjectId
from app.utils.response_utils import response
from datetime import datetime

router = APIRouter(
    tags=['Comment'],
    prefix='/api'
)

commentTable = db['comment']

@router.post('/comment', response_description='Comment on a post', response_model=Comment)
async def add_comment(
    post_id: str, 
    text: str=Query(min_length=1, max_length=200),
    current_user: dict=Depends(oauth2.get_current_user)    
):
    try:
        post = await postTable.find_one({'_id': ObjectId(post_id)})
        if not post:
            return response(status.HTTP_404_NOT_FOUND, "Post not found!!")
        
        user = {
            "user_id": current_user['id'],
            "username": current_user['username']
        }
        created_at = datetime.utcnow()

        comment_instance = Comment(
            user=user,
            post_id=post_id,
            text= f"@{post['user']['username']} {text}",
            created_at=created_at
        )

        comment_ref = await commentTable.insert_one(comment_instance.dict())
        comment = await commentTable.find_one({'_id': comment_ref.inserted_id})

        return response(status.HTTP_201_CREATED, "Comment sent!", comment_serializer(comment))
    except Exception as e:
        return response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@router.delete('/comment/{comment_id}', response_description="Delete a comment you sent")
async def delete_comment(comment_id: str, current_user: dict=Depends(oauth2.get_current_user)):
    try:
        comment = await commentTable.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            return response(status.HTTP_404_NOT_FOUND, "Comment not found!")
        
        if current_user["id"] != comment['user']['user_id']:
            return response(status.HTTP_401_UNAUTHORIZED, "This comment does not belong to this user!")
        
        await commentTable.delete_one({'_id': ObjectId(comment_id)})
     
        return response(status.HTTP_200_OK, "Comment deleted!", comment_serializer(comment))
    except Exception as e:
        return response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
    

"""@router.put('comment/{comment_id}' response_description='Edit a comment you made')
async def edit_comment(comment_id: str, current_user: dict=Depends(oauth2.get_current_user), ):
     try:
        comment = await postTable.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            return response(status.HTTP_404_NOT_FOUND, "Comment not found!!")
        
        if current_user["id"] != comment['user']['user_id']:
            return response(status.HTTP_401_UNAUTHORIZED, "This comment does not belong to this user!")
        
        user = {
            "user_id": current_user['id'],
            "username": current_user['username']
        }
        created_at = datetime.utcnow()

        comment_instance = Comment(
            user=user,
            post_id=post_id,
            text= f"@{post['user']['username']} {text}",
            created_at=created_at
        )

        comment_ref = await commentTable.insert_one(comment_instance.dict())
        comment = await commentTable.find_one({'_id': comment_ref.inserted_id})

        return response(status.HTTP_201_CREATED, "Comment sent!", comment_serializer(comment))"""