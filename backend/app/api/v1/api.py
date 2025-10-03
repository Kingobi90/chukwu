"""API v1 router aggregation"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, courses, flashcards, focus, social, notes

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(focus.router, prefix="/focus", tags=["focus"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
