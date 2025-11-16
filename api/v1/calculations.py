"""
Crew Pay Calculations API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.orchestrator import run_crew_pay_workflow

router = APIRouter(prefix="/calculations", tags=["calculations"])

class PayCalculationRequest(BaseModel):
    crew_member_id: str
    pay_period_start: date
    pay_period_end: date

class PayCalculationResponse(BaseModel):
    status: str
    total_pay: float
    breakdown: dict
    compliance_status: str
    requires_review: bool
    execution_id: str

@router.post("/run", response_model=PayCalculationResponse)
async def calculate_crew_pay(request: PayCalculationRequest):
    """
    Calculate crew pay for a given period
    
    Example:
```json
    {
        "crew_member_id": "P12345",
        "pay_period_start": "2025-11-01",
        "pay_period_end": "2025-11-15"
    }
```
    """
    try:
        # Run the orchestrator
        result = run_crew_pay_workflow(
            crew_member_id=request.crew_member_id,
            pay_period_start=request.pay_period_start,
            pay_period_end=request.pay_period_end
        )
        
        return PayCalculationResponse(
            status=result.get("status", "complete"),
            total_pay=result.get("total_pay", 0.0),
            breakdown=result.get("breakdown", {}),
            compliance_status=result.get("compliance_status", "unknown"),
            requires_review=result.get("requires_review", True),
            execution_id=result.get("execution_id", "")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{execution_id}")
async def get_calculation_status(execution_id: str):
    """Get status of a pay calculation"""
    # TODO: Query database for execution status
    return {
        "execution_id": execution_id,
        "status": "processing",
        "message": "Status lookup coming soon"
    }
