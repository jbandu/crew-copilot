# Crew Copilot - API Reference

Complete API reference documentation for Crew Copilot REST API.

**Version**: 1.0.0
**Base URL**: `http://localhost:8000` (development)
**Protocol**: HTTP/HTTPS
**Format**: JSON
**Authentication**: None (add JWT for production)

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

---

## 1. Overview

### API Features

- ✅ **RESTful Design**: Standard HTTP methods (GET, POST, PUT, DELETE)
- ✅ **JSON Responses**: All responses in JSON format
- ✅ **Pydantic Validation**: Automatic request/response validation
- ✅ **OpenAPI Docs**: Auto-generated at `/docs` and `/redoc`
- ✅ **CORS Enabled**: Cross-origin requests supported
- ✅ **Error Handling**: Consistent error response format

### Base URLs

| Environment | Base URL |
|------------|----------|
| Development | `http://localhost:8000` |
| Staging | `https://staging-api.crew-copilot.com` |
| Production | `https://api.crew-copilot.com` |

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 2. Authentication

**Current**: No authentication (development only)

**Production**: Implement JWT Bearer tokens

```http
Authorization: Bearer <your_token_here>
```

### Future Authentication Flow

1. POST `/api/v1/auth/login` with credentials
2. Receive JWT token
3. Include token in `Authorization` header
4. Token expires after 24 hours
5. Refresh with POST `/api/v1/auth/refresh`

---

## 3. Endpoints

### Health Check

#### GET /health

Check API health status.

**Request**: No parameters

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-11-16T12:00:00.000Z",
  "version": "1.0.0",
  "agents_available": true,
  "database_connected": true
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

### Crew Management

#### GET /api/v1/crew/{employee_id}

Get crew member details by employee ID.

**Parameters**:
- `employee_id` (path, required): Employee ID (e.g., "P12345")

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "employee_id": "P12345",
  "first_name": "Sarah",
  "last_name": "Chen",
  "email": "sarah.chen@aveloair.com",
  "phone": "555-0101",
  "base_airport": "BUR",
  "role": "Captain",
  "seniority_date": "2021-04-15",
  "hire_date": "2021-04-15",
  "hourly_rate": 105.00,
  "crew_type": "line_holder",
  "monthly_guarantee": 75.00,
  "status": "active",
  "created_at": "2021-04-15T00:00:00",
  "updated_at": "2025-11-16T12:00:00"
}
```

**Errors**:
- `404 Not Found`: Crew member not found

**Example**:
```bash
curl http://localhost:8000/api/v1/crew/P12345
```

---

#### GET /api/v1/crew

List all crew members with pagination.

**Parameters**:
- `skip` (query, optional): Number of records to skip (default: 0)
- `limit` (query, optional): Maximum number of records (default: 100, max: 1000)

**Response**: `200 OK`
```json
[
  {
    "id": "uuid",
    "employee_id": "P12345",
    "first_name": "Sarah",
    "last_name": "Chen",
    "role": "Captain",
    ...
  },
  ...
]
```

**Example**:
```bash
# Get first 10 crew members
curl "http://localhost:8000/api/v1/crew?limit=10"

# Get next 10 (pagination)
curl "http://localhost:8000/api/v1/crew?skip=10&limit=10"
```

---

### Flight Assignments

#### GET /api/v1/crew/{employee_id}/flights

Get flight assignments for a crew member.

**Parameters**:
- `employee_id` (path, required): Employee ID
- `start_date` (query, optional): Start date filter (YYYY-MM-DD)
- `end_date` (query, optional): End date filter (YYYY-MM-DD)

**Response**: `200 OK`
```json
[
  {
    "id": "uuid",
    "flight_number": "XP101",
    "flight_date": "2025-11-03",
    "origin_airport": "BUR",
    "destination_airport": "PDX",
    "scheduled_departure": "2025-11-03T22:30:00",
    "actual_departure": "2025-11-03T22:45:00",
    "scheduled_arrival": "2025-11-04T01:15:00",
    "actual_arrival": "2025-11-04T01:20:00",
    "scheduled_block_time": 2.75,
    "actual_block_time": 2.58,
    "position": "captain",
    "overnight_location": "PDX",
    "is_international": false,
    "is_redeye": true
  },
  ...
]
```

**Example**:
```bash
# All flights for crew member
curl http://localhost:8000/api/v1/crew/P12345/flights

