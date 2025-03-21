from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    password: str
    email: EmailStr
    full_name: str
    firebase_uid: str

class UserUpdate(UserBase):
    pass

class UserInDB(UserBase):
    id: int
    firebase_uid: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class User(UserInDB):
    pass

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    firebase_uid: str
    token: str 