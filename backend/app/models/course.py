"""Course model"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Course(Base):
    """Course model"""
    __tablename__ = "courses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Moodle data
    moodle_course_id = Column(Integer, nullable=False, index=True)
    fullname = Column(String(500), nullable=False)
    shortname = Column(String(255), nullable=False)
    summary = Column(Text)
    
    # Sync settings
    sync_enabled = Column(Boolean, default=True)
    last_synced = Column(DateTime)
    sync_status = Column(String(50), default="pending")  # pending, syncing, completed, error
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="courses")
    flashcards = relationship("Flashcard", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course {self.shortname}>"
