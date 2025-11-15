# Crew Copilot - Usage Guide

How to use Crew Copilot for crew pay calculations.

## Quick Start

### 1. Calculate Crew Pay (Python)

```python
from agents.orchestrator import run_crew_pay_workflow

# Run workflow for a crew member
result = run_crew_pay_workflow(
    crew_member_id="P12345",
    pay_period="2025-11-01 to 2025-11-15"
)

# Access results
print(f"Total Pay: ${result['total_pay']:.2f}")
print(f"Total Hours: {result['total_hours']:.2f}")
print(f"Confidence: {result['confidence_score']:.2%}")
print(f"Requires Review: {result['requires_human_review']}")

# Detailed breakdown
breakdown = result['breakdown']
print(f"\nBase Pay: ${breakdown['base_pay']:.2f}")
print(f"Per Diem: ${breakdown['per_diem']:.2f}")
print(f"Premium Pay: ${breakdown['premium_pay']:.2f}")
```

### 2. Calculate Crew Pay (API)

```bash
curl -X POST http://localhost:8000/api/v1/calculations/process \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "P12345",
    "pay_period_start": "2025-11-01",
    "pay_period_end": "2025-11-15"
  }'
```

Response:
```json
{
  "execution_id": "uuid-here",
  "employee_id": "P12345",
  "pay_period_start": "2025-11-01",
  "pay_period_end": "2025-11-15",
  "status": "complete",
  "total_pay": 2182.50,
  "total_hours": 16.0,
  "breakdown": {
    "base_pay": 1680.00,
    "flight_pay": 1680.00,
    "guarantee_pay": 1575.00,
    "per_diem": 352.00,
    "premium_pay": 150.50,
    "total_pay": 2182.50
  },
  "confidence_score": 0.95,
  "requires_human_review": false,
  "warnings": [],
  "processing_time_seconds": 12.5
}
```

## Understanding the Results

### Status Values

- **complete**: Calculation completed successfully
- **needs_review**: Requires human review (compliance issues or low confidence)
- **error**: Processing error occurred

### Confidence Score

The confidence score (0.0 to 1.0) indicates the AI's confidence in the calculation:

- **0.95 - 1.00**: High confidence, clear data, no issues
- **0.85 - 0.94**: Good confidence, minor data quality issues
- **0.70 - 0.84**: Medium confidence, some missing data
- **< 0.70**: Low confidence, significant data issues or violations

### Breakdown Components

- **base_pay**: Greater of (flight pay OR guarantee pay)
- **flight_pay**: Actual flight hours × hourly rate
- **guarantee_pay**: Monthly minimum guarantee
- **per_diem**: Layover allowances
- **premium_pay**: Sum of all premiums (holiday, red-eye, international, etc.)
- **total_pay**: base_pay + per_diem + premium_pay

## Common Use Cases

### Process Pay for All Crew Members

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import CrewMember
from api.config import settings
from agents.orchestrator import CrewPayOrchestrator

# Setup database
engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)
db = Session()

# Initialize orchestrator
orchestrator = CrewPayOrchestrator()

# Get all active crew members
crew_members = db.query(CrewMember).filter(
    CrewMember.status == "active"
).all()

# Process pay for each
results = []
for crew in crew_members:
    result = orchestrator.process(
        crew_member_data=crew.__dict__,
        flight_assignments=[],  # Load from DB
        pay_period_start="2025-11-01",
        pay_period_end="2025-11-15"
    )
    results.append(result)
    print(f"Processed {crew.employee_id}: ${result['total_pay']:.2f}")

# Save results to database
# ... implement your save logic
```

### Generate Pay Report

```python
import pandas as pd

# Process pay for all crew
results = []  # ... from above

# Convert to DataFrame
df = pd.DataFrame([
    {
        "Employee ID": r["employee_id"],
        "Name": f"{r['crew_member_data']['first_name']} {r['crew_member_data']['last_name']}",
        "Role": r["crew_member_data"]["role"],
        "Hours": r["total_hours"],
        "Base Pay": r["breakdown"]["base_pay"],
        "Per Diem": r["breakdown"]["per_diem"],
        "Premium": r["breakdown"]["premium_pay"],
        "Total Pay": r["total_pay"],
        "Confidence": r["confidence_score"],
        "Review": r["requires_human_review"]
    }
    for r in results
])

# Export to Excel
df.to_excel("pay_report_2025-11-15.xlsx", index=False)

