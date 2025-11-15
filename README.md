# Crew Copilot 🚀

AI-powered crew pay intelligence system eliminating daily claims at Avelo Airlines.

## Overview

Crew Copilot is a multi-agent AI system built with LangGraph and Claude Sonnet 4.5 that automates complex crew pay calculations with 95%+ accuracy, eliminating the need for daily claims.

## Architecture

### 8 Specialized AI Agents

1. **Flight Time Calculator** - Calculate flight pay from ACARS data
2. **Duty Time Monitor** - Enforce FAA Part 117 regulations
3. **Per Diem Calculator** - Apply GSA/State Dept rates
4. **Premium Pay Calculator** - Calculate overtime, holiday, red-eye pay
5. **Guarantee Calculator** - Ensure minimum monthly guarantees
6. **Compliance Validator** - Validate against FAA & union contracts
7. **Claim Dispute Resolution** - Auto-process and resolve claims
8. **Crew Pay Orchestrator** - LangGraph coordinator

### Tech Stack

- **AI**: Claude Sonnet 4.5, LangGraph, LangChain
- **Backend**: FastAPI, Python 3.10+
- **Database**: PostgreSQL (Neon)
- **Testing**: pytest

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Set Up Database

```bash
psql $DATABASE_URL -f database/schema.sql
psql $DATABASE_URL -f database/faa_tables.sql
psql $DATABASE_URL -f database/seed_crew.sql
psql $DATABASE_URL -f database/seed_flights.sql
```

### 4. Run API Server

```bash
uvicorn api.main:app --reload
```

### 5. Test the Workflow

```python
from agents.orchestrator import run_crew_pay_workflow

result = run_crew_pay_workflow(
    crew_member_id="P12345",
    pay_period="2025-11-01 to 2025-11-15"
)
print(result)
```

## Project Structure

```
crew-copilot/
├── agents/               # AI agents
│   ├── core/            # Individual agents
│   ├── orchestrator.py  # LangGraph workflow
│   ├── state.py         # State management
│   └── prompts/         # Agent prompts
├── api/                 # FastAPI application
│   ├── main.py
│   ├── models.py        # SQLAlchemy ORM
│   ├── schemas.py       # Pydantic schemas
│   └── v1/              # API endpoints
├── database/            # SQL schemas & seeds
├── tests/               # Test suite
└── docs/                # Documentation
```

## API Endpoints

- `POST /api/v1/calculations/process` - Process crew pay for period
- `GET /api/v1/crew/{employee_id}` - Get crew member details
- `POST /api/v1/claims/file` - File a new claim
- `GET /api/v1/claims/{claim_id}` - Get claim status

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agents --cov=api

# Run specific agent tests
pytest tests/test_agents/test_flight_time.py
```

## License

Proprietary - Avelo Airlines Design Partner Agreement
