# StudyMaster Architecture Documentation

## System Overview

StudyMaster is a full-stack AI-enhanced learning platform that integrates with Moodle to provide intelligent study tools, gamified accountability, and real-time collaboration features.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │ Smart    │  │  Focus   │  │ Campus   │       │
│  │          │  │ Study    │  │  Mode    │  │Underground│       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │              │              │
│       └─────────────┴──────────────┴──────────────┘              │
│                          │                                        │
│                    TanStack Query                                │
│                          │                                        │
└──────────────────────────┼────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │   Nginx     │
                    │ (Reverse    │
                    │  Proxy)     │
                    └──────┬──────┘
                           │
┌──────────────────────────┼────────────────────────────────────────┐
│                    FastAPI Backend                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    API Routes                                │ │
│  │  /api/auth  /api/courses  /api/flashcards  /api/social     │ │
│  └────────────────────┬────────────────────────────────────────┘ │
│                       │                                           │
│  ┌────────────────────┴────────────────────────────────────────┐ │
│  │              Business Logic Layer                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │ Moodle   │  │   AI     │  │  Social  │  │  Points  │  │ │
│  │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └────────────────────┬────────────────────────────────────────┘ │
│                       │                                           │
│  ┌────────────────────┴────────────────────────────────────────┐ │
│  │                Data Access Layer                            │ │
│  │              (SQLAlchemy Async)                             │ │
│  └────────────────────┬────────────────────────────────────────┘ │
└───────────────────────┼───────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │PostgreSQL│    │  Redis  │    │   S3    │
   │         │    │ Cache/  │    │  File   │
   │         │    │ Session │    │ Storage │
   └─────────┘    └─────────┘    └─────────┘
```

## Component Details

### Frontend Architecture

#### Technology Stack
- **React 18.2+**: Component-based UI
- **TypeScript**: Type safety
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Accessible components
- **Zustand**: State management
- **TanStack Query**: Server state
- **React Router v6**: Client-side routing
- **Socket.IO Client**: Real-time updates

#### Folder Structure
```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── flashcards/      # Flashcard components
│   │   ├── focus/           # Focus mode components
│   │   ├── social/          # Social features
│   │   └── common/          # Shared components
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── SmartStudy.tsx
│   │   ├── FocusMode.tsx
│   │   ├── CampusUnderground.tsx
│   │   ├── LiveSync.tsx
│   │   ├── Accountability.tsx
│   │   └── BrainDump.tsx
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── socket.ts        # WebSocket client
│   │   ├── utils.ts         # Utilities
│   │   └── constants.ts     # Constants
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useCourses.ts
│   │   ├── useFlashcards.ts
│   │   └── useWebSocket.ts
│   ├── stores/
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── syncStore.ts
│   ├── types/
│   │   ├── api.ts
│   │   ├── models.ts
│   │   └── index.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

### Backend Architecture

#### Technology Stack
- **FastAPI**: Async web framework
- **SQLAlchemy 1.4**: ORM with async support
- **PostgreSQL**: Primary database
- **Redis**: Caching and sessions
- **Celery**: Task queue
- **APScheduler**: Cron jobs
- **Socket.IO**: WebSocket server

#### Folder Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── courses.py
│   │   │   │   ├── flashcards.py
│   │   │   │   ├── focus.py
│   │   │   │   ├── social.py
│   │   │   │   └── notes.py
│   │   │   └── api.py
│   │   └── deps.py          # Dependencies
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── security.py      # Auth & encryption
│   │   └── cache.py         # Redis cache
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── flashcard.py
│   │   ├── social.py
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── flashcard.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── moodle.py        # Moodle API client
│   │   ├── ai.py            # AI/GPT services
│   │   ├── flashcard.py     # Flashcard logic
│   │   ├── social.py        # Social features
│   │   ├── points.py        # Gamification
│   │   └── pdf.py           # PDF processing
│   ├── tasks/
│   │   ├── celery_app.py
│   │   ├── sync.py          # Moodle sync tasks
│   │   └── decay.py         # Points decay
│   ├── websocket/
│   │   ├── manager.py
│   │   └── handlers.py
│   ├── utils/
│   │   ├── encryption.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── api/
│   ├── services/
│   └── conftest.py
├── requirements.txt
└── Dockerfile
```

## Data Models

### Core Models

#### User
```python
class User(Base):
    id: UUID
    username: str
    email: str
    encrypted_token: str  # Moodle API token
    created_at: datetime
    last_login: datetime
    points: int
    streak_days: int
