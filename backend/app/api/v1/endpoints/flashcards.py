"""Flashcard endpoints"""

from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.flashcard import Flashcard
from app.schemas.flashcard import FlashcardCreate, FlashcardResponse, FlashcardReview
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[FlashcardResponse])
async def get_flashcards(
    course_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all flashcards for current user"""
    query = select(Flashcard).where(Flashcard.user_id == current_user.id)
    
    if course_id:
        query = query.where(Flashcard.course_id == course_id)
    
    result = await db.execute(query)
    flashcards = result.scalars().all()
    return flashcards


@router.get("/due", response_model=List[FlashcardResponse])
async def get_due_flashcards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get flashcards due for review"""
    result = await db.execute(
        select(Flashcard).where(
            Flashcard.user_id == current_user.id,
            Flashcard.next_review <= datetime.utcnow()
        ).order_by(Flashcard.next_review)
    )
    flashcards = result.scalars().all()
    return flashcards


@router.post("/", response_model=FlashcardResponse)
async def create_flashcard(
    flashcard_data: FlashcardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new flashcard"""
    flashcard = Flashcard(
        user_id=current_user.id,
        course_id=flashcard_data.course_id,
        front=flashcard_data.front,
        back=flashcard_data.back,
        source_file=flashcard_data.source_file
    )
    
    db.add(flashcard)
    await db.commit()
    await db.refresh(flashcard)
    
    return flashcard


@router.post("/{flashcard_id}/review", response_model=FlashcardResponse)
async def review_flashcard(
    flashcard_id: str,
    review: FlashcardReview,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Review flashcard using SM-2 algorithm"""
    
    result = await db.execute(
        select(Flashcard).where(
            Flashcard.id == flashcard_id,
            Flashcard.user_id == current_user.id
        )
    )
    flashcard = result.scalar_one_or_none()
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    # SM-2 Algorithm
    quality = review.quality  # 0-5
    
    if quality >= 3:
        # Correct response
        if flashcard.repetitions == 0:
            flashcard.interval = 1
        elif flashcard.repetitions == 1:
            flashcard.interval = 6
        else:
            flashcard.interval = int(flashcard.interval * flashcard.easiness_factor)
        
        flashcard.repetitions += 1
        flashcard.correct_reviews += 1
    else:
        # Incorrect response - reset
        flashcard.repetitions = 0
        flashcard.interval = 1
    
    # Update easiness factor
    flashcard.easiness_factor = max(
        1.3,
        flashcard.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    )
    
    # Set next review date
    flashcard.next_review = datetime.utcnow() + timedelta(days=flashcard.interval)
    flashcard.last_reviewed = datetime.utcnow()
    flashcard.total_reviews += 1
    
    await db.commit()
    await db.refresh(flashcard)
    
    # Award points to user
    current_user.points += 5 if quality >= 3 else 2
    current_user.last_activity = datetime.utcnow()
    await db.commit()
    
    return flashcard


@router.delete("/{flashcard_id}")
async def delete_flashcard(
    flashcard_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete flashcard"""
    
    result = await db.execute(
        select(Flashcard).where(
            Flashcard.id == flashcard_id,
            Flashcard.user_id == current_user.id
        )
    )
    flashcard = result.scalar_one_or_none()
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    await db.delete(flashcard)
    await db.commit()
    
    return {"message": "Flashcard deleted successfully"}
