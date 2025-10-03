# StudyMaster Quick Start Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Redis 7+
- Docker & Docker Compose (optional)

## Option 1: Docker Setup (Recommended)

### 1. Clone and Setup
```bash
cd /Users/obinna.c/CascadeProjects/ug-dashboard/moodle-api-client
```

### 2. Create Environment Files

**Backend (.env)**
```bash
cat > .env << EOF
# Database
DATABASE_URL=postgresql+asyncpg://studymaster:password@postgres:5432/studymaster
DATABASE_URL_SYNC=postgresql://studymaster:password@postgres:5432/studymaster

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Moodle
MOODLE_URL=https://moodle.concordia.ca

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=studymaster-files

# Environment
ENVIRONMENT=development
DEBUG=True
EOF
```

**Frontend (.env)**
```bash
cat > frontend/.env << EOF
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Run Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 5. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Option 2: Manual Setup

### Backend Setup

#### 1. Create Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements-new.txt
```

#### 3. Setup PostgreSQL
```bash
# Create database
createdb studymaster

# Or using psql
psql -U postgres
CREATE DATABASE studymaster;
CREATE USER studymaster WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE studymaster TO studymaster;
\q
```

#### 4. Setup Redis
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis
```

#### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

#### 6. Run Migrations
```bash
cd backend
alembic upgrade head
```

#### 7. Start Backend
```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 8. Start Celery Worker (separate terminal)
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

#### 9. Start Celery Beat (separate terminal)
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

### Frontend Setup

#### 1. Install Dependencies
```bash
cd frontend
npm install
```

#### 2. Start Development Server
```bash
npm run dev
```

#### 3. Build for Production
```bash
npm run build
npm run preview  # Preview production build
```

## Initial Data Setup

### 1. Create Admin User (Optional)
```bash
# Using Python shell
python
>>> from app.db.session import SessionLocal
>>> from app.models.user import User
>>> from app.core.security import get_password_hash
>>> db = SessionLocal()
>>> admin = User(
...     username="admin",
...     email="admin@studymaster.com",
...     hashed_password=get_password_hash("admin123")
... )
>>> db.add(admin)
>>> db.commit()
```

### 2. Test Moodle Connection
```bash
# Using API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"token": "your_moodle_token"}'
```

## Development Workflow

### Running Tests
```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend
black app/
isort app/
flake8 app/
mypy app/

# Frontend
npm run lint
npm run type-check
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Common Tasks

### Reset Database
```bash
# Drop and recreate
dropdb studymaster
createdb studymaster
alembic upgrade head
```

### Clear Redis Cache
```bash
redis-cli FLUSHALL
```

### View Logs
```bash
# Docker
docker-compose logs -f backend
docker-compose logs -f frontend

# Manual
tail -f logs/app.log
```

### Backup Database
```bash
pg_dump studymaster > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
psql studymaster < backup_20231215.sql
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Check connection
psql -U studymaster -d studymaster
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

### Frontend Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Migration Conflicts
```bash
# Reset migrations (development only!)
alembic downgrade base
rm alembic/versions/*.py
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## Production Deployment

### Using Docker Compose
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Environment Variables (Production)
```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/studymaster
REDIS_URL=redis://prod-redis:6379/0
ALLOWED_ORIGINS=https://studymaster.com
```

### SSL/HTTPS Setup
```bash
# Using Let's Encrypt with Nginx
certbot --nginx -d studymaster.com -d www.studymaster.com
```

## Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Redis health
curl http://localhost:8000/health/redis
```

### Metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## Next Steps

1. **Configure Moodle Integration**
   - Obtain API token from Moodle
   - Test connection
   - Enable auto-sync

2. **Setup OpenAI**
   - Get API key
   - Configure in .env
   - Test PDF summarization

3. **Configure S3 Storage**
   - Create S3 bucket
   - Set up IAM credentials
   - Test file uploads

4. **Customize Features**
   - Adjust sync intervals
   - Configure point decay rates
   - Customize UI theme

5. **Deploy to Production**
   - Set up domain
   - Configure SSL
   - Set up monitoring
   - Configure backups

## Support & Resources

- **Documentation**: `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Discord**: Community server

## License

MIT License - See LICENSE file for details