# Flights for specific date range
curl "http://localhost:8000/api/v1/crew/P12345/flights?start_date=2025-11-01&end_date=2025-11-15"
```

---

### Pay Calculations ⭐

#### POST /api/v1/calculations/process

**Process crew pay calculation** - Main endpoint that runs all 8 agents.

**Request Body**:
```json
{
  "employee_id": "P12345",
  "pay_period_start": "2025-11-01",
  "pay_period_end": "2025-11-15"
}
```

**Response**: `200 OK`
```json
{
  "execution_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
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

**Status Values**:
- `complete`: Successfully processed
- `needs_review`: Requires human review
- `error`: Processing failed

**Confidence Score**:
- `0.95-1.00`: High confidence
- `0.85-0.94`: Good confidence
- `0.70-0.84`: Medium confidence
- `< 0.70`: Low confidence (likely flagged for review)

**Errors**:
- `404 Not Found`: Crew member not found
- `422 Validation Error`: Invalid request format
- `500 Internal Server Error`: Processing error

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/calculations/process \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "P12345",
    "pay_period_start": "2025-11-01",
    "pay_period_end": "2025-11-15"
  }'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/calculations/process",
    json={
        "employee_id": "P12345",
        "pay_period_start": "2025-11-01",
        "pay_period_end": "2025-11-15"
    }
)

data = response.json()
print(f"Total Pay: ${data['total_pay']:.2f}")
print(f"Confidence: {data['confidence_score']:.2%}")
```

---

### Claims Management

#### POST /api/v1/claims/file

File a new pay claim.

**Request Body**:
```json
{
  "employee_id": "P12345",
  "claim_type": "missing_premium",
  "description": "Red-eye premium not applied to flight XP101 on 2025-11-03",
  "amount_claimed": 100.00,
  "flight_number": "XP101",
  "flight_date": "2025-11-03"
}
```

**Claim Types**:
- `missing_flight_time`
- `incorrect_block_time`
- `missing_premium`
- `per_diem_error`
- `guarantee_not_applied`
- `duty_violation`
- `other`

**Response**: `200 OK`
```json
{
  "id": "uuid",
  "claim_number": "CLM-20251116-P12345",
  "employee_id": "P12345",
  "claim_type": "missing_premium",
  "description": "Red-eye premium not applied...",
  "amount_claimed": 100.00,
  "amount_approved": null,
  "status": "filed",
  "filed_at": "2025-11-16T12:00:00",
  "resolved_at": null,
  "resolution_notes": null
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/claims/file \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "P12345",
    "claim_type": "missing_premium",
    "description": "Red-eye premium not applied",
    "amount_claimed": 100.00
  }'
```

---

#### GET /api/v1/claims/{claim_id}

Get claim status by claim number or ID.

**Parameters**:
- `claim_id` (path, required): Claim number (e.g., "CLM-20251116-P12345") or UUID

**Response**: `200 OK`
```json
{
  "id": "uuid",
  "claim_number": "CLM-20251116-P12345",
  "employee_id": "P12345",
  "claim_type": "missing_premium",
  "description": "Red-eye premium not applied...",
  "amount_claimed": 100.00,
  "amount_approved": 100.00,
  "status": "approved",
  "filed_at": "2025-11-16T12:00:00",
  "resolved_at": "2025-11-16T14:30:00",
  "resolution_notes": "Claim verified and approved. Premium will be included in next pay period."
}
```

**Claim Statuses**:
- `filed`: Claim submitted
- `investigating`: Under review
- `approved`: Claim approved
- `rejected`: Claim rejected
- `paid`: Payment processed
- `withdrawn`: Claim withdrawn by crew member

**Example**:
```bash
curl http://localhost:8000/api/v1/claims/CLM-20251116-P12345
```

---

## 4. Request/Response Formats

### Request Headers

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>  # For production
```

### Date Format

All dates use **ISO 8601** format:
- Date: `YYYY-MM-DD` (e.g., "2025-11-16")
- DateTime: `YYYY-MM-DDTHH:MM:SS` (e.g., "2025-11-16T12:00:00")
- Timezone: UTC by default

### Decimal Precision

- **Currency**: 2 decimal places (e.g., 105.00)
- **Hours**: 2 decimal places (e.g., 75.50)
- **Confidence**: 4 decimal places (e.g., 0.9500)

### Boolean Values

Use JSON boolean: `true` or `false` (lowercase)

---

## 5. Error Handling

### Error Response Format

All errors return this structure:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": "2025-11-16T12:00:00.000Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Examples

**404 Not Found**:
```json
{
  "error": "Not Found",
  "detail": "Crew member P99999 not found",
  "timestamp": "2025-11-16T12:00:00.000Z"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "pay_period_start"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal Server Error",
  "detail": "Error processing pay calculation: Connection timeout",
  "timestamp": "2025-11-16T12:00:00.000Z"
}
```

---

## 6. Rate Limiting

**Current**: No rate limiting (development)

**Production**: Recommended limits
- **Per User**: 100 requests/minute
- **Per IP**: 1000 requests/minute
- **Calculations Endpoint**: 10 requests/minute

