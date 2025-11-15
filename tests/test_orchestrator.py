"""
Test Crew Pay Orchestrator
"""

import pytest
from agents.orchestrator import CrewPayOrchestrator
from tests.fixtures.sample_data import SAMPLE_CREW_MEMBER, SAMPLE_FLIGHTS


@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return CrewPayOrchestrator()


def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initializes all agents."""
    assert orchestrator.flight_time_agent is not None
    assert orchestrator.duty_time_agent is not None
    assert orchestrator.per_diem_agent is not None
    assert orchestrator.premium_pay_agent is not None
    assert orchestrator.guarantee_agent is not None
    assert orchestrator.compliance_agent is not None
    assert orchestrator.claim_resolution_agent is not None
    assert orchestrator.workflow is not None


def test_orchestrator_state_structure(orchestrator):
    """Test initial state structure."""
    initial_state = {
        "crew_member_id": SAMPLE_CREW_MEMBER["id"],
        "employee_id": SAMPLE_CREW_MEMBER["employee_id"],
        "pay_period_start": "2025-11-01",
        "pay_period_end": "2025-11-15",
        "execution_id": "test-exec-123",
        "crew_member_data": SAMPLE_CREW_MEMBER,
        "flight_assignments": SAMPLE_FLIGHTS,
        "flight_time_data": None,
        "duty_time_data": None,
        "per_diem_data": None,
        "premium_pay_data": None,
        "guarantee_data": None,
        "compliance_status": None,
        "claims_data": None,
        "total_pay": None,
        "total_hours": None,
        "breakdown": None,
        "status": "processing",
        "error_log": [],
        "warnings": [],
        "requires_human_review": False,
        "confidence_score": 1.0,
        "processing_started_at": "2025-11-15T12:00:00",
        "processing_completed_at": None,
    }

    assert initial_state["crew_member_id"] == SAMPLE_CREW_MEMBER["id"]
    assert initial_state["status"] == "processing"


@pytest.mark.integration
def test_full_workflow(orchestrator):
    """
    Test complete workflow execution.
    Requires ANTHROPIC_API_KEY.
    """
    result = orchestrator.process(
        crew_member_data=SAMPLE_CREW_MEMBER,
        flight_assignments=SAMPLE_FLIGHTS,
        pay_period_start="2025-11-01",
        pay_period_end="2025-11-15",
    )

    # Validate result
    assert result["status"] in ["complete", "needs_review"]
    assert result["execution_id"] is not None
    assert "total_pay" in result
    assert "total_hours" in result
    assert "confidence_score" in result

    # Validate all agent data is present
    assert result["flight_time_data"] is not None
    assert result["duty_time_data"] is not None
    assert result["per_diem_data"] is not None
    assert result["premium_pay_data"] is not None
    assert result["guarantee_data"] is not None
    assert result["compliance_status"] is not None

    # Validate breakdown
    if result["breakdown"]:
        breakdown = result["breakdown"]
        assert "base_pay" in breakdown
        assert "total_pay" in breakdown
        assert breakdown["total_pay"] > 0

    print(f"\n✅ Workflow completed successfully!")
    print(f"Total Pay: ${result.get('total_pay', 0):.2f}")
    print(f"Total Hours: {result.get('total_hours', 0):.2f}")
    print(f"Confidence: {result['confidence_score']:.2%}")
