"""
Crew Copilot FastAPI Application

Main API application for crew pay calculations.
"""

import time
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .config import settings
from .models import Base, CrewMember, FlightAssignment, Claim, PayCalculation
from .schemas import (
    CrewMemberResponse,
    FlightAssignmentResponse,
    PayCalculationRequest,
    PayCalculationResponse,
    PayBreakdown,
    ClaimCreate,
    ClaimResponse,
    HealthCheck,
    ErrorResponse,
)

from agents.orchestrator import CrewPayOrchestrator

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize orchestrator
orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    global orchestrator
    # Startup
    print("Initializing Crew Pay Orchestrator...")
    orchestrator = CrewPayOrchestrator()
    print("Orchestrator initialized successfully!")
    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Check API health status."""
    db_connected = True
    try:
        db.execute("SELECT 1")
    except Exception:
        db_connected = False

    return HealthCheck(
        status="healthy" if db_connected else "unhealthy",
        database_connected=db_connected,
        agents_available=orchestrator is not None,
    )


# Crew endpoints
@app.get(
    "/api/v1/crew/{employee_id}",
    response_model=CrewMemberResponse,
    tags=["Crew"],
)
async def get_crew_member(employee_id: str, db: Session = Depends(get_db)):
    """Get crew member by employee ID."""
    crew_member = (
        db.query(CrewMember).filter(CrewMember.employee_id == employee_id).first()
    )

    if not crew_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew member {employee_id} not found",
        )

    return crew_member


@app.get("/api/v1/crew", response_model=List[CrewMemberResponse], tags=["Crew"])
async def list_crew_members(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """List all crew members."""
    crew_members = db.query(CrewMember).offset(skip).limit(limit).all()
    return crew_members


# Flight assignments endpoint
@app.get(
    "/api/v1/crew/{employee_id}/flights",
    response_model=List[FlightAssignmentResponse],
    tags=["Flights"],
)
async def get_crew_flights(
    employee_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get flight assignments for a crew member."""
    crew_member = (
        db.query(CrewMember).filter(CrewMember.employee_id == employee_id).first()
    )

    if not crew_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew member {employee_id} not found",
        )

    query = db.query(FlightAssignment).filter(
        FlightAssignment.crew_member_id == crew_member.id
    )

    if start_date:
        query = query.filter(FlightAssignment.flight_date >= start_date)
    if end_date:
        query = query.filter(FlightAssignment.flight_date <= end_date)

    flights = query.order_by(FlightAssignment.flight_date).all()
    return flights


