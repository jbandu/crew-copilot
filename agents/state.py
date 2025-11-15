"""
State management for LangGraph orchestration.

Defines the CrewPayState that flows through all agents.
"""

from typing import TypedDict, Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime


class CrewPayState(TypedDict):
    """State object passed between agents in the LangGraph workflow."""

    # Core identifiers
    crew_member_id: str
    employee_id: str
    pay_period_start: str
    pay_period_end: str
    execution_id: str

    # Crew member info
    crew_member_data: Optional[Dict[str, Any]]

    # Flight data
    flight_assignments: List[Dict[str, Any]]

    # Agent outputs
    flight_time_data: Optional[Dict[str, Any]]
    duty_time_data: Optional[Dict[str, Any]]
    per_diem_data: Optional[Dict[str, Any]]
    premium_pay_data: Optional[Dict[str, Any]]
    guarantee_data: Optional[Dict[str, Any]]
    compliance_status: Optional[Dict[str, Any]]
    claims_data: Optional[Dict[str, Any]]

    # Final results
    total_pay: Optional[float]
    total_hours: Optional[float]
    breakdown: Optional[Dict[str, Any]]

    # Workflow control
    status: str  # "processing", "complete", "needs_review", "error"
    error_log: List[str]
    warnings: List[str]
    requires_human_review: bool
    confidence_score: float

    # Metadata
    processing_started_at: Optional[str]
    processing_completed_at: Optional[str]
