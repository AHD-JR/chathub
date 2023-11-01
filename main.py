from fastapi import FastAPI, WebSocket
from app.db import client
import os
from dotenv import load_dotenv
from app.utils.cloudinary import configure_cloudinary
from app.api.user import router as user_router
from app.api.status import router as status_router
from app.api.auth import router as login_router
from app.api.post import router as post_router
from app.api.comment import router as comment_router
from app.api.message import router as message_router
from fastapi.responses import HTMLResponse
from test_webscoket_connection import html

app = FastAPI()

load_dotenv()

try:
    client.server_info()
    print("Connected to MongoDB 🚀")
except:
    print('Could not connect to MongoDB!')

try:
    configure_cloudinary()
    print("Cloudinary Configured 🚀")
except:
    print('Could not configure Cloudinary!')

port = os.environ.get('PORT')

@app.get('/')
def get_root():
    return {'msg': f'This server is off and running on port {port}...'}

"""@app.get("/ws")
async def get():
    return HTMLResponse(html)"""

app.include_router(login_router)
app.include_router(user_router)
app.include_router(status_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(message_router)

