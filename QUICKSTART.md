# Quick Start Guide

## Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Mistral AI API Key

## Step-by-Step Setup

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd Assignment

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your keys
nano .env  # or use your preferred editor
```

**Required variables:**
```bash
MISTRAL_API_KEY=your-mistral-api-key-here
SECRET_KEY=your-secret-key-at-least-32-characters-long

# Email Configuration (Choose one)

# Option 1: Gmail SMTP (Recommended for testing)
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
EMAIL_FROM=your-email@gmail.com

# Option 2: SendGrid
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your-sendgrid-key
```

**📧 Gmail Setup Instructions:**
1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Create a new App Password for "Mail"
3. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
4. Use it as `SMTP_PASSWORD` in your `.env` file

### 3. Start Database Services

```bash
# Start PostgreSQL and Redis using Docker
docker-compose up -d postgres redis

# Wait for services to be ready (5-10 seconds)
sleep 10

# Initialize database tables
python3 -c "from app.core.database import init_db; init_db()"
```

### 4. Start the Application

Open two terminal windows:

**Terminal 1 - API Server:**
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
source .venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
```

### 5. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"AI Agent Orchestration System",...}
```

### 6. Test with Sample Upload

```bash
# Upload a PDF (replace with your PDF file)
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@your_document.pdf" \
  -F "recipient_email=test@example.com" \
  -F "user_id=1"

# Response contains job_id
# {
#   "document": {...},
#   "job_id": "550e8400-e29b-41d4-a716-446655440000",
#   "message": "Document uploaded successfully..."
# }

# Check job status (use the job_id from above)
curl http://localhost:8000/api/v1/jobs/YOUR-JOB-ID/status

# Get detailed results
curl http://localhost:8000/api/v1/jobs/YOUR-JOB-ID
```

### 7. Access API Documentation

Open in your browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Alternative: Docker Compose (All-in-One)

```bash
# Start everything with Docker Compose
docker-compose up --build

# API will be available at http://localhost:8000
```

## Troubleshooting

### Database Connection Error
```bash
# Restart database
docker-compose restart postgres

# Check if running
docker-compose ps
```

### Redis Connection Error
```bash
# Restart Redis
docker-compose restart redis
```

### Celery Worker Not Processing
```bash
# Check worker logs
celery -A app.tasks.celery_app worker --loglevel=debug

# Clear Redis queue
redis-cli FLUSHALL
```

### Port Already in Use
```bash
# Change port in command
uvicorn app.main:app --port 8001

# Or stop the process using the port
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

## Development Tips

### Running Tests
```bash
pytest tests/ -v
```

### Checking Logs
```bash
# API logs are in stdout
# Celery logs are in worker terminal

# For structured log analysis
tail -f logs/app.log | jq .
```

### Database Migrations (Future)
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Next Steps

1. Read the [README.md](README.md) for detailed documentation
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check [API_EXAMPLES.md](API_EXAMPLES.md) for usage examples
4. Watch the technical walkthrough video

## Support

For questions about the assignment:
- Email: himanshu.dixit@trinetralabs.ai
