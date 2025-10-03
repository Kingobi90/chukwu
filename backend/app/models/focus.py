"""Focus Mode session model"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class FocusSession(Base):
    """Focus Mode Pomodoro session"""
    __tablename__ = "focus_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Session details
    duration_minutes = Column(Integer, nullable=False)  # 25, 50, 15, 5
    ambient_sound = Column(String(100))  # white_noise, rain, lofi, silence
    
    # Status
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    completed = Column(Boolean, default=False)
    interrupted = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="focus_sessions")
    
    def __repr__(self):
        return f"<FocusSession {self.id} - {self.duration_minutes}min>"
