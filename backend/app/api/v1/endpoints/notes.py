"""Brain Dump notes endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.note import Note
from app.api.deps import get_current_user

router = APIRouter()


class NoteCreate(BaseModel):
    title: str | None = None
    content: str
    note_type: str = "thought"
    tags: List[str] = []
    color: str = "default"


class NoteResponse(BaseModel):
    id: str
    title: str | None
    content: str
    note_type: str
    tags: List[str]
    color: str
    audio_url: str | None
    transcription: str | None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    note_type: str | None = None,
    tag: str | None = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all notes for current user"""
    query = select(Note).where(Note.user_id == current_user.id)
    
    if note_type:
        query = query.where(Note.note_type == note_type)
    
    if tag:
        query = query.where(Note.tags.contains([tag]))
    
    query = query.order_by(Note.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    notes = result.scalars().all()
    return notes


@router.post("/", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new note"""
    
    note = Note(
        user_id=current_user.id,
        title=note_data.title,
        content=note_data.content,
        note_type=note_data.note_type,
        tags=note_data.tags,
        color=note_data.color
    )
    
    db.add(note)
    await db.commit()
    await db.refresh(note)
    
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a note"""
    
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    note.title = note_data.title
    note.content = note_data.content
    note.note_type = note_data.note_type
    note.tags = note_data.tags
    note.color = note_data.color
    
    await db.commit()
    await db.refresh(note)
    
    return note


@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a note"""
    
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    await db.delete(note)
    await db.commit()
    
    return {"message": "Note deleted successfully"}


@router.get("/search")
async def search_notes(
    q: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search notes by content"""
    
    result = await db.execute(
        select(Note).where(
            Note.user_id == current_user.id,
            Note.content.ilike(f"%{q}%")
        ).order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()
    return notes