# Calculate totals
print(f"Total Payroll: ${df['Total Pay'].sum():,.2f}")
print(f"Total Hours: {df['Hours'].sum():,.2f}")
print(f"Items Needing Review: {df['Review'].sum()}")
```

### File a Claim

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/claims/file",
    json={
        "employee_id": "P12345",
        "claim_type": "missing_premium",
        "description": "Red-eye premium not applied to flight XP101 on 2025-11-03",
        "amount_claimed": 100.00,
        "flight_number": "XP101",
        "flight_date": "2025-11-03"
    }
)

claim = response.json()
print(f"Claim filed: {claim['claim_number']}")
print(f"Status: {claim['status']}")
```

### Check Claim Status

```bash
curl http://localhost:8000/api/v1/claims/CLM-20251115-P12345
```

## Working with Individual Agents

### Flight Time Calculator Only

```python
from agents.core.flight_time_calculator import FlightTimeCalculator

agent = FlightTimeCalculator()

result = agent.calculate({
    "crew_member_data": {
        "employee_id": "P12345",
        "hourly_rate": 105.00,
        # ... other crew data
    },
    "flight_assignments": [
        # ... flight data
    ],
    "execution_id": "test-123"
})

print(result["totals"]["total_credit_hours"])
print(result["totals"]["total_flight_pay"])
```

### Compliance Validator Only

```python
from agents.core.compliance_validator import ComplianceValidator

agent = ComplianceValidator()

result = agent.calculate({
    "crew_member_data": {...},
    "flight_time_data": {...},
    "duty_time_data": {...},
    "per_diem_data": {...},
    "premium_pay_data": {...},
    "guarantee_data": {...},
    "execution_id": "test-123"
})

if result["overall_compliance"] == "fail":
    print("VIOLATIONS FOUND:")
    for violation in result["violations"]:
        print(f"  - {violation['description']}")
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Tests

```bash
# Unit tests only (fast, no API calls)
pytest tests/test_agents/test_flight_time.py

# Integration tests (requires API key)
pytest -m integration
```

### Test with Sample Data

```bash
# Run the orchestrator with sample data
python agents/orchestrator.py
```

## Best Practices

### 1. Always Validate Input Data

```python
def validate_crew_data(crew_data):
    required_fields = ["employee_id", "role", "crew_type", "hourly_rate"]
    for field in required_fields:
        if field not in crew_data or crew_data[field] is None:
            raise ValueError(f"Missing required field: {field}")
    return True
```

### 2. Handle Errors Gracefully

```python
try:
    result = orchestrator.process(...)
except Exception as e:
    logger.error(f"Pay calculation failed: {str(e)}")
    # Notify administrators
    # Flag for manual review
```

### 3. Review Low Confidence Results

```python
if result["confidence_score"] < 0.85 or result["requires_human_review"]:
    # Send to human reviewer
    queue_for_review(result)
else:
    # Auto-approve
    approve_pay(result)
```

### 4. Monitor Agent Performance

```python
from api.models import AgentExecutionLog

# Query execution logs
logs = db.query(AgentExecutionLog).filter(
    AgentExecutionLog.agent_name == "FlightTimeCalculator",
    AgentExecutionLog.success == False
).all()

# Analyze failure patterns
for log in logs:
    print(f"Error: {log.error_message}")
```

## Advanced Usage

### Custom Agent Configuration

```python
from agents.core.flight_time_calculator import FlightTimeCalculator

# Use higher temperature for more creative interpretations
agent = FlightTimeCalculator()
agent.temperature = 0.3  # Default is 0.1

# Or customize prompts
from agents.prompts import flight_time_prompts
flight_time_prompts.FLIGHT_TIME_SYSTEM_PROMPT += "\nAdditional instruction..."
```

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_crew_pay(crew_id):
    return run_crew_pay_workflow(crew_id, "2025-11-01 to 2025-11-15")

crew_ids = ["P12345", "P12346", "P23456", "FA34567", "FA34568"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_crew_pay, crew_ids))
```

## Troubleshooting

### Low Confidence Scores

**Cause**: Missing or inconsistent flight data
**Solution**:
- Verify ACARS data is complete
- Check for missing actual departure/arrival times
- Ensure duty times are recorded

### High Processing Time

**Cause**: Too many flights or complex scenarios
**Solution**:
- Process in smaller batches
- Use caching for frequently accessed data
- Optimize database queries

### Compliance Violations

**Cause**: Crew exceeded FAA limits
**Solution**:
- Review duty time logs
- Verify rest periods
- Check if exemptions apply
- Flag for crew scheduling review

## Support

For issues or questions:
- Check documentation in `/docs`
- Review test cases in `/tests`
- File issues on GitHub
- Contact: support@example.com
