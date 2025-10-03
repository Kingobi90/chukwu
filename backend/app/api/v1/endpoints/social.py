"""Social features endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.social import StudyGroup, SharedResource
from app.api.deps import get_current_user

router = APIRouter()


class StudyGroupCreate(BaseModel):
    name: str
    description: str | None = None
    moodle_course_id: int | None = None
    max_members: int = 10


class StudyGroupResponse(BaseModel):
    id: str
    name: str
    description: str | None
    moodle_course_id: int | None
    member_count: int
    max_members: int
    
    class Config:
        from_attributes = True


class SharedResourceCreate(BaseModel):
    title: str
    description: str | None = None
    resource_type: str
    file_url: str | None = None
    moodle_course_id: int | None = None


class SharedResourceResponse(BaseModel):
    id: str
    title: str
    description: str | None
    resource_type: str
    file_url: str | None
    downloads: int
    upvotes: int
    
    class Config:
        from_attributes = True


@router.get("/groups", response_model=List[StudyGroupResponse])
async def get_study_groups(
    course_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all study groups"""
    query = select(StudyGroup).where(StudyGroup.is_public == True)
    
    if course_id:
        query = query.where(StudyGroup.moodle_course_id == course_id)
    
    result = await db.execute(query)
    groups = result.scalars().all()
    return groups


@router.post("/groups", response_model=StudyGroupResponse)
async def create_study_group(
    group_data: StudyGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new study group"""
    
    group = StudyGroup(
        name=group_data.name,
        description=group_data.description,
        moodle_course_id=group_data.moodle_course_id,
        max_members=group_data.max_members,
        created_by=current_user.id,
        member_count=1
    )
    
    db.add(group)
    await db.commit()
    await db.refresh(group)
    
    return group


@router.get("/resources", response_model=List[SharedResourceResponse])
async def get_shared_resources(
    course_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Get shared resources"""
    query = select(SharedResource)
    
    if course_id:
        query = query.where(SharedResource.moodle_course_id == course_id)
    
    query = query.order_by(SharedResource.upvotes.desc())
    
    result = await db.execute(query)
    resources = result.scalars().all()
    return resources


@router.post("/resources", response_model=SharedResourceResponse)
async def create_shared_resource(
    resource_data: SharedResourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Share a resource"""
    
    resource = SharedResource(
        user_id=current_user.id,
        title=resource_data.title,
        description=resource_data.description,
        resource_type=resource_data.resource_type,
        file_url=resource_data.file_url,
        moodle_course_id=resource_data.moodle_course_id
    )
    
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    
    # Award points
    current_user.points += 10
    await db.commit()
    
    return resource


@router.post("/resources/{resource_id}/upvote")
async def upvote_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upvote a shared resource"""
    
    result = await db.execute(
        select(SharedResource).where(SharedResource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    resource.upvotes += 1
    await db.commit()
    
    return {"message": "Resource upvoted", "upvotes": resource.upvotes}
