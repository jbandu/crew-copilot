"""
SQLAlchemy ORM Models

Defines database models for Crew Copilot.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Numeric,
    Boolean,
    Date,
    DateTime,
    Time,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class CrewMember(Base):
    """Crew member profile."""

    __tablename__ = "crew_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    base_airport = Column(String(3), index=True)
    role = Column(String(50), nullable=False, index=True)
    seniority_date = Column(Date)
    hire_date = Column(Date, nullable=False)
    hourly_rate = Column(Numeric(10, 2), nullable=False)
    crew_type = Column(String(20), nullable=False)
    monthly_guarantee = Column(Numeric(5, 2))
    contract_id = Column(UUID(as_uuid=True))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    flight_assignments = relationship("FlightAssignment", back_populates="crew_member")
    pay_calculations = relationship("PayCalculation", back_populates="crew_member")
    claims = relationship("Claim", back_populates="crew_member")

    __table_args__ = (
        CheckConstraint(
            crew_type.in_(["line_holder", "reserve"]), name="valid_crew_type"
        ),
        CheckConstraint(
            role.in_(
                ["Captain", "First Officer", "Flight Attendant", "Lead Flight Attendant"]
            ),
            name="valid_role",
        ),
    )


class FlightAssignment(Base):
    """Flight assignment for a crew member."""

    __tablename__ = "flight_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crew_member_id = Column(
        UUID(as_uuid=True), ForeignKey("crew_members.id", ondelete="CASCADE"), index=True
    )
    flight_number = Column(String(20), nullable=False, index=True)
    flight_date = Column(Date, nullable=False, index=True)
    origin_airport = Column(String(3), nullable=False)
    destination_airport = Column(String(3), nullable=False)
    scheduled_departure = Column(DateTime, nullable=False)
    actual_departure = Column(DateTime)
    scheduled_arrival = Column(DateTime, nullable=False)
    actual_arrival = Column(DateTime)
    scheduled_block_time = Column(Numeric(5, 2))
    actual_block_time = Column(Numeric(5, 2))
    duty_report_time = Column(DateTime)
    duty_end_time = Column(DateTime)
    flight_duty_period = Column(Numeric(5, 2))
    aircraft_type = Column(String(20))
    position = Column(String(50))
    overnight_location = Column(String(3))
    is_international = Column(Boolean, default=False)
    is_redeye = Column(Boolean, default=False)
    is_deadhead = Column(Boolean, default=False)
    trip_id = Column(String(50), index=True)
    sequence_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    crew_member = relationship("CrewMember", back_populates="flight_assignments")
    pay_calculations = relationship("PayCalculation", back_populates="flight_assignment")


class PayCalculation(Base):
    """Pay calculation record."""

    __tablename__ = "pay_calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crew_member_id = Column(
        UUID(as_uuid=True), ForeignKey("crew_members.id", ondelete="CASCADE"), index=True
    )
    pay_period_start = Column(Date, nullable=False, index=True)
    pay_period_end = Column(Date, nullable=False, index=True)
    flight_assignment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("flight_assignments.id", ondelete="SET NULL"),
    )
    calculation_type = Column(String(50), nullable=False, index=True)
    base_hours = Column(Numeric(10, 4))
    credit_hours = Column(Numeric(10, 4))
    rate = Column(Numeric(10, 2))
    amount = Column(Numeric(10, 2), nullable=False)
    calculation_details = Column(JSONB)
    calculated_by_agent = Column(String(100))
    confidence_score = Column(Numeric(5, 4), default=1.0)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    crew_member = relationship("CrewMember", back_populates="pay_calculations")
    flight_assignment = relationship("FlightAssignment", back_populates="pay_calculations")

    __table_args__ = (
        CheckConstraint(
            calculation_type.in_(
                [
                    "flight_pay",
                    "per_diem",
                    "premium_overtime",
                    "premium_holiday",
                    "premium_redeye",
                    "premium_international",
                    "premium_training",
                    "guarantee",
                    "deadhead",
                    "cancellation",
                ]
            ),
            name="valid_calculation_type",
        ),
    )


class Claim(Base):
    """Crew member pay claim."""

    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    crew_member_id = Column(
        UUID(as_uuid=True), ForeignKey("crew_members.id", ondelete="CASCADE"), index=True
    )
    flight_assignment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("flight_assignments.id", ondelete="SET NULL"),
    )
    claim_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    amount_claimed = Column(Numeric(10, 2))
    amount_approved = Column(Numeric(10, 2))
    status = Column(String(50), default="filed", index=True)
    filed_via = Column(String(20), default="system")
    auto_detected = Column(Boolean, default=False)
    agent_analysis = Column(JSONB)
    supporting_documents = Column(JSONB)
    assigned_to = Column(String(100))
    resolution_notes = Column(Text)
    filed_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    resolved_at = Column(DateTime)
    paid_at = Column(DateTime)

    # Relationships
    crew_member = relationship("CrewMember", back_populates="claims")

    __table_args__ = (
        CheckConstraint(
            status.in_(
                ["filed", "investigating", "approved", "rejected", "paid", "withdrawn"]
            ),
            name="valid_claim_status",
        ),
        CheckConstraint(
            claim_type.in_(
                [
                    "missing_flight_time",
                    "incorrect_block_time",
                    "missing_premium",
                    "per_diem_error",
                    "guarantee_not_applied",
                    "duty_violation",
                    "other",
                ]
            ),
            name="valid_claim_type",
        ),
    )


class AgentExecutionLog(Base):
    """Audit log for agent executions."""

    __tablename__ = "agent_execution_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String(100), nullable=False, index=True)
    execution_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    crew_member_id = Column(UUID(as_uuid=True), ForeignKey("crew_members.id", ondelete="SET NULL"))
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    execution_time_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class PayPeriod(Base):
    """Pay period definition."""

    __tablename__ = "pay_periods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    period_number = Column(Integer, nullable=False)
    status = Column(String(20), default="open")
    closed_at = Column(DateTime)
    paid_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("year", "period_number", name="unique_period"),
        CheckConstraint(status.in_(["open", "closed", "paid"]), name="valid_period_status"),
    )


class PerDiemRate(Base):
    """Per diem rates by city."""

    __tablename__ = "per_diem_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city = Column(String(100), nullable=False, index=True)
    state_country = Column(String(100))
    airport_code = Column(String(3), index=True)
    rate = Column(Numeric(10, 2), nullable=False)
    is_international = Column(Boolean, default=False)
    effective_date = Column(Date, nullable=False, index=True)
    expiration_date = Column(Date, index=True)
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
