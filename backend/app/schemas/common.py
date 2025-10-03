"""Common Pydantic schemas"""

from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Message(BaseModel):
    """Generic message response"""
    message: str
    detail: str | None = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = 0
    limit: int = 100
