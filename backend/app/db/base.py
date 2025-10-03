"""Database base configuration"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic - done at the end to avoid circular imports
def import_models():
    from app.models import user, course, flashcard, focus, social, note  # noqa
