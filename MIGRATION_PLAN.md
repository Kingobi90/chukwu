# StudyMaster Migration Plan: Flask → FastAPI + React

## Current State Analysis
- **Backend**: Flask 2.2.2 with synchronous request handling
- **Frontend**: Jinja2 templates with Bootstrap 5
- **Database**: SQLite (via pdf_summarizer.py)
- **Features**: Basic Moodle sync, PDF summarization, grades viewing
- **Missing**: Real-time sync, WebSockets, caching, modern React UI, gamification

## Migration Strategy

### Phase 1: Backend Infrastructure (Week 1-2)
**Goal**: Migrate from Flask to FastAPI with async support

#### 1.1 Core Backend Setup
- [ ] Create FastAPI application structure
- [ ] Set up SQLAlchemy 1.4 with async support
- [ ] Configure PostgreSQL connection (with SQLite fallback for dev)
- [ ] Implement Alembic migrations
- [ ] Add Redis for caching and session management

#### 1.2 Authentication & Security
- [ ] Implement OAuth token encryption with Fernet
- [ ] Create JWT-based session management
- [ ] Add rate limiting with FastAPI-Limiter
- [ ] Set up CORS for React frontend
- [ ] Implement Pydantic models for input validation

#### 1.3 Moodle Client Modernization
- [ ] Replace `requests` with `httpx` for async support
- [ ] Add connection pooling
- [ ] Implement smart caching with Redis
- [ ] Add retry logic with exponential backoff
- [ ] Create background task scheduler with APScheduler

### Phase 2: Database & Models (Week 2-3)
**Goal**: Design and implement comprehensive data models

#### 2.1 Core Models
```python
# users, courses, materials, modules, files
# flashcards, focus_sessions, notes
# groups, buddies, resources, achievements
# leaderboard_entries, challenges
```

#### 2.2 Migration Scripts
- [ ] Create initial schema migration
- [ ] Migrate existing SQLite data to PostgreSQL
- [ ] Set up indexes for performance
- [ ] Implement full-text search for notes

### Phase 3: API Endpoints (Week 3-4)
**Goal**: Build RESTful API with WebSocket support

#### 3.1 Core Endpoints
- [ ] `/api/auth/*` - Authentication
- [ ] `/api/courses/*` - Course management
- [ ] `/api/materials/*` - Material sync
- [ ] `/api/flashcards/*` - Smart Study
- [ ] `/api/focus/*` - Focus Mode sessions
- [ ] `/api/social/*` - Campus Underground
- [ ] `/api/notes/*` - Brain Dump

#### 3.2 WebSocket Endpoints
- [ ] `/ws/sync` - Real-time Moodle sync updates
- [ ] `/ws/leaderboard` - Live leaderboard updates
- [ ] `/ws/notifications` - Push notifications

### Phase 4: Frontend Setup (Week 4-5)
**Goal**: Create modern React application

#### 4.1 Project Setup
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @tanstack/react-query zustand react-router-dom
npm install tailwindcss postcss autoprefixer
npm install socket.io-client axios
npm install @radix-ui/react-* # shadcn/ui components
```

#### 4.2 Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # shadcn/ui components
│   │   ├── flashcards/
│   │   ├── focus/
│   │   └── social/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── SmartStudy.tsx
│   │   ├── FocusMode.tsx
│   │   ├── CampusUnderground.tsx
│   │   ├── LiveSync.tsx
│   │   ├── Accountability.tsx
│   │   └── BrainDump.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── socket.ts
│   │   └── utils.ts
│   ├── hooks/
│   ├── stores/
│   └── types/
```

### Phase 5: Feature Implementation (Week 5-8)

#### 5.1 Smart Study System
- [ ] Flashcard generation with GPT API
- [ ] SM-2 spaced repetition algorithm
- [ ] Active recall audio with TTS
- [ ] Audio player with bookmarks
- [ ] Progress tracking

#### 5.2 Live Class Sync
- [ ] APScheduler for 30-min polling
- [ ] Celery task queue for processing
- [ ] PDF summarization pipeline
- [ ] File categorization
- [ ] Real-time sync dashboard

