# path: backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")

class UserCreate(UserBase):
    """DTO cho đăng ký tài khoản - AC 2.1.1"""
    password: str = Field(..., min_length=12) # Validator sẽ check chữ hoa/thường/số ở tầng service

class UserUpdate(BaseModel):
    username: Optional[str] = None
    status: Optional[str] = None
    mfa_enabled: Optional[bool] = None

class UserResponse(UserBase):
    """DTO trả về cho Client"""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    status: str
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    roles: List[str] = [] # Flatten role names for UI