**Rate Limit Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1700000000
```

**429 Response**:
```json
{
  "error": "Too Many Requests",
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "timestamp": "2025-11-16T12:00:00.000Z"
}
```

---

## 7. Examples

### Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Check API health
health = requests.get(f"{BASE_URL}/health").json()
print(f"API Status: {health['status']}")

# 2. Get crew member
crew = requests.get(f"{BASE_URL}/api/v1/crew/P12345").json()
print(f"Crew: {crew['first_name']} {crew['last_name']}")

# 3. Get their flights
flights = requests.get(
    f"{BASE_URL}/api/v1/crew/P12345/flights",
    params={"start_date": "2025-11-01", "end_date": "2025-11-15"}
).json()
print(f"Flights: {len(flights)}")

# 4. Calculate pay
pay_calc = requests.post(
    f"{BASE_URL}/api/v1/calculations/process",
    json={
        "employee_id": "P12345",
        "pay_period_start": "2025-11-01",
        "pay_period_end": "2025-11-15"
    }
).json()

print(f"\nPay Calculation Results:")
print(f"  Total Pay: ${pay_calc['total_pay']:.2f}")
print(f"  Total Hours: {pay_calc['total_hours']:.2f}")
print(f"  Confidence: {pay_calc['confidence_score']:.2%}")
print(f"  Status: {pay_calc['status']}")

# Print breakdown
breakdown = pay_calc['breakdown']
print(f"\nBreakdown:")
print(f"  Flight Pay: ${breakdown['flight_pay']:.2f}")
print(f"  Per Diem: ${breakdown['per_diem']:.2f}")
print(f"  Premium Pay: ${breakdown['premium_pay']:.2f}")

# 5. File a claim if needed
if pay_calc['confidence_score'] < 0.9:
    claim = requests.post(
        f"{BASE_URL}/api/v1/claims/file",
        json={
            "employee_id": "P12345",
            "claim_type": "other",
            "description": "Low confidence calculation - needs review",
            "amount_claimed": 0.00
        }
    ).json()
    print(f"\nClaim Filed: {claim['claim_number']}")
```

### Batch Processing Example

```python
import requests
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000"

def calculate_pay(employee_id):
    """Calculate pay for one crew member."""
    response = requests.post(
        f"{BASE_URL}/api/v1/calculations/process",
        json={
            "employee_id": employee_id,
            "pay_period_start": "2025-11-01",
            "pay_period_end": "2025-11-15"
        }
    )
    return response.json()

# Get all crew members
crew_list = requests.get(f"{BASE_URL}/api/v1/crew").json()
employee_ids = [crew['employee_id'] for crew in crew_list]

# Process in parallel (max 5 concurrent)
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(calculate_pay, employee_ids))

# Summary
total_payroll = sum(r['total_pay'] for r in results)
needs_review = sum(1 for r in results if r['requires_human_review'])

print(f"Processed: {len(results)} crew members")
print(f"Total Payroll: ${total_payroll:,.2f}")
print(f"Needs Review: {needs_review}")
```

### Error Handling Example

```python
import requests

def calculate_pay_safe(employee_id, start_date, end_date):
    """Calculate pay with error handling."""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/calculations/process",
            json={
                "employee_id": employee_id,
                "pay_period_start": start_date,
                "pay_period_end": end_date
            },
            timeout=30  # 30 second timeout
        )

        response.raise_for_status()  # Raise exception for 4xx/5xx

        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Crew member {employee_id} not found")
        elif e.response.status_code == 422:
            print(f"Validation error: {e.response.json()}")
        else:
            print(f"HTTP error: {e}")
        return None

    except requests.exceptions.Timeout:
        print(f"Request timeout for {employee_id}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage
result = calculate_pay_safe("P12345", "2025-11-01", "2025-11-15")
if result:
    print(f"Total Pay: ${result['total_pay']:.2f}")
```

---

## Appendix: Quick Reference

### Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/api/v1/crew/{employee_id}` | Get crew member |
| GET | `/api/v1/crew` | List crew members |
| GET | `/api/v1/crew/{employee_id}/flights` | Get flights |
| POST | `/api/v1/calculations/process` | Calculate pay ⭐ |
| POST | `/api/v1/claims/file` | File claim |
| GET | `/api/v1/claims/{claim_id}` | Get claim status |

### Common Response Codes

- ✅ **200**: Success
- ❌ **404**: Not found
- ❌ **422**: Validation error
- ❌ **500**: Server error

### Testing

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

---

**END OF API REFERENCE**

For complete code documentation, see: `docs/CODE_DOCUMENTATION.md`
For usage examples, see: `docs/USAGE.md`
For setup instructions, see: `docs/SETUP.md`
