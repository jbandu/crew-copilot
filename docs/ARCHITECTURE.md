# Crew Copilot - Architecture

System architecture and design documentation.

## Overview

Crew Copilot is a multi-agent AI system built with LangGraph and Claude Sonnet 4.5 that automates complex airline crew pay calculations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Server                        │
│                    (api/main.py)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Orchestrator                     │
│                   (agents/orchestrator.py)                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
     ┌───────────┴───────────┐
     │                       │
     ▼                       ▼
┌─────────┐            ┌──────────┐
│ Agent 1 │────────────│ Agent 2  │
│ Flight  │            │ Duty     │
│ Time    │            │ Time     │
└─────────┘            └──────────┘
     │                       │
     ▼                       ▼
┌─────────┐            ┌──────────┐
│ Agent 3 │────────────│ Agent 4  │
│ Per     │            │ Premium  │
│ Diem    │            │ Pay      │
└─────────┘            └──────────┘
     │                       │
     ▼                       ▼
┌─────────┐            ┌──────────┐
│ Agent 5 │────────────│ Agent 6  │
│ Guarantee│           │Compliance│
└─────────┘            └──────────┘
     │                       │
     └───────────┬───────────┘
                 ▼
           ┌──────────┐
           │ Agent 7  │
           │ Claims   │
           └──────────┘
                 │
                 ▼
         ┌──────────────┐
         │   Database   │
         │ (PostgreSQL) │
         └──────────────┘
