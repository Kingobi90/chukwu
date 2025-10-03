# StudyMaster - Production Setup Guide

## What's Been Built

✅ **FastAPI Backend** - Async API with PostgreSQL, Redis, JWT auth  
✅ **React Frontend** - TypeScript, Tailwind CSS, TanStack Query  
✅ **Docker Infrastructure** - PostgreSQL, Redis, MinIO  
✅ **Core Features** - Auth, Courses, Flashcards (SM-2), Focus Mode  

---

## Quick Start (5 minutes)

### Step 1: Generate Encryption Keys

```bash
cd backend
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output. You'll need it for `.env`.

### Step 2: Create `.env` File

```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY` - Any random string (32+ chars)
- `ENCRYPTION_KEY` - The key from Step 1
- `MOODLE_URL` - Your Moodle URL (default: https://moodle.concordia.ca)
- `OPENAI_API_KEY` - Your OpenAI API key

### Step 3: Start Infrastructure

```bash
# Start PostgreSQL, Redis, MinIO
docker-compose up -d postgres redis minio
```

Wait 10 seconds for services to initialize.

### Step 4: Setup Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

### Step 5: Start Backend

```bash
# Still in backend/ with venv activated
uvicorn app.main:app --reload --port 8000
```

Backend running at: **http://localhost:8000**  
API docs at: **http://localhost:8000/api/docs**

### Step 6: Setup Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend running at: **http://localhost:3000**

---

## First Login

1. Go to **http://localhost:3000**
2. Get your Moodle API token:
   - Login to Moodle
   - Profile → Preferences → Security Keys
   - Create token for "Web Services"
3. Paste token and login
4. Your courses will sync automatically!

---

## Features Available Now

### ✅ Smart Study
- AI flashcards with SM-2 spaced repetition
- Review due cards
- Track progress

### ✅ Focus Mode
- Pomodoro timer (25/50/15/5 min presets)
- Ambient sounds
- Session tracking
- Statistics dashboard

### ✅ Dashboard
- Points & streak tracking
- Course overview
- Quick stats

### 🚧 Coming Soon
- Campus Underground (study groups)
- Live Sync (auto Moodle sync)
- Accountability Circle (leaderboards)
- Brain Dump (notes + voice memos)

---

## Architecture

```
┌─────────────────────────────────────┐
│   React Frontend (Port 3000)        │
│   - TypeScript + Tailwind           │
│   - TanStack Query + Zustand        │
└──────────────┬──────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────┐
│   FastAPI Backend (Port 8000)       │
│   - Async endpoints                 │
│   - JWT authentication              │
│   - Pydantic validation             │
└──────┬───────┬──────────┬───────────┘
       │       │          │
   ┌───▼───┐ ┌─▼──┐  ┌───▼────┐
   │Postgres│ │Redis│  │ MinIO  │
   │  :5432 │ │:6379│  │ :9000  │
   └────────┘ └─────┘  └────────┘
```

---

## Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest -v
```

### API Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Login (replace with your token)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"moodle_token":"YOUR_TOKEN"}'
```

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database Connection Error
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Frontend Build Errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Missing Encryption Key Error
```bash
# Generate new key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env as ENCRYPTION_KEY
```

---

## Production Deployment

### Full Docker Stack
```bash
# Build all services
docker-compose build

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f
```

### Environment Variables
Ensure these are set in production `.env`:
- `ENVIRONMENT=production`
- `DEBUG=False`
- Strong `SECRET_KEY` and `ENCRYPTION_KEY`
- Production database URLs
- HTTPS CORS origins

---

## Development Commands

```bash
# Backend
make dev          # Start dev environment
make migrate      # Run migrations
make test         # Run tests
make lint         # Run linters

# Frontend
npm run dev       # Dev server
npm run build     # Production build
npm run lint      # ESLint
```

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login with Moodle token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### Courses
- `GET /api/v1/courses/` - List courses
- `POST /api/v1/courses/sync` - Sync from Moodle
- `GET /api/v1/courses/{id}/materials` - Get materials

### Flashcards
- `GET /api/v1/flashcards/due` - Get due cards
- `POST /api/v1/flashcards/{id}/review` - Review card
- `POST /api/v1/flashcards/` - Create card

### Focus Mode
- `POST /api/v1/focus/sessions` - Start session
- `PATCH /api/v1/focus/sessions/{id}/complete` - Complete
- `GET /api/v1/focus/stats` - Get statistics

Full API docs: **http://localhost:8000/api/docs**

---

## Database Schema

### Users
- JWT authentication
- Encrypted Moodle tokens
- Points & streak tracking

### Courses
- Synced from Moodle
- Auto-update support

### Flashcards
- SM-2 spaced repetition
- Easiness factor tracking
- Review statistics

### Focus Sessions
- Duration tracking
- Completion status
- Ambient sound preferences

---

## Next Steps

1. ✅ Login and sync courses
2. ✅ Create flashcards from materials
3. ✅ Start a focus session
4. 🚧 Implement remaining features
5. 🚧 Deploy to production

---

## Support

- **Backend Issues**: Check `backend/app/` files
- **Frontend Issues**: Check `frontend/src/` files
- **Database Issues**: Check Docker logs
- **API Docs**: http://localhost:8000/api/docs

---

**Built with:** FastAPI 0.115 • React 18.2 • PostgreSQL 15 • Redis 7 • TypeScript 5.6
