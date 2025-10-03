"""Course endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.course import Course
from app.schemas.course import CourseResponse
from app.api.deps import get_current_user
from app.services.moodle import MoodleService
from app.core.security import decrypt_moodle_token

router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all courses for current user"""
    result = await db.execute(
        select(Course).where(Course.user_id == current_user.id)
    )
    courses = result.scalars().all()
    return courses


@router.post("/sync")
async def sync_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync courses from Moodle"""
    
    # Get Moodle token
    moodle_token = decrypt_moodle_token(current_user.encrypted_moodle_token)
    moodle = MoodleService(token=moodle_token)
    
    try:
        # Fetch courses from Moodle
        moodle_courses = await moodle.get_courses()
        
        synced_count = 0
        for moodle_course in moodle_courses:
            # Check if course exists
            result = await db.execute(
                select(Course).where(
                    Course.user_id == current_user.id,
                    Course.moodle_course_id == moodle_course["id"]
                )
            )
            course = result.scalar_one_or_none()
            
            if not course:
                # Create new course
                course = Course(
                    user_id=current_user.id,
                    moodle_course_id=moodle_course["id"],
                    fullname=moodle_course.get("fullname", ""),
                    shortname=moodle_course.get("shortname", ""),
                    summary=moodle_course.get("summary", "")
                )
                db.add(course)
                synced_count += 1
            else:
                # Update existing course
                course.fullname = moodle_course.get("fullname", course.fullname)
                course.shortname = moodle_course.get("shortname", course.shortname)
                course.summary = moodle_course.get("summary", course.summary)
        
        await db.commit()
        
        return {
            "message": "Courses synced successfully",
            "synced_count": synced_count,
            "total_courses": len(moodle_courses)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync courses: {str(e)}"
        )


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific course"""
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.get("/{course_id}/materials")
async def get_course_materials(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get course materials from Moodle"""
    
    # Verify course ownership
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.user_id == current_user.id
        )
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get Moodle token
    moodle_token = decrypt_moodle_token(current_user.encrypted_moodle_token)
    moodle = MoodleService(token=moodle_token)
    
    try:
        materials = await moodle.get_course_contents(course.moodle_course_id)
        return materials
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch materials: {str(e)}"
        )
