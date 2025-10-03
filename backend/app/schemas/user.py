"""User schemas"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: str  # Changed from EmailStr to allow moodle.local emails


class UserCreate(UserBase):
    """User creation schema"""
    moodle_token: str


class UserLogin(BaseModel):
    """User login schema"""
    moodle_token: str


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    points: int
    streak_days: int
    last_activity: datetime | None
    created_at: datetime
    last_login: datetime | None
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics"""
    total_flashcards: int
    flashcards_due: int
    focus_sessions_today: int
    total_focus_minutes: int
    current_streak: int
    total_points: int
