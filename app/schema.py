from pydantic import BaseModel, constr, Field
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum

class User(BaseModel):
    user_id: str
    username: str

class UserCredentials(BaseModel):
    username: str = Field(..., description='What do you uniquely want to be called on this platform?', min_length=5, max_length=15)
    password: constr(min_length=6, max_length=20)

class UserProfile(BaseModel):
    name: str = Field(..., description='Help people descover you by using the name that you are known by', min_length=1)
    username: str = Field(..., description='What do you uniquely want to be called on this platform?', min_length=5, max_length=15)
    password: constr(min_length=6, max_length=20)
    phoneNumber: constr(min_length=11, max_length=15)
    email: str
    bio: constr(max_length=200)
    avatar: str
    gender: str
    followers: List[User] = Field(default_factory=list)
    followings: List[User] = Field(default_factory=list)
    links: List[str]

class PrivacyEnum(str, Enum):
    public = "Public"
    private = "Private"
    custom = "Custom"

class Content(BaseModel):
    public_id: str
    secure_url: str

class Status(BaseModel):
    user_id: str
    content: Content
    caption: str
    created_at: datetime = datetime.utcnow()
    expired_at: datetime = datetime.utcnow() + timedelta(hours=24)
    privacy: PrivacyEnum = PrivacyEnum.public
    is_expired: bool = False

class Comment(BaseModel):
    user: User
    post_id: str
    text: str
    created_at: datetime = datetime.utcnow()

class Post(BaseModel):
    user: User
    content: Content
    caption: str
    likes: Optional[List[User]]
    comments: Optional[List[Comment]]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class Message(BaseModel):
    sender_id: str
    receiver_id: str
    text: str
    created_at: datetime = datetime.utcnow()

class Notification(BaseModel):
    user_id: str 
    message: str
    created_at: datetime = datetime.utcnow()
    is_read: bool = False
