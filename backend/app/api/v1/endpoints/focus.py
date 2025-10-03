"""Focus Mode endpoints"""

from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.focus import FocusSession
from app.api.deps import get_current_user

router = APIRouter()


class FocusSessionCreate(BaseModel):
    duration_minutes: int
    ambient_sound: str | None = None


class FocusSessionResponse(BaseModel):
    id: str
    duration_minutes: int
    ambient_sound: str | None
    started_at: datetime
    completed_at: datetime | None
    completed: bool
    
    class Config:
        from_attributes = True


class FocusStats(BaseModel):
    total_sessions: int
    total_minutes: int
    sessions_today: int
    minutes_today: int
    current_streak: int


@router.post("/sessions", response_model=FocusSessionResponse)
async def start_focus_session(
    session_data: FocusSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new focus session"""
    
    session = FocusSession(
        user_id=current_user.id,
        duration_minutes=session_data.duration_minutes,
        ambient_sound=session_data.ambient_sound
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session


@router.patch("/sessions/{session_id}/complete", response_model=FocusSessionResponse)
async def complete_focus_session(
    session_id: str,
    interrupted: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete a focus session"""
    
    result = await db.execute(
        select(FocusSession).where(
            FocusSession.id == session_id,
            FocusSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.completed_at = datetime.utcnow()
    session.completed = not interrupted
    session.interrupted = interrupted
    
    # Award points
    if not interrupted:
        points = session.duration_minutes // 5  # 1 point per 5 minutes
        current_user.points += points
        current_user.last_activity = datetime.utcnow()
    
    await db.commit()
    await db.refresh(session)
    
    return session


@router.get("/sessions", response_model=List[FocusSessionResponse])
async def get_focus_sessions(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get focus session history"""
    
    result = await db.execute(
        select(FocusSession)
        .where(FocusSession.user_id == current_user.id)
        .order_by(FocusSession.started_at.desc())
        .limit(limit)
    )
    sessions = result.scalars().all()
    return sessions


@router.get("/stats", response_model=FocusStats)
async def get_focus_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get focus session statistics"""
    
    # Total stats
    total_result = await db.execute(
        select(
            func.count(FocusSession.id),
            func.sum(FocusSession.duration_minutes)
        ).where(
            FocusSession.user_id == current_user.id,
            FocusSession.completed == True
        )
    )
    total_sessions, total_minutes = total_result.one()
    
    # Today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(
            func.count(FocusSession.id),
            func.sum(FocusSession.duration_minutes)
        ).where(
            FocusSession.user_id == current_user.id,
            FocusSession.completed == True,
            FocusSession.started_at >= today_start
        )
    )
    sessions_today, minutes_today = today_result.one()
    
    return FocusStats(
        total_sessions=total_sessions or 0,
        total_minutes=total_minutes or 0,
        sessions_today=sessions_today or 0,
        minutes_today=minutes_today or 0,
        current_streak=current_user.streak_days
    )
