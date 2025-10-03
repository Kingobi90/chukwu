# StudyMaster - Next Steps to Complete Setup

## ✅ What's Been Completed

1. **Backend Infrastructure** - FastAPI app with all models, schemas, and API endpoints
2. **Frontend Application** - React app with Login, Dashboard, Smart Study, Focus Mode pages
3. **Docker Services** - PostgreSQL, Redis, MinIO containers running
4. **Dependencies** - Backend Python packages installed, Frontend npm packages installing
5. **Environment** - `.env` file created with generated encryption keys

## 🔧 Remaining Setup Steps

### Step 1: Wait for Database Initialization (30 seconds)

The PostgreSQL container needs time to fully initialize the `studymaster` user and database.

```bash
# Check if postgres is ready
docker logs studymaster-postgres | grep "database system is ready"
```

### Step 2: Run Database Migration

```bash
cd backend
./venv/bin/alembic revision --autogenerate -m "Initial migration"
./venv/bin/alembic upgrade head
```

If you get "role studymaster does not exist", wait another 30 seconds and try again.

### Step 3: Start Backend Server

```bash
# In backend/ directory with venv activated
./venv/bin/uvicorn app.main:app --reload --port 8000
```

Backend will be at: **http://localhost:8000**  
API docs at: **http://localhost:8000/api/docs**

### Step 4: Start Frontend (New Terminal)

```bash
cd frontend

# If npm install is still running, wait for it to complete
# Then start dev server
npm run dev
```

Frontend will be at: **http://localhost:3000**

### Step 5: Add Your API Keys

Edit `backend/.env` and add:
```
OPENAI_API_KEY=sk-your-key-here
```

### Step 6: First Login

1. Go to http://localhost:3000
2. Get your Moodle API token from Moodle → Profile → Security Keys
3. Paste and login
4. Your courses will sync!

---

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Stop and recreate postgres with fresh data
docker-compose down -v
docker-compose up -d postgres redis minio

# Wait 30 seconds, then run migrations
sleep 30
cd backend && ./venv/bin/alembic upgrade head
```

### Port Already in Use

```bash
# Kill process on port
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

### Frontend Dependencies Not Installing

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📋 Quick Reference

### Start Everything

```bash
# Terminal 1: Infrastructure
docker-compose up -d postgres redis minio

# Terminal 2: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm run dev
```

### Stop Everything

```bash
docker-compose down
# Ctrl+C in backend and frontend terminals
```

### Reset Database

```bash
docker-compose down -v
docker-compose up -d postgres
sleep 30
cd backend && ./venv/bin/alembic upgrade head
```

---

## 🎯 What You Can Do Now

Once everything is running:

✅ **Login** with Moodle token  
✅ **Sync courses** from Moodle  
✅ **Create flashcards** manually  
✅ **Review flashcards** with SM-2 spaced repetition  
✅ **Start focus sessions** with Pomodoro timer  
✅ **Track stats** on dashboard  

---

## 📁 Project Structure

```
moodle-api-client/
├── backend/              # FastAPI (port 8000)
│   ├── app/
│   │   ├── api/v1/endpoints/  # All API routes
│   │   ├── models/            # Database models
│   │   └── main.py            # FastAPI app
│   └── .env               # Environment variables
├── frontend/             # React (port 3000)
│   └── src/
│       ├── pages/        # All pages
│       └── lib/api.ts    # API client
└── docker-compose.yml    # Services config
```

---

## 🚀 Current Status

- ✅ Docker services: Running
- ✅ Backend dependencies: Installed
- ⏳ Frontend dependencies: Installing (check with `ps aux | grep npm`)
- ⏳ Database migration: Pending (run Step 2 above)
- ⏳ Servers: Not started yet

---

**Next:** Wait for npm to finish, then run Step 2 (database migration).