```

## Component Details

### 1. FastAPI Application Layer

**Location**: `api/`

**Responsibilities**:
- HTTP request handling
- Database connections
- Input validation
- Response formatting
- Error handling

**Key Files**:
- `main.py` - FastAPI app and endpoints
- `models.py` - SQLAlchemy ORM models
- `schemas.py` - Pydantic request/response schemas
- `config.py` - Configuration management

**Endpoints**:
- `GET /health` - Health check
- `GET /api/v1/crew/{employee_id}` - Get crew member
- `GET /api/v1/crew/{employee_id}/flights` - Get flights
- `POST /api/v1/calculations/process` - Calculate pay
- `POST /api/v1/claims/file` - File claim
- `GET /api/v1/claims/{claim_id}` - Get claim status

### 2. Agent Orchestration Layer

**Location**: `agents/orchestrator.py`

**Responsibilities**:
- Coordinate agent execution
- Manage workflow state
- Handle errors and retries
- Aggregate results
- Decide routing (human review vs auto-approval)

**Workflow**:
```python
Entry → Flight Time → Duty Time → Per Diem → Premium →
Guarantee → Compliance → [Claims / Review] → Finalize → End
```

**State Management**:
- Uses TypedDict `CrewPayState` defined in `agents/state.py`
- State flows through all agents
- Each agent updates relevant portions
- Immutable state pattern (agents return new state)

### 3. Specialized Agents

**Location**: `agents/core/`

Each agent inherits from `BaseAgent` and implements:
- Specialized calculation logic
- Claude API integration
- Error handling
- Logging and audit trails

#### Agent 1: Flight Time Calculator
- **File**: `flight_time_calculator.py`
- **Input**: Flight assignments, crew data
- **Output**: Flight hours, credit hours, flight pay
- **Key Logic**: Block time calculation, minimum credit application

#### Agent 2: Duty Time Monitor
- **File**: `duty_time_monitor.py`
- **Input**: Flight assignments, duty times
- **Output**: Compliance status, violations, fatigue assessment
- **Key Logic**: FAA Part 117 validation, cumulative limit tracking

#### Agent 3: Per Diem Calculator
- **File**: `per_diem_calculator.py`
- **Input**: Layover locations, dates
- **Output**: Per diem breakdown by day
- **Key Logic**: GSA rate lookup, first/last day proration

#### Agent 4: Premium Pay Calculator
- **File**: `premium_pay_calculator.py`
- **Input**: Flights, crew role, rates
- **Output**: Premium pay by type
- **Key Logic**: Holiday detection, red-eye identification, premium stacking

#### Agent 5: Guarantee Calculator
- **File**: `guarantee_calculator.py`
- **Input**: Actual hours, crew type
- **Output**: Guarantee vs actual comparison
- **Key Logic**: Monthly minimum enforcement

#### Agent 6: Compliance Validator
- **File**: `compliance_validator.py`
- **Input**: All prior agent outputs
- **Output**: Compliance status, violations, recommendations
- **Key Logic**: Multi-layered validation (FAA, contract, calculations)

#### Agent 7: Claim Resolution
- **File**: `claim_resolution.py`
- **Input**: Claim data, supporting evidence
- **Output**: Resolution recommendation
- **Key Logic**: Root cause analysis, auto-resolution criteria

### 4. Base Agent Class

**Location**: `agents/core/base_agent.py`

**Provides**:
- Claude API client initialization
- Structured API calling
- JSON parsing from Claude responses
- Logging infrastructure
- Execution tracking
- Error handling patterns

**Key Methods**:
- `call_claude()` - Make API calls with system prompt
- `log_execution()` - Record execution for audit
- `calculate()` - Abstract method implemented by each agent

### 5. Database Layer

**Location**: `api/models.py`, `database/schema.sql`

**Tables**:
- `crew_members` - Crew profiles
- `flight_assignments` - Individual flights
- `pay_calculations` - Calculated pay records
- `claims` - Pay dispute claims
- `agent_execution_log` - Audit trail
- `faa_compliance_log` - Regulatory compliance tracking
- `pay_periods` - Pay period definitions
- `premium_rules` - Contract rules for premiums
- `per_diem_rates` - GSA/State Dept rates
- `faa_fdp_limits` - FAA Part 117 Table B limits

**Relationships**:
```
crew_members (1) ──── (N) flight_assignments
crew_members (1) ──── (N) pay_calculations
crew_members (1) ──── (N) claims
flight_assignments (1) ──── (N) pay_calculations
```

## Data Flow

### Pay Calculation Flow

1. **API Request**
   ```
   POST /api/v1/calculations/process
   {
     "employee_id": "P12345",
     "pay_period_start": "2025-11-01",
     "pay_period_end": "2025-11-15"
   }
   ```

2. **Database Query**
   - Fetch crew member profile
   - Fetch flight assignments for period
   - Convert to dictionaries

3. **Initialize State**
   ```python
   state = {
     "crew_member_data": {...},
     "flight_assignments": [...],
     "execution_id": "uuid",
     # ... empty agent data fields
   }
   ```

4. **Execute Workflow**
   - LangGraph invokes each agent in sequence
   - Each agent:
     - Receives current state
     - Calls Claude with specialized prompt
     - Updates state with results
     - Returns updated state
   - State flows through all agents

5. **Aggregate Results**
   - Orchestrator finalizes calculations
   - Computes total pay
   - Calculates confidence score
   - Determines review requirement

6. **Return Response**
   ```json
   {
     "total_pay": 2182.50,
     "breakdown": {...},
     "confidence_score": 0.95,
     "requires_human_review": false
   }
   ```

## Claude Integration

### Prompt Engineering

Each agent has a specialized system prompt defining:
- Agent role and expertise
- Specific responsibilities
- Calculation rules and formulas
- Output format (JSON schema)
- Edge case handling

**Example** (`agents/prompts/flight_time_prompts.py`):
```python
FLIGHT_TIME_SYSTEM_PROMPT = """
You are an expert Flight Time Calculator Agent...

RESPONSIBILITIES:
1. Calculate block time from actual flight data
2. Handle multiple flight segments per duty period
...

OUTPUT FORMAT:
{
  "flights": [...],
  "totals": {...},
  ...
}
"""
```

### Structured Outputs

All agents return JSON responses parsed into dictionaries:
- Consistent schema validation
- Type safety with Pydantic models
- Easy integration between agents
- Audit trail preservation

### Temperature Settings

- **Flight/Duty/Per Diem/Premium/Guarantee**: 0.1 (deterministic calculations)
- **Compliance**: 0.1 (strict rule enforcement)
- **Claims**: 0.1 (objective analysis)

## Error Handling

### Layered Error Handling

1. **Agent Level**
   ```python
   try:
       result = agent.calculate(input_data)
   except Exception as e:
       log_error(e)
       raise
   ```

2. **Orchestrator Level**
   ```python
   try:
       state = agent_function(state)
   except Exception as e:
       state["error_log"].append(str(e))
       state["status"] = "error"
   ```

3. **API Level**
   ```python
   try:
       result = orchestrator.process(...)
   except Exception as e:
       raise HTTPException(500, detail=str(e))
   ```

### Retry Logic

- Network errors: 3 retries with exponential backoff
- Rate limits: Automatic retry after delay
- Transient errors: Retry once
- Validation errors: No retry, immediate fail

## Performance Considerations

### Optimization Strategies

1. **Database**
   - Connection pooling (SQLAlchemy)
   - Indexed queries (employee_id, flight_date, etc.)
   - Batch loading of related data

2. **API Calls**
   - Async/await patterns for I/O
   - Claude API rate limit management
   - Response caching (when appropriate)

3. **Workflow**
   - Parallel agent execution (where dependencies allow)
   - Early termination on critical errors
   - Selective agent execution (skip if no relevant data)

### Scalability

**Current Design** (Single server):
- ~10-20 pay calculations per minute
- Limited by Claude API rate limits
- Suitable for <1000 crew members

**Scaling Options**:
- Horizontal scaling with load balancer
- Message queue for async processing (Celery + Redis)
- Caching layer (Redis) for frequently accessed data
- Database read replicas

## Security

### Data Protection

- Environment variables for secrets (.env)
- Database credentials not in code
- API keys in secure storage
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)

### Access Control

- API authentication (to be implemented)
- Role-based access control (RBAC)
- Audit logging for all calculations
- Sensitive data encryption at rest

## Monitoring & Logging

### Logging Levels

- **DEBUG**: Detailed agent execution
- **INFO**: Request/response, workflow progress
- **WARNING**: Data quality issues, low confidence
- **ERROR**: Exceptions, failures
- **CRITICAL**: System failures

### Metrics to Monitor

- API response time
- Agent execution time
- Confidence score distribution
- Human review rate
- Error rate by agent
- Database query performance

### Audit Trail

All executions logged in `agent_execution_log`:
- Agent name
- Execution ID (links related executions)
- Input/output data
- Execution time
- Success/failure
- Error messages

## Testing Strategy

### Test Layers

1. **Unit Tests** (`tests/test_agents/`)
   - Individual agent logic
   - Helper function validation
   - Mock Claude responses

2. **Integration Tests** (`tests/test_orchestrator.py`)
   - Full workflow execution
   - Actual Claude API calls
   - Database integration

3. **API Tests** (to be added)
   - Endpoint validation
   - Response format checking
   - Error handling

### Test Data

Sample data in `tests/fixtures/sample_data.py`:
- Crew member profiles
- Flight assignments
- Expected results

## Future Enhancements

### Planned Features

1. **Machine Learning**
   - Historical pattern detection
   - Anomaly detection for claims
   - Predictive analytics for scheduling

2. **Advanced Workflows**
   - Parallel agent execution
   - Dynamic routing based on crew type
   - Custom agent configurations per airline

3. **Integration**
   - ACARS system integration
   - Payroll system export
   - Crew scheduling system sync

4. **UI/UX**
   - Web dashboard for payroll staff
   - Mobile app for crew members
   - Real-time pay estimates

### Technical Debt

- Add comprehensive API authentication
- Implement rate limiting
- Add response caching
- Improve error messages
- Add more test coverage
- Performance profiling and optimization