#### 5.3 Focus Mode
- [ ] Pomodoro timer component
- [ ] Ambient sound selection
- [ ] Session tracking
- [ ] Fullscreen mode
- [ ] Statistics dashboard

#### 5.4 Accountability Circle
- [ ] Points system backend
- [ ] Daily decay cron job
- [ ] Leaderboard with window functions
- [ ] Achievement system
- [ ] WebSocket live updates

#### 5.5 Campus Underground
- [ ] Study groups CRUD
- [ ] Buddy matching algorithm
- [ ] File sharing with S3
- [ ] Real-time messaging
- [ ] Resource marketplace

#### 5.6 Brain Dump
- [ ] Markdown editor with autosave
- [ ] Voice memo recording
- [ ] Whisper transcription
- [ ] Full-text search
- [ ] Tag system

### Phase 6: AI Integration (Week 8-9)
**Goal**: Integrate OpenAI and Langchain

#### 6.1 PDF Processing
- [ ] PyPDF2 text extraction
- [ ] Token chunking (3000 max)
- [ ] GPT summarization with retry
- [ ] Langchain integration
- [ ] Dual-pane viewer

#### 6.2 Flashcard Generation
- [ ] NLP-based extraction
- [ ] GPT card generation
- [ ] Quality scoring
- [ ] Batch processing

### Phase 7: Deployment (Week 9-10)
**Goal**: Production-ready deployment

#### 7.1 Containerization
```dockerfile
# Backend Dockerfile
# Frontend Dockerfile
# docker-compose.yml
```

#### 7.2 Infrastructure
- [ ] Nginx reverse proxy
- [ ] Gunicorn with workers
- [ ] Redis PubSub for WebSockets
- [ ] PostgreSQL with backups
- [ ] S3 for file storage

#### 7.3 CI/CD
- [ ] GitHub Actions pipeline
- [ ] Pytest + Playwright tests
- [ ] Automated deployments
- [ ] Log aggregation

### Phase 8: Testing & Optimization (Week 10-11)
- [ ] Unit tests with pytest
- [ ] Integration tests
- [ ] E2E tests with Playwright
- [ ] Performance optimization
- [ ] Security audit

## Technology Stack Summary

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 13+ (SQLite fallback)
- **ORM**: SQLAlchemy 1.4 (async)
- **Cache**: Redis 7+
- **Tasks**: Celery + APScheduler
- **AI**: OpenAI API, Langchain
- **PDF**: PyPDF2
- **Auth**: Fernet encryption, JWT

### Frontend
- **Framework**: React 18.2+
- **Language**: TypeScript 5+
- **Build**: Vite 5+
- **Styling**: Tailwind CSS 3.4+
- **Components**: shadcn/ui
- **State**: Zustand
- **Data**: TanStack Query
- **Router**: React Router v6
- **WebSocket**: Socket.IO Client

### DevOps
- **Container**: Docker + Docker Compose
- **Server**: Gunicorn + Nginx
- **CI/CD**: GitHub Actions
- **Testing**: pytest, Playwright
- **Monitoring**: Logs + observability

## Migration Checklist

### Pre-Migration
- [ ] Backup existing SQLite database
- [ ] Document current API endpoints
- [ ] Export user data
- [ ] Set up development environment

### During Migration
- [ ] Run both systems in parallel
- [ ] Gradual feature migration
- [ ] Data migration scripts
- [ ] User testing

### Post-Migration
- [ ] Performance benchmarking
- [ ] Security audit
- [ ] Documentation update
- [ ] User training

## Risk Mitigation
1. **Data Loss**: Automated backups, migration scripts with rollback
2. **Downtime**: Parallel deployment, gradual cutover
3. **Performance**: Load testing, caching strategy
4. **Security**: Penetration testing, code review

## Success Metrics
- API response time < 200ms (p95)
- WebSocket latency < 50ms
- Frontend load time < 2s
- Test coverage > 80%
- Zero data loss during migration

## Next Steps
1. Review and approve migration plan
2. Set up development environment
3. Begin Phase 1 implementation
4. Weekly progress reviews
