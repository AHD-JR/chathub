from fastapi import APIRouter, status, UploadFile, Query, Depends
from app.db import db
from app.schema import UserProfile
from app.serializer import user_serializer
from app.utils.hashing import hash
from app.utils.response_utils import response
from bson import ObjectId
from app.utils.cloudinary import media_upload, media_deletion
from app.utils import oauth2
import asyncio

userTable = db['users']

router = APIRouter(
    tags=['User Profile'],
    prefix='/api'
)

@router.post('/register', response_description='Create a new account on the chat platform', response_model=UserProfile)
async def create_account(req: UserProfile):
    try:
        user = await userTable.find_one({'username': req.username})
        if user:
            return response(status_code=226, message='Username has been taken!')
     
        user_object = req.dict()
        user_object['password'] = hash(user_object['password'])

        user_id_ref = await userTable.insert_one(user_object)
        new_user = await userTable.find_one({'_id': user_id_ref.inserted_id})
        
        return response(status_code=201, message='User account has been created', data=user_serializer(new_user))
    except Exception as e:
        return response(status_code=400, message=str(e))
    

@router.get('/users', response_description="Get all users, senior approach")
async def get_all_users(
    page: int=Query(default=1, description='Page number to fatch', ge=1),
    limit: int=Query(default=10, description='Number of documents per page', le=100),
    current_user: UserProfile = Depends(oauth2.get_current_user)
):
    try:
        users = await userTable.find({}).skip((page - 1) * limit).limit(limit).to_list(limit)

        if not users:
            return response(status_code=404, message="No users found!")
        
        total_count = await userTable.count_documents({})

        res = {
            "data": [user_serializer(user) for user in users],
            "page": page,
            "limit": limit,
            "total": total_count
        }

        return response(status_code=200, message="Users fetched successfully.", data=res)
    except Exception as e:
        return response(status_code=500, message=str(e))


@router.get('/users/{user_id}', response_description="Get user", response_model=UserProfile)
async def get_user(user_id: str, current_user: UserProfile = Depends(oauth2.get_current_user)):
    user = await userTable.find_one({'_id': ObjectId(user_id)})
    if not user:
       return response(status_code=404, message='No such user!')
    
    return response(status_code=200, message="User info fetched!", data=user_serializer(user))


@router.put('/edit_profile/{user_id}')
async def update_profile(user_id: str, req: UserProfile, current_user: UserProfile = Depends(oauth2.get_current_user)):
    try: 
        user = await userTable.find_one({'_id': ObjectId(user_id)})
        if user:
            updated_result = await userTable.update_one({'_id': ObjectId(user_id)}, {'$set': req.dict()})
            if updated_result.modified_count != 0:
                updated_user = await userTable.find_one({'_id': ObjectId(user_id)})
                return response(status_code=200, message="Profile Updated!", data=user_serializer(updated_user))
            else:
                return response(status_code=400, message="Not updated, Unable to update profile")
        else:
            return response(status_code=404, message="User not found!")
    except Exception as e:
        return response(status_code=400, message=str(e))
    
    
@router.delete('/user/{user_id}')
async def delete_user(user_id, current_user: UserProfile = Depends(oauth2.get_current_user)):
    try:
        user = await userTable.find_one({'_id': ObjectId(user_id)})
        if not user:
            return response(status_code=404, message="USer not found!")
        
        await userTable.delete_one({"_id": ObjectId(user_id)})

        return response(status_code=200, message="User deleted", data=user_serializer(user))
    except Exception as e:
        return response(status_code=400, message=str(e))


@router.post('/profile_photo')
async def upload_profile_photo(photo: UploadFile, current_user: UserProfile = Depends(oauth2.get_current_user)):
    return await media_upload(photo)


@router.delete('/profile_photo')
async def remove_profile_photo(public_id: str, current_user: UserProfile = Depends(oauth2.get_current_user)):
   return await media_deletion(public_id=public_id)


@router.put('/follow')
async def follow_user(user_id: str, current_user: dict = Depends(oauth2.get_current_user)):
    try:
        target_user = await userTable.find_one({'_id': ObjectId(user_id)})
        if not target_user:
            return response(status_code=404, message="User does not exist!")
        
        target_user = user_serializer(target_user)

        if target_user['id'] == current_user['id']:
            return response(status_code=400, message="You can't follow yourself!")
        
        followers_list = target_user['followers']
        followings_list = current_user['followings']

        if any(follower.get('user_id') == current_user['id'] for follower in followers_list):
            return response(status_code=226, message="You are already following this account")
        
        follower =  {
            "user_id": current_user['id'],
            "username": current_user['username']
        }
        following = {
            "user_id": target_user['id'],
            "username": target_user['username']
        }

        followers_list.append(follower)
        followings_list.append(following)

        target_user_data = {key: value for key, value in target_user.items() if key != "id"}
        current_user_data = {key: value for key, value in current_user.items() if key != "id"}

        await asyncio.gather(
            userTable.update_one({"_id": ObjectId(current_user['id'])}, {'$set': current_user_data}),
            userTable.update_one({"_id": ObjectId(target_user['id'])}, {'$set': target_user_data})
        )
        
        updated_current_user = await userTable.find_one({'_id': ObjectId(current_user['id'])})
        updated_target_user = await userTable.find_one({'_id': ObjectId(target_user['id'])})
        
        res = {
            "dower": user_serializer(updated_current_user),
            "gainer": user_serializer(updated_target_user)
        }

        return response(status_code=200, message=f"{current_user['username']} followed {target_user['username']}!", data=res)
    except Exception as e:
        return response(status_code=500, message=str(e))
    

@router.put('/unfollow')
async def unfollow_user(user_id: str, current_user: UserProfile = Depends(oauth2.get_current_user)):
    try:
        target_user = await userTable.find_one({'_id': ObjectId(user_id)})
        if not target_user:
            return response(status_code=404, message="User does not exist!")
        
        target_user = user_serializer(target_user)

        if target_user['id'] == current_user['id']:
            return response(status_code=400, message="You can't unfollow yourself!")       
        
        target_user_followers_list = target_user['followers']
        current_user_followings_list = current_user['followings']

        is_following = any(follower.get('user_id') ==  target_user['id'] for follower in current_user_followings_list)

        if is_following:
            target_user_followers_list = [follower for follower in target_user_followers_list if follower['user_id'] != current_user['id']]
            current_user_followings_list = [following for following in current_user_followings_list if following['user_id'] != target_user['id']]

            target_user['followers'] = target_user_followers_list
            current_user['followings'] = current_user_followings_list

            target_user_data = {key: value for key, value in target_user.items() if key != "id"}
            current_user_data = {key: value for key, value in current_user.items() if key != "id"}

            await asyncio.gather(
                userTable.update_one({"_id": ObjectId(current_user['id'])}, {'$set': current_user_data}),
                userTable.update_one({"_id": ObjectId(target_user['id'])}, {'$set': target_user_data})
            )
        
            updated_current_user = await userTable.find_one({'_id': ObjectId(current_user['id'])})
            updated_target_user = await userTable.find_one({'_id': ObjectId(target_user['id'])})
        else:
            return response(status_code=404, message="You are not following this account")
        
        
        res = {
            "dower": user_serializer(updated_current_user),
            "gainer": user_serializer(updated_target_user)
        }

        
        return response(status_code=200, message=f"{current_user['username']} unfollowed {target_user['username']}!", data=res)
    except Exception as e:
        return response(status_code=500, message=str(e))
    
 
        