# Crew Copilot - Developer Guide

Quick reference guide for developers working on Crew Copilot.

---

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/jbandu/crew-copilot.git
cd crew-copilot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your DATABASE_URL and ANTHROPIC_API_KEY

# 3. Setup database
psql $DATABASE_URL -f database/schema.sql
psql $DATABASE_URL -f database/faa_tables.sql
psql $DATABASE_URL -f database/seed_crew.sql
psql $DATABASE_URL -f database/seed_flights.sql

# 4. Test
python agents/orchestrator.py

# 5. Run API
uvicorn api.main:app --reload
```

---

## Project Structure

```
crew-copilot/
├── agents/              # AI Agents
│   ├── core/           # 7 specialized agents
│   ├── prompts/        # Claude prompts
│   ├── orchestrator.py # LangGraph workflow
│   └── state.py        # State management
│
├── api/                # FastAPI Application
│   ├── main.py         # API endpoints
│   ├── models.py       # Database ORM
│   ├── schemas.py      # Request/response schemas
│   └── config.py       # Settings
│
├── database/           # Database
│   ├── schema.sql      # Table definitions
│   ├── faa_tables.sql  # Lookup data
│   └── seed_*.sql      # Test data
│
├── tests/              # Tests
│   ├── test_agents/    # Agent tests
│   └── test_orchestrator.py
│
└── docs/               # Documentation
    ├── CODE_DOCUMENTATION.md    # Complete code docs
    ├── API_REFERENCE.md         # API reference
    ├── ARCHITECTURE.md          # System architecture
    ├── SETUP.md                 # Setup guide
    └── USAGE.md                 # Usage examples
```

---

## Common Tasks

### Run Tests

```bash
# All tests
pytest

# Unit tests only (fast, no API calls)
pytest -m "not integration"

# Integration tests (requires ANTHROPIC_API_KEY)
pytest -m integration

# With coverage
pytest --cov=agents --cov=api

# Specific test
pytest tests/test_agents/test_flight_time.py::test_flight_time_with_no_flights -v
```

### Database Operations

```bash
# Connect to database
psql $DATABASE_URL

# Run migrations
psql $DATABASE_URL -f database/schema.sql

# Check tables
psql $DATABASE_URL -c "\dt"

# Query data
psql $DATABASE_URL -c "SELECT * FROM crew_members;"

# Reset database (CAREFUL!)
psql $DATABASE_URL -f database/schema.sql
psql $DATABASE_URL -f database/faa_tables.sql
psql $DATABASE_URL -f database/seed_crew.sql
psql $DATABASE_URL -f database/seed_flights.sql
```

### Code Quality

```bash
# Format code
black agents/ api/ tests/

# Lint
ruff check agents/ api/ tests/

# Type checking
mypy agents/ api/
```

### API Development

```bash
# Start dev server
uvicorn api.main:app --reload

# Start on different port
uvicorn api.main:app --port 8001

# View API docs
open http://localhost:8000/docs

# Test endpoint
curl http://localhost:8000/health
```

---

## Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `agents/orchestrator.py` | LangGraph workflow | 426 |
| `agents/core/base_agent.py` | Base agent class | 169 |
| `agents/state.py` | State definition | 42 |
| `api/main.py` | API endpoints | 369 |
| `api/models.py` | Database models | 206 |
| `database/schema.sql` | Database schema | 422 |

---

## Code Patterns

### Adding a New Agent

1. Create `agents/core/new_agent.py`:
```python
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="NewAgent", temperature=0.1)

    def calculate(self, input_data):
        result = self.call_claude(
            system_prompt=NEW_AGENT_PROMPT,
            user_message=f"Calculate..."
        )
        return result
```

2. Create `agents/prompts/new_agent_prompts.py`:
```python
NEW_AGENT_PROMPT = """You are an expert..."""
```

3. Add to orchestrator workflow

4. Update state in `agents/state.py`

5. Write tests in `tests/test_agents/test_new_agent.py`

### Adding an API Endpoint

1. Define schema in `api/schemas.py`:
```python
class NewRequest(BaseModel):
    field: str

class NewResponse(BaseModel):
    result: str
