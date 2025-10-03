"""Social features models"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Table, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

# Association table for study group members
group_members = Table(
    'group_members',
    Base.metadata,
    Column('group_id', UUID(as_uuid=True), ForeignKey('study_groups.id', ondelete="CASCADE")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE")),
    Column('joined_at', DateTime, default=datetime.utcnow)
)


class StudyGroup(Base):
    """Study group model"""
    __tablename__ = "study_groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Course association
    moodle_course_id = Column(Integer, index=True)
    
    # Group settings
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    member_count = Column(Integer, default=0)
    max_members = Column(Integer, default=10)
    is_public = Column(Boolean, default=True)
    
    # Next session
    next_session = Column(DateTime)
    session_location = Column(String(255))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<StudyGroup {self.name}>"


class Buddy(Base):
    """Study buddy relationship"""
    __tablename__ = "buddies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    buddy_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Compatibility score (0-100)
    compatibility_score = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="pending")  # pending, accepted, rejected
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Buddy {self.user_id} -> {self.buddy_id}>"


class SharedResource(Base):
    """Shared study resource"""
    __tablename__ = "shared_resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Resource details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    resource_type = Column(String(50))  # pdf, link, note, video
    file_url = Column(String(1000))
    
    # Course association
    moodle_course_id = Column(Integer, index=True)
    
    # Engagement
    downloads = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SharedResource {self.title}>"