```

#### Course
```python
class Course(Base):
    id: int  # Moodle course ID
    user_id: UUID
    fullname: str
    shortname: str
    last_synced: datetime
    sync_enabled: bool
```

#### Flashcard
```python
class Flashcard(Base):
    id: UUID
    user_id: UUID
    course_id: int
    front: str
    back: str
    difficulty: int  # SM-2 difficulty
    next_review: datetime
    interval: int
    repetitions: int
```

#### FocusSession
```python
class FocusSession(Base):
    id: UUID
    user_id: UUID
    duration_minutes: int
    started_at: datetime
    completed: bool
    ambient_sound: str
```

#### StudyGroup
```python
class StudyGroup(Base):
    id: UUID
    name: str
    course_id: int
    created_by: UUID
    member_count: int
    next_session: datetime
```

## API Design

### RESTful Endpoints

#### Authentication
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
POST   /api/v1/auth/refresh
```

#### Courses
```
GET    /api/v1/courses
GET    /api/v1/courses/{id}
POST   /api/v1/courses/sync
GET    /api/v1/courses/{id}/materials
```

#### Flashcards
```
GET    /api/v1/flashcards
POST   /api/v1/flashcards
GET    /api/v1/flashcards/due
POST   /api/v1/flashcards/{id}/review
POST   /api/v1/flashcards/generate
```

#### Focus Mode
```
POST   /api/v1/focus/sessions
GET    /api/v1/focus/sessions
GET    /api/v1/focus/stats
```

#### Social
```
GET    /api/v1/social/groups
POST   /api/v1/social/groups
GET    /api/v1/social/buddies
POST   /api/v1/social/resources
```

### WebSocket Events

#### Sync Updates
```javascript
// Client → Server
socket.emit('sync:start', { courseId })

// Server → Client
socket.on('sync:progress', { progress, status })
socket.on('sync:complete', { newItems })
```

#### Leaderboard
```javascript
// Server → Client (broadcast)
socket.on('leaderboard:update', { rankings })
```

## Security Architecture

### Token Encryption
```python
from cryptography.fernet import Fernet

# Encrypt Moodle API token
cipher = Fernet(settings.ENCRYPTION_KEY)
encrypted_token = cipher.encrypt(token.encode())
```

### JWT Authentication
```python
# Access token: 15 minutes
# Refresh token: 7 days
# Stored in httpOnly cookies
```

### Rate Limiting
```python
@limiter.limit("10/minute")
async def expensive_endpoint():
    pass
```

## Caching Strategy

### Redis Cache Layers

#### L1: API Response Cache
```python
@cache(expire=300)  # 5 minutes
async def get_courses():
    pass
```

#### L2: Computed Data Cache
```python
# Leaderboard: 1 hour
# Course materials: 30 minutes
# User stats: 5 minutes
```

#### L3: Session Cache
```python
# WebSocket sessions
# User preferences
```

## Background Tasks

### Celery Tasks

#### Moodle Sync (Every 30 minutes)
```python
@celery_app.task
def sync_moodle_courses(user_id):
    # Fetch new materials
    # Process PDFs
    # Generate flashcards
    # Send notifications
```

#### Points Decay (Daily at midnight)
```python
@celery_app.task
def decay_points():
    # Apply decay formula
    # Update leaderboard
```

### APScheduler Jobs
```python
scheduler.add_job(
    sync_all_users,
    'interval',
    minutes=30
)
```

## File Storage

### S3 Structure
```
s3://studymaster/
├── users/{user_id}/
│   ├── pdfs/
│   ├── audio/
│   └── notes/
└── shared/
    └── resources/
```

## Performance Optimization

### Database
- Connection pooling (20-50 connections)
- Indexed queries on frequently accessed fields
- Materialized views for leaderboards
- Query result caching

### API
- Response compression (gzip)
- HTTP/2 support
- CDN for static assets
- Lazy loading for large datasets

### Frontend
- Code splitting
- Image optimization
- Service worker caching
- Debounced API calls

## Monitoring & Logging

### Structured Logging
```python
logger.info(
    "moodle_sync_completed",
    extra={
        "user_id": user_id,
        "duration_ms": duration,
        "items_synced": count
    }
)
```

### Metrics
- API response times
- WebSocket connections
- Cache hit rates
- Task queue length
- Database query performance

## Deployment

### Docker Compose (Development)
```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  
  postgres:
    image: postgres:13
  
  redis:
    image: redis:7
  
  celery:
    build: ./backend
    command: celery worker
```

### Production (Kubernetes/Docker Swarm)
- Load balanced FastAPI instances
- Redis cluster
- PostgreSQL with replication
- S3 for file storage
- Nginx ingress