```

2. Add endpoint in `api/main.py`:
```python
@app.post("/api/v1/new", response_model=NewResponse)
async def new_endpoint(request: NewRequest, db: Session = Depends(get_db)):
    # Implementation
    return NewResponse(result="...")
```

### Database Query Patterns

```python
# Get single record
crew = db.query(CrewMember).filter(
    CrewMember.employee_id == "P12345"
).first()

# Get multiple with filter
flights = db.query(FlightAssignment).filter(
    FlightAssignment.crew_member_id == crew.id,
    FlightAssignment.flight_date >= start_date,
    FlightAssignment.flight_date <= end_date
).all()

# Join queries
results = db.query(CrewMember, FlightAssignment).join(
    FlightAssignment
).filter(...).all()

# Count
count = db.query(FlightAssignment).filter(...).count()
```

---

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection | Yes |
| `ANTHROPIC_API_KEY` | Claude API key | Yes |
| `APP_ENV` | Environment (dev/staging/prod) | No |
| `LOG_LEVEL` | Logging level | No |
| `API_HOST` | API host | No |
| `API_PORT` | API port | No |

---

## Debugging

### Enable Debug Logging

```python
# In agents/orchestrator.py
logging.basicConfig(level=logging.DEBUG)  # Change from INFO
```

### View Agent Execution Logs

```sql
SELECT
    agent_name,
    execution_time_ms,
    success,
    error_message,
    created_at
FROM agent_execution_log
ORDER BY created_at DESC
LIMIT 10;
```

### Test Single Agent

```python
from agents.core.flight_time_calculator import FlightTimeCalculator

agent = FlightTimeCalculator()
result = agent.calculate({
    "crew_member_data": {...},
    "flight_assignments": [...],
    "execution_id": "debug-123"
})
print(result)
```

### Print State at Each Step

Add to orchestrator methods:
```python
def _calculate_flight_time(self, state):
    print(f"State before flight time: {state['status']}")
    # ... calculation
    print(f"Flight time data: {state['flight_time_data']}")
    return state
```

---

## Performance Tips

1. **Database**: Use indexes on frequently queried fields
2. **API**: Use pagination for large result sets
3. **Agents**: Batch flights in single Claude call vs multiple calls
4. **Caching**: Cache per diem rates, premium rules
5. **Async**: Use async/await for I/O operations

---

## Security Checklist

- [ ] Never commit `.env` file
- [ ] Use parameterized queries (SQLAlchemy handles this)
- [ ] Validate all inputs with Pydantic
- [ ] Add rate limiting in production
- [ ] Implement authentication (JWT)
- [ ] Use HTTPS in production
- [ ] Sanitize error messages (don't leak internals)
- [ ] Audit sensitive operations

---

## Deployment

### Development
```bash
uvicorn api.main:app --reload
```

### Production
```bash
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Docker (Future)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Useful Commands

```bash
# Count lines of code
find . -name "*.py" -exec wc -l {} + | tail -1

# Find TODO comments
grep -r "TODO" --include="*.py" .

# Check imports
python -m pylint --disable=all --enable=import-error agents/

# Generate requirements
pip freeze > requirements.txt

# Database backup
pg_dump $DATABASE_URL > backup.sql

# Database restore
psql $DATABASE_URL < backup.sql
```

---

## Resources

**Documentation**:
- Complete code docs: `docs/CODE_DOCUMENTATION.md`
- API reference: `docs/API_REFERENCE.md`
- Architecture: `docs/ARCHITECTURE.md`
- Setup guide: `docs/SETUP.md`
- Usage examples: `docs/USAGE.md`

**External Docs**:
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [Claude API Docs](https://docs.anthropic.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)

**Tools**:
- API Playground: http://localhost:8000/docs
- Database Admin: Use psql or pgAdmin

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | `pip install -r requirements.txt` |
| Database connection failed | Check `DATABASE_URL` in `.env` |
| Claude API errors | Verify `ANTHROPIC_API_KEY` |
| Tests failing | Run `pytest -v` for details |
| Port already in use | `lsof -i :8000` and kill process |

---

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Run tests: `pytest`
4. Format code: `black .`
5. Commit: `git commit -m "feat: add feature"`
6. Push: `git push origin feature/my-feature`
7. Create Pull Request

---

**Happy Coding!** 🚀

For questions, see complete documentation in `/docs` folder.
