"""
Pydantic Schemas

Request and response schemas for the API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field


# Crew Member Schemas
class CrewMemberBase(BaseModel):
    """Base crew member schema."""

    employee_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    base_airport: Optional[str] = None
    role: str
    crew_type: str
    hourly_rate: Decimal
    monthly_guarantee: Optional[Decimal] = None


class CrewMemberCreate(CrewMemberBase):
    """Create crew member schema."""

    hire_date: date
    seniority_date: Optional[date] = None


class CrewMemberResponse(CrewMemberBase):
    """Crew member response schema."""

    id: str
    hire_date: date
    seniority_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Flight Assignment Schemas
class FlightAssignmentBase(BaseModel):
    """Base flight assignment schema."""

    flight_number: str
    flight_date: date
    origin_airport: str
    destination_airport: str
    scheduled_departure: datetime
    scheduled_arrival: datetime


class FlightAssignmentResponse(FlightAssignmentBase):
    """Flight assignment response schema."""

    id: str
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    scheduled_block_time: Optional[Decimal] = None
    actual_block_time: Optional[Decimal] = None
    position: Optional[str] = None
    overnight_location: Optional[str] = None
    is_international: bool = False
    is_redeye: bool = False

    class Config:
        from_attributes = True


# Pay Calculation Schemas
class PayCalculationRequest(BaseModel):
    """Request to calculate crew pay."""

    employee_id: str = Field(..., description="Crew member employee ID")
    pay_period_start: str = Field(..., description="Pay period start date (YYYY-MM-DD)")
    pay_period_end: str = Field(..., description="Pay period end date (YYYY-MM-DD)")


class PayBreakdown(BaseModel):
    """Pay breakdown details."""

    base_pay: float
    flight_pay: float
    guarantee_pay: float
    per_diem: float
    premium_pay: float
    total_pay: float


class PayCalculationResponse(BaseModel):
    """Pay calculation response."""

    execution_id: str
    employee_id: str
    pay_period_start: str
    pay_period_end: str
    status: str
    total_pay: Optional[float] = None
    total_hours: Optional[float] = None
    breakdown: Optional[PayBreakdown] = None
    confidence_score: float
    requires_human_review: bool
    warnings: List[str] = []
    processing_time_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class PayCalculationDetail(BaseModel):
    """Detailed pay calculation results."""

    calculation_id: str
    employee_id: str
    pay_period_start: str
    pay_period_end: str
    total_pay: float
    total_hours: float
    breakdown: PayBreakdown
    flight_time_data: Optional[Dict[str, Any]] = None
    duty_time_data: Optional[Dict[str, Any]] = None
    per_diem_data: Optional[Dict[str, Any]] = None
    premium_pay_data: Optional[Dict[str, Any]] = None
    guarantee_data: Optional[Dict[str, Any]] = None
    compliance_status: Optional[Dict[str, Any]] = None
    confidence_score: float
    requires_human_review: bool


# Claim Schemas
class ClaimCreate(BaseModel):
    """Create a claim."""

    employee_id: str
    claim_type: str
    description: str
    amount_claimed: Optional[Decimal] = None
    flight_number: Optional[str] = None
    flight_date: Optional[date] = None


class ClaimResponse(BaseModel):
    """Claim response schema."""

    id: str
    claim_number: str
    employee_id: str
    claim_type: str
    description: str
    amount_claimed: Optional[Decimal] = None
    amount_approved: Optional[Decimal] = None
    status: str
    filed_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True


# Error Response
class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health Check
class HealthCheck(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    agents_available: bool = True
    database_connected: bool = True
