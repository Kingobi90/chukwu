"""Flashcard schemas"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class FlashcardBase(BaseModel):
    """Base flashcard schema"""
    front: str
    back: str


class FlashcardCreate(FlashcardBase):
    """Flashcard creation schema"""
    course_id: UUID
    source_file: str | None = None


class FlashcardResponse(FlashcardBase):
    """Flashcard response schema"""
    id: UUID
    course_id: UUID
    easiness_factor: float
    interval: int
    repetitions: int
    next_review: datetime
    total_reviews: int
    correct_reviews: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FlashcardReview(BaseModel):
    """Flashcard review submission"""
    quality: int  # 0-5 (SM-2 algorithm)


class FlashcardGenerate(BaseModel):
    """Generate flashcards from PDF"""
    course_id: UUID
    file_url: str
    max_cards: int = 20
