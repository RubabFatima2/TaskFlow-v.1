from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re


class UserRegister(BaseModel):
    """Request schema for user registration"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password has minimum complexity requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """Request schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response schema for user data (no password)"""
    id: int
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
