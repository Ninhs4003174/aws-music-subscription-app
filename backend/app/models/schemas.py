from pydantic import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SongQuery(BaseModel):
    artist: Optional[str] = None
    year: Optional[str] = None
    album: Optional[str] = None
    title: Optional[str] = None

class SubscriptionRequest(BaseModel):
    user_email: str
    song_id: str
    title: str
    artist: str
    album: str
    image_url: str