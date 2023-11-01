from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.db import db
from app.schema import Message
from datetime import datetime
from app.utils.response_utils import response
from typing import Dict

router = APIRouter(
    tags=['Messages']
)

messageTable = db['messages']

active_connections: Dict[str, WebSocket] = {}

def add_connection(user_id: str, websocket: WebSocket):
    active_connections[user_id] = websocket

def remove_connection(user_id: str):
    del active_connections[user_id]

async def send_message(websocket: WebSocket, message: Message):
    await websocket.send_text(message)

async def broadcast_message(user_id: str, message: Message):
    for connection_id, websocket in active_connections.items():
        if connection_id != user_id:
            await send_message(websocket, message)

async def handle_disconnect(user_id: str):
    if user_id in active_connections:
        remove_connection(user_id)

async def store_message(sender_id: str, reciever_id: str, content: str):
    try:
        message = Message(
            sender_id=sender_id,
            reciever_id=reciever_id,
            content=content,
            datetime=datetime.utcnow()
        )

        await messageTable.insert_one(message.dict())
    except Exception as e:
        return response(status_code=500, message=str(e))
    

async def get_messages(user_id1: str, user_id2: str) -> List[Message]:
    try:
        messages = await messageTable.find({
            '$or': [
                {'sender_id': user_id1, 'receiver_id': user_id2},
                {'sender_id': user_id2, 'receiver_id': user_id1},
            ]
        }).sort('sent_at', 1).to_list(50)

        return messages
    except Exception as e:
        return response(status_code=500, message=str(e))
    
@router.websocket('/ws/{sender_id}')
async def websocket_endpoint(websocket: WebSocket, sender_id: str):
    await websocket.accept()

    add_connection(sender_id, websocket)
    print('Connection added!')
    for connection_id, websocket in active_connections.items():
        print(f"{connection_id}: {websocket}")
        
    try:
        while True:
            data = await websocket.receive_text()

            """message_content = data"""
            
            """message = Message(
                sender_id=sender_id,
                receiver_id="",
                content=message_content,
                datetime=datetime.utcnow()
            )
"""
            # Process incoming messages and broadcast to the pair
            await broadcast_message(sender_id, data)
            # Store messages in the database
            # Handle disconnects
    except WebSocketDisconnect:
        handle_disconnect(sender_id)

    