# Pay calculation endpoint
@app.post(
    "/api/v1/calculations/process",
    response_model=PayCalculationResponse,
    tags=["Calculations"],
)
async def process_pay_calculation(
    request: PayCalculationRequest, db: Session = Depends(get_db)
):
    """
    Process crew pay calculation for a pay period.

    This endpoint orchestrates all 8 AI agents to calculate complete crew pay.
    """
    start_time = time.time()

    # Get crew member
    crew_member = (
        db.query(CrewMember)
        .filter(CrewMember.employee_id == request.employee_id)
        .first()
    )

    if not crew_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew member {request.employee_id} not found",
        )

    # Get flight assignments for period
    flights = (
        db.query(FlightAssignment)
        .filter(FlightAssignment.crew_member_id == crew_member.id)
        .filter(FlightAssignment.flight_date >= request.pay_period_start)
        .filter(FlightAssignment.flight_date <= request.pay_period_end)
        .all()
    )

    # Convert to dictionaries
    crew_data = {
        "id": str(crew_member.id),
        "employee_id": crew_member.employee_id,
        "first_name": crew_member.first_name,
        "last_name": crew_member.last_name,
        "role": crew_member.role,
        "crew_type": crew_member.crew_type,
        "hourly_rate": float(crew_member.hourly_rate),
        "base_airport": crew_member.base_airport,
        "monthly_guarantee": float(crew_member.monthly_guarantee or 0),
    }

    flight_data = [
        {
            "flight_number": f.flight_number,
            "flight_date": str(f.flight_date),
            "origin_airport": f.origin_airport,
            "destination_airport": f.destination_airport,
            "scheduled_departure": str(f.scheduled_departure),
            "actual_departure": str(f.actual_departure) if f.actual_departure else None,
            "scheduled_arrival": str(f.scheduled_arrival),
            "actual_arrival": str(f.actual_arrival) if f.actual_arrival else None,
            "scheduled_block_time": float(f.scheduled_block_time or 0),
            "actual_block_time": float(f.actual_block_time or 0),
            "duty_report_time": str(f.duty_report_time) if f.duty_report_time else None,
            "duty_end_time": str(f.duty_end_time) if f.duty_end_time else None,
            "flight_duty_period": float(f.flight_duty_period or 0),
            "position": f.position,
            "overnight_location": f.overnight_location,
            "is_international": f.is_international,
            "is_redeye": f.is_redeye,
            "is_deadhead": f.is_deadhead,
            "trip_id": f.trip_id,
            "sequence_number": f.sequence_number,
        }
        for f in flights
    ]

    # Run orchestrator
    try:
        result = orchestrator.process(
            crew_member_data=crew_data,
            flight_assignments=flight_data,
            pay_period_start=request.pay_period_start,
            pay_period_end=request.pay_period_end,
        )

        processing_time = time.time() - start_time

        # Build response
        breakdown = None
        if result.get("breakdown"):
            breakdown = PayBreakdown(**result["breakdown"])

        return PayCalculationResponse(
            execution_id=result["execution_id"],
            employee_id=request.employee_id,
            pay_period_start=request.pay_period_start,
            pay_period_end=request.pay_period_end,
            status=result["status"],
            total_pay=result.get("total_pay"),
            total_hours=result.get("total_hours"),
            breakdown=breakdown,
            confidence_score=result["confidence_score"],
            requires_human_review=result["requires_human_review"],
            warnings=result.get("warnings", []),
            processing_time_seconds=round(processing_time, 2),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing pay calculation: {str(e)}",
        )


# Claims endpoints
@app.post("/api/v1/claims/file", response_model=ClaimResponse, tags=["Claims"])
async def file_claim(claim: ClaimCreate, db: Session = Depends(get_db)):
    """File a new pay claim."""
    # Get crew member
    crew_member = (
        db.query(CrewMember)
        .filter(CrewMember.employee_id == claim.employee_id)
        .first()
    )

    if not crew_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew member {claim.employee_id} not found",
        )

    # Generate claim number
    claim_number = f"CLM-{datetime.now().strftime('%Y%m%d')}-{crew_member.employee_id}"

    # Create claim
    new_claim = Claim(
        claim_number=claim_number,
        crew_member_id=crew_member.id,
        claim_type=claim.claim_type,
        description=claim.description,
        amount_claimed=claim.amount_claimed,
        status="filed",
        filed_via="api",
    )

    try:
        db.add(new_claim)
        db.commit()
        db.refresh(new_claim)

        return ClaimResponse(
            id=str(new_claim.id),
            claim_number=new_claim.claim_number,
            employee_id=claim.employee_id,
            claim_type=new_claim.claim_type,
            description=new_claim.description,
            amount_claimed=new_claim.amount_claimed,
            amount_approved=new_claim.amount_approved,
            status=new_claim.status,
            filed_at=new_claim.filed_at,
            resolved_at=new_claim.resolved_at,
            resolution_notes=new_claim.resolution_notes,
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error filing claim: {str(e)}",
        )


@app.get("/api/v1/claims/{claim_id}", response_model=ClaimResponse, tags=["Claims"])
async def get_claim(claim_id: str, db: Session = Depends(get_db)):
    """Get claim by ID or claim number."""
    # Try by ID first, then by claim number
    claim = db.query(Claim).filter(Claim.claim_number == claim_id).first()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found",
        )

    crew_member = db.query(CrewMember).filter(CrewMember.id == claim.crew_member_id).first()

    return ClaimResponse(
        id=str(claim.id),
        claim_number=claim.claim_number,
        employee_id=crew_member.employee_id if crew_member else "unknown",
        claim_type=claim.claim_type,
        description=claim.description,
        amount_claimed=claim.amount_claimed,
        amount_approved=claim.amount_approved,
        status=claim.status,
        filed_at=claim.filed_at,
        resolved_at=claim.resolved_at,
        resolution_notes=claim.resolution_notes,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.app_env == "development"),
    )
