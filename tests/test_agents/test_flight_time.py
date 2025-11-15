"""
Test Flight Time Calculator Agent
"""

import pytest
from agents.core.flight_time_calculator import FlightTimeCalculator
from tests.fixtures.sample_data import SAMPLE_CREW_MEMBER, SAMPLE_FLIGHTS


@pytest.fixture
def flight_time_agent():
    """Create FlightTimeCalculator instance."""
    return FlightTimeCalculator()


def test_flight_time_calculator_initialization(flight_time_agent):
    """Test that agent initializes correctly."""
    assert flight_time_agent.agent_name == "FlightTimeCalculator"
    assert flight_time_agent.temperature == 0.1
    assert flight_time_agent.client is not None


def test_flight_time_with_no_flights(flight_time_agent):
    """Test calculation with no flights."""
    result = flight_time_agent.calculate(
        {
            "crew_member_data": SAMPLE_CREW_MEMBER,
            "flight_assignments": [],
            "execution_id": "test-123",
        }
    )

    assert result["totals"]["total_flights"] == 0
    assert result["totals"]["total_actual_hours"] == 0.0
    assert result["totals"]["total_credit_hours"] == 0.0


def test_prepare_flight_data(flight_time_agent):
    """Test flight data preparation."""
    formatted = flight_time_agent._prepare_flight_data(
        SAMPLE_FLIGHTS, SAMPLE_CREW_MEMBER
    )

    assert "Flight 1:" in formatted
    assert "Flight 2:" in formatted
    assert "XP101" in formatted
    assert "XP102" in formatted
    assert "BUR" in formatted
    assert "PDX" in formatted


# Note: Full integration tests with Claude API require ANTHROPIC_API_KEY
# and would make actual API calls. These are marked as integration tests.

@pytest.mark.integration
def test_flight_time_calculation_full(flight_time_agent):
    """
    Full integration test with Claude API.
    Requires ANTHROPIC_API_KEY environment variable.
    """
    result = flight_time_agent.calculate(
        {
            "crew_member_data": SAMPLE_CREW_MEMBER,
            "flight_assignments": SAMPLE_FLIGHTS,
            "execution_id": "test-integration-123",
        }
    )

    # Validate result structure
    assert "flights" in result
    assert "totals" in result
    assert "discrepancies" in result
    assert "confidence_score" in result

    # Validate totals
    totals = result["totals"]
    assert totals["total_flights"] > 0
    assert totals["total_credit_hours"] > 0
    assert totals["total_flight_pay"] > 0
    assert totals["hourly_rate"] == SAMPLE_CREW_MEMBER["hourly_rate"]
