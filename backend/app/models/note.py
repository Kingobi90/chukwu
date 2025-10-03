"""Brain Dump notes model"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class Note(Base):
    """Brain Dump note model"""
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Content
    title = Column(String(500))
    content = Column(Text, nullable=False)
    note_type = Column(String(50), default="thought")  # thought, study_note, todo, question
    
    # Voice memo
    audio_url = Column(String(1000))
    transcription = Column(Text)
    
    # Organization
    tags = Column(ARRAY(String), default=[])
    color = Column(String(50), default="default")  # for UI color coding
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    
    def __repr__(self):
        return f"<Note {self.title or self.id}>"
