"""Course schemas"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class CourseBase(BaseModel):
    """Base course schema"""
    fullname: str
    shortname: str
    summary: str | None = None


class CourseResponse(CourseBase):
    """Course response schema"""
    id: UUID
    moodle_course_id: int
    sync_enabled: bool
    last_synced: datetime | None
    sync_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CourseSync(BaseModel):
    """Course sync request"""
    course_id: UUID
    force: bool = False


class CourseMaterial(BaseModel):
    """Course material schema"""
    id: int
    name: str
    module_type: str
    file_url: str | None
    file_size: int | None
    created_at: datetime
