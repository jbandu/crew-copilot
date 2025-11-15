# Crew Copilot - Setup Guide

Complete setup guide for the Crew Copilot AI-powered crew pay system.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher (Neon PostgreSQL recommended)
- Anthropic API key (Claude Sonnet 4.5)
- Git

## Step 1: Clone Repository

```bash
git clone https://github.com/jbandu/crew-copilot.git
cd crew-copilot
```

## Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/crew_copilot

# Anthropic
ANTHROPIC_API_KEY=your_api_key_here

# Application
APP_ENV=development
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Step 5: Set Up Database

### Create Database Schema

```bash
# Connect to your PostgreSQL database
psql $DATABASE_URL

# Or if using separate connection details:
psql -h your-host -U your-user -d crew_copilot
```

Run the schema files:

```bash
psql $DATABASE_URL -f database/schema.sql
psql $DATABASE_URL -f database/faa_tables.sql
psql $DATABASE_URL -f database/seed_crew.sql
psql $DATABASE_URL -f database/seed_flights.sql
```

### Verify Database Setup

```sql
-- Check tables were created
\dt

-- Check crew members were inserted
SELECT employee_id, first_name, last_name, role FROM crew_members;

-- Check flight assignments
SELECT COUNT(*) FROM flight_assignments;
```

## Step 6: Verify Setup

Test that everything is working:

```bash
# Run unit tests
pytest tests/test_agents/test_flight_time.py -v

# Run the orchestrator test
python agents/orchestrator.py
```

Expected output:
```
Testing Crew Pay Workflow...
================================================================================
Initializing agents...
Processing crew pay...
✅ Workflow complete!
Total Pay: $XXX.XX
```

## Step 7: Start API Server

```bash
# Development mode (with auto-reload)
uvicorn api.main:app --reload

# Or use the main.py directly
python api/main.py
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Step 8: Test API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Get Crew Member

```bash
curl http://localhost:8000/api/v1/crew/P12345
```

### Process Pay Calculation

```bash
curl -X POST http://localhost:8000/api/v1/calculations/process \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "P12345",
    "pay_period_start": "2025-11-01",
    "pay_period_end": "2025-11-15"
  }'
```

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"
```

If connection fails:
- Verify DATABASE_URL is correct
- Check database server is running
- Verify network connectivity
- Check firewall rules

### Anthropic API Issues

```bash
# Test API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

If API calls fail:
- Verify ANTHROPIC_API_KEY is set correctly
- Check API key has sufficient credits
- Verify network connectivity

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn api.main:app --port 8001
```

## Next Steps

- Read [USAGE.md](USAGE.md) for detailed usage examples
- Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Check [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation

## Production Deployment

For production deployment:

1. Set `APP_ENV=production` in `.env`
2. Use a production-grade WSGI server (e.g., Gunicorn)
3. Set up HTTPS/SSL
4. Configure database connection pooling
5. Set up monitoring and logging
6. Implement rate limiting
7. Configure CORS properly

Example production command:
```bash
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```
