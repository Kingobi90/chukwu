"""Flashcard model with SM-2 spaced repetition"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Flashcard(Base):
    """Flashcard model with SM-2 algorithm"""
    __tablename__ = "flashcards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    # Card content
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    source_file = Column(String(500))  # PDF or material source
    
    # SM-2 Algorithm fields
    easiness_factor = Column(Float, default=2.5)  # EF: 1.3 - 2.5
    interval = Column(Integer, default=1)  # Days until next review
    repetitions = Column(Integer, default=0)  # Number of successful reviews
    next_review = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Statistics
    total_reviews = Column(Integer, default=0)
    correct_reviews = Column(Integer, default=0)
    last_reviewed = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="flashcards")
    course = relationship("Course", back_populates="flashcards")
    
    def __repr__(self):
        return f"<Flashcard {self.id}>"
