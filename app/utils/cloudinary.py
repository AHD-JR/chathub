from fastapi import UploadFile, status
import asyncio
from cloudinary.uploader import upload
import cloudinary
import os
from cloudinary import api
from dotenv import load_dotenv
from app.utils.response_utils import response

load_dotenv()

name = os.environ.get('CLOUD_NAME')
key = os.environ.get('CLOUD_API_KEY')
secret = os.environ.get('CLOUD_API_SECRET')
          
def configure_cloudinary():
    cloudinary.config( 
        cloud_name=name, 
        api_key=key, 
        api_secret=secret
    )

# Since cloudinary does not have methods that support asynchronous programming:
# We wrap the synchronous upload function in an asynchronous coroutine
"""async def async_upload(file, folder):
    return await asyncio.to_thread(upload, file, folder=folder)"""

async def media_upload(photo: UploadFile):
    try:
        #We can actually use he asyncio directly!
        res = await asyncio.to_thread(upload, photo.file, folder="profile_photos")
        #res = await async_upload(photo.file, folder="profile_photos")

        public_id = res['public_id']
        secure_url = res['secure_url']
        data = {
            "public_id": public_id,
            "secure_url": secure_url
        }
        
        return data
        #return response(status.HTTP_200_OK, "Photo uploaded successfully!", data)
    except Exception as e:
        return response(status.HTTP_400_BAD_REQUEST, str(e))
    

async def media_deletion(public_id: str):
    try:
        res = await asyncio.to_thread(api.delete_resources, [public_id])

        if res["deleted"][public_id] == "deleted":
            return response(status_code=200, message="Profile photo is removed!")
        else:
            return response(status_code=400, message=f"Failed to delete image {public_id}.")
    except Exception as e:
        return response(status_code=400, message=str(e))
