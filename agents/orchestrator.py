"""
Crew Pay Orchestration Agent

Master coordinator using LangGraph to manage workflow across all agents.
"""

import os
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from .state import CrewPayState
from .core import (
    FlightTimeCalculator,
    DutyTimeMonitor,
    PerDiemCalculator,
    PremiumPayCalculator,
    GuaranteeCalculator,
    ComplianceValidator,
    ClaimResolutionAgent,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class CrewPayOrchestrator:
    """
    Master orchestrator for crew pay calculations using LangGraph.

    Coordinates all 7 specialized agents in the correct sequence.
    """

    def __init__(self):
        """Initialize the orchestrator and all agents."""
        self.flight_time_agent = FlightTimeCalculator()
        self.duty_time_agent = DutyTimeMonitor()
        self.per_diem_agent = PerDiemCalculator()
        self.premium_pay_agent = PremiumPayCalculator()
        self.guarantee_agent = GuaranteeCalculator()
        self.compliance_agent = ComplianceValidator()
        self.claim_resolution_agent = ClaimResolutionAgent()

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        Workflow:
        Entry → Flight Time → Duty Time → Per Diem → Premium →
        Guarantee → Compliance → [Pass → Claims / Fail → Human Review] → End
        """
        workflow = StateGraph(CrewPayState)

        # Add nodes for each agent
        workflow.add_node("flight_time", self._calculate_flight_time)
        workflow.add_node("duty_time", self._monitor_duty_time)
        workflow.add_node("per_diem", self._calculate_per_diem)
        workflow.add_node("premium_pay", self._calculate_premium_pay)
        workflow.add_node("guarantee", self._calculate_guarantee)
        workflow.add_node("compliance", self._validate_compliance)
        workflow.add_node("claims", self._process_claims)
        workflow.add_node("finalize", self._finalize_results)

        # Define edges (workflow sequence)
        workflow.set_entry_point("flight_time")
        workflow.add_edge("flight_time", "duty_time")
        workflow.add_edge("duty_time", "per_diem")
        workflow.add_edge("per_diem", "premium_pay")
        workflow.add_edge("premium_pay", "guarantee")
        workflow.add_edge("guarantee", "compliance")

        # Conditional edge from compliance
        workflow.add_conditional_edges(
            "compliance",
            self._route_after_compliance,
            {
                "claims": "claims",
                "finalize": "finalize",
                "needs_review": "finalize",
            },
        )

        workflow.add_edge("claims", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def _calculate_flight_time(self, state: CrewPayState) -> CrewPayState:
        """Execute Flight Time Calculator agent."""
        logger.info("Executing Flight Time Calculator...")

        try:
            result = self.flight_time_agent.calculate(
                {
                    "crew_member_data": state["crew_member_data"],
                    "flight_assignments": state["flight_assignments"],
                    "execution_id": state["execution_id"],
                }
            )

            state["flight_time_data"] = result
            state["status"] = "processing"
            logger.info(
                f"Flight Time calculated: {result.get('totals', {}).get('total_credit_hours', 0)} hours"
            )

        except Exception as e:
            logger.error(f"Flight Time calculation error: {str(e)}")
            state["error_log"].append(f"Flight Time Error: {str(e)}")
            state["status"] = "error"

        return state

    def _monitor_duty_time(self, state: CrewPayState) -> CrewPayState:
        """Execute Duty Time Monitor agent."""
        logger.info("Executing Duty Time Monitor...")

        try:
            result = self.duty_time_agent.calculate(
                {
                    "crew_member_data": state["crew_member_data"],
                    "flight_assignments": state["flight_assignments"],
                    "execution_id": state["execution_id"],
                }
            )

            state["duty_time_data"] = result
            logger.info(
                f"Duty Time compliance: {result.get('compliance_status', 'unknown')}"
            )

            # Flag violations
            if result.get("violations"):
                state["warnings"].append(
                    f"Duty time violations detected: {len(result['violations'])}"
                )

        except Exception as e:
            logger.error(f"Duty Time monitoring error: {str(e)}")
            state["error_log"].append(f"Duty Time Error: {str(e)}")

        return state

    def _calculate_per_diem(self, state: CrewPayState) -> CrewPayState:
        """Execute Per Diem Calculator agent."""
        logger.info("Executing Per Diem Calculator...")

        try:
            # Note: In production, fetch per_diem_rates from database
            result = self.per_diem_agent.calculate(
                {
                    "crew_member_data": state["crew_member_data"],
                    "flight_assignments": state["flight_assignments"],
                    "per_diem_rates": {},  # Would be loaded from DB
                    "execution_id": state["execution_id"],
                }
            )

            state["per_diem_data"] = result
            logger.info(
                f"Per Diem calculated: ${result.get('totals', {}).get('total_net_per_diem', 0)}"
            )

        except Exception as e:
            logger.error(f"Per Diem calculation error: {str(e)}")
            state["error_log"].append(f"Per Diem Error: {str(e)}")

        return state

    def _calculate_premium_pay(self, state: CrewPayState) -> CrewPayState:
        """Execute Premium Pay Calculator agent."""
        logger.info("Executing Premium Pay Calculator...")

        try:
            result = self.premium_pay_agent.calculate(
                {
                    "crew_member_data": state["crew_member_data"],
                    "flight_assignments": state["flight_assignments"],
                    "flight_time_data": state["flight_time_data"],
                    "premium_rules": {},  # Would be loaded from DB
                    "execution_id": state["execution_id"],
                }
            )

            state["premium_pay_data"] = result
            logger.info(
                f"Premium Pay calculated: ${result.get('totals', {}).get('total_premium_pay', 0)}"
            )

        except Exception as e:
            logger.error(f"Premium Pay calculation error: {str(e)}")
            state["error_log"].append(f"Premium Pay Error: {str(e)}")

        return state

    def _calculate_guarantee(self, state: CrewPayState) -> CrewPayState:
        """Execute Guarantee Calculator agent."""
        logger.info("Executing Guarantee Calculator...")

        try:
            result = self.guarantee_agent.calculate(
                {
                    "crew_member_data": state["crew_member_data"],
                    "flight_time_data": state["flight_time_data"],
                    "pay_period_start": state["pay_period_start"],
                    "pay_period_end": state["pay_period_end"],
                    "execution_id": state["execution_id"],
                }
            )

            state["guarantee_data"] = result
            logger.info(
                f"Guarantee calculated: {result.get('paid_hours', 0)} hours paid"
            )

        except Exception as e:
            logger.error(f"Guarantee calculation error: {str(e)}")
            state["error_log"].append(f"Guarantee Error: {str(e)}")

        return state

    def _validate_compliance(self, state: CrewPayState) -> CrewPayState:
        """Execute Compliance Validator agent."""
        logger.info("Executing Compliance Validator...")

        try:
            result = self.compliance_agent.calculate(
                {
                    "crew_member_data": state["crew_member_data"],
                    "flight_time_data": state["flight_time_data"],
                    "duty_time_data": state["duty_time_data"],
                    "per_diem_data": state["per_diem_data"],
                    "premium_pay_data": state["premium_pay_data"],
                    "guarantee_data": state["guarantee_data"],
                    "execution_id": state["execution_id"],
                }
            )

            state["compliance_status"] = result
            state["requires_human_review"] = result.get("requires_human_review", False)

            logger.info(
                f"Compliance validation: {result.get('overall_compliance', 'unknown')}"
            )

        except Exception as e:
            logger.error(f"Compliance validation error: {str(e)}")
            state["error_log"].append(f"Compliance Error: {str(e)}")
            state["requires_human_review"] = True

        return state

    def _process_claims(self, state: CrewPayState) -> CrewPayState:
        """Execute Claim Resolution agent if needed."""
        logger.info("Processing claims (if any)...")

        # Note: In production, this would check for existing claims
        # For now, just log that we checked
        state["claims_data"] = {"claims_processed": 0}

        return state

    def _finalize_results(self, state: CrewPayState) -> CrewPayState:
        """Finalize and calculate total pay."""
        logger.info("Finalizing results...")

        try:
            # Calculate total pay
            flight_pay = state["flight_time_data"].get("totals", {}).get(
                "total_flight_pay", 0
            )
            per_diem = state["per_diem_data"].get("totals", {}).get(
                "total_net_per_diem", 0
            )
            premium_pay = state["premium_pay_data"].get("totals", {}).get(
                "total_premium_pay", 0
            )
            guarantee_pay = state["guarantee_data"].get("calculation", {}).get(
                "base_pay", 0
            )

            # Use the greater of flight_pay or guarantee_pay as base
            base_pay = max(flight_pay, guarantee_pay)

            total_pay = base_pay + per_diem + premium_pay

            state["total_pay"] = total_pay
            state["total_hours"] = state["flight_time_data"].get("totals", {}).get(
                "total_credit_hours", 0
            )
            state["breakdown"] = {
                "base_pay": base_pay,
                "flight_pay": flight_pay,
                "guarantee_pay": guarantee_pay,
                "per_diem": per_diem,
                "premium_pay": premium_pay,
                "total_pay": total_pay,
            }

            # Calculate confidence score
            flight_confidence = state["flight_time_data"].get("confidence_score", 1.0)
            duty_confidence = state["duty_time_data"].get("confidence_score", 1.0)
            per_diem_confidence = state["per_diem_data"].get("confidence_score", 1.0)
            premium_confidence = state["premium_pay_data"].get("confidence_score", 1.0)
            guarantee_confidence = state["guarantee_data"].get("confidence_score", 1.0)
            compliance_confidence = state["compliance_status"].get(
                "confidence_score", 1.0
            )

            state["confidence_score"] = min(
                flight_confidence,
                duty_confidence,
                per_diem_confidence,
                premium_confidence,
                guarantee_confidence,
                compliance_confidence,
            )

            state["status"] = "complete"
            state["processing_completed_at"] = datetime.now().isoformat()

            logger.info(f"Final total pay: ${total_pay:.2f}")
            logger.info(f"Confidence score: {state['confidence_score']:.2f}")

        except Exception as e:
            logger.error(f"Finalization error: {str(e)}")
            state["error_log"].append(f"Finalization Error: {str(e)}")
            state["status"] = "error"

        return state

    def _route_after_compliance(self, state: CrewPayState) -> str:
        """Decide routing after compliance check."""
        compliance_status = state["compliance_status"].get("overall_compliance")

        if state["requires_human_review"]:
            return "needs_review"
        elif compliance_status == "fail":
            return "needs_review"
        elif state.get("claims_data"):  # If there are claims to process
            return "claims"
        else:
            return "finalize"

    def process(
        self,
        crew_member_data: Dict[str, Any],
        flight_assignments: list,
        pay_period_start: str,
        pay_period_end: str,
    ) -> CrewPayState:
        """
        Process crew pay calculations.

        Args:
            crew_member_data: Crew member profile
            flight_assignments: List of flight assignments
            pay_period_start: Start date (YYYY-MM-DD)
            pay_period_end: End date (YYYY-MM-DD)

        Returns:
            Final state with all calculations
        """
        execution_id = str(uuid.uuid4())

        logger.info(
            f"Starting crew pay processing for {crew_member_data.get('employee_id')}"
        )
        logger.info(f"Execution ID: {execution_id}")

        # Initialize state
        initial_state: CrewPayState = {
            "crew_member_id": crew_member_data.get("id", ""),
            "employee_id": crew_member_data.get("employee_id", ""),
            "pay_period_start": pay_period_start,
            "pay_period_end": pay_period_end,
            "execution_id": execution_id,
            "crew_member_data": crew_member_data,
            "flight_assignments": flight_assignments,
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
            "processing_started_at": datetime.now().isoformat(),
            "processing_completed_at": None,
        }

        # Run workflow
        final_state = self.workflow.invoke(initial_state)

        logger.info(f"Processing complete. Status: {final_state['status']}")

        return final_state


def run_crew_pay_workflow(
    crew_member_id: str, pay_period: str, db_connection: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Convenience function to run the complete workflow.

    Args:
        crew_member_id: Employee ID (e.g., "P12345")
        pay_period: Pay period string (e.g., "2025-11-01 to 2025-11-15")
        db_connection: Database connection (optional, for production)

    Returns:
        Dictionary with final results
    """
    # Parse pay period
    period_parts = pay_period.split(" to ")
    if len(period_parts) != 2:
        raise ValueError(
            "Invalid pay period format. Use: 'YYYY-MM-DD to YYYY-MM-DD'"
        )

    pay_period_start, pay_period_end = period_parts

    # Mock data for demonstration
    # In production, fetch from database
    crew_member_data = {
        "id": "uuid-here",
        "employee_id": crew_member_id,
        "first_name": "Sarah",
        "last_name": "Chen",
        "role": "Captain",
        "crew_type": "line_holder",
        "hourly_rate": 105.00,
        "base_airport": "BUR",
    }

    flight_assignments = [
        {
            "flight_number": "XP101",
            "flight_date": "2025-11-03",
            "origin_airport": "BUR",
            "destination_airport": "PDX",
            "scheduled_departure": "2025-11-03 22:30:00",
            "actual_departure": "2025-11-03 22:45:00",
            "scheduled_arrival": "2025-11-04 01:15:00",
            "actual_arrival": "2025-11-04 01:20:00",
            "scheduled_block_time": 2.75,
            "actual_block_time": 2.58,
            "duty_report_time": "2025-11-03 21:30:00",
            "duty_end_time": "2025-11-04 02:00:00",
            "flight_duty_period": 4.50,
            "position": "captain",
            "overnight_location": "PDX",
            "is_redeye": True,
            "is_international": False,
            "trip_id": "TRIP-001",
            "sequence_number": 1,
        },
        # Add more flights as needed
    ]

    # Create orchestrator and run
    orchestrator = CrewPayOrchestrator()
    result = orchestrator.process(
        crew_member_data=crew_member_data,
        flight_assignments=flight_assignments,
        pay_period_start=pay_period_start,
        pay_period_end=pay_period_end,
    )

    return result


if __name__ == "__main__":
    # Test the workflow
    print("Testing Crew Pay Workflow...")
    print("=" * 80)

    result = run_crew_pay_workflow(
        crew_member_id="P12345", pay_period="2025-11-01 to 2025-11-15"
    )

    print(f"\nExecution ID: {result['execution_id']}")
    print(f"Status: {result['status']}")
    print(f"Total Pay: ${result.get('total_pay', 0):.2f}")
    print(f"Total Hours: {result.get('total_hours', 0):.2f}")
    print(f"Confidence: {result['confidence_score']:.2%}")
    print(f"Requires Review: {result['requires_human_review']}")

    if result.get("breakdown"):
        print("\nPay Breakdown:")
        for key, value in result["breakdown"].items():
            print(f"  {key}: ${value:.2f}")

    if result.get("error_log"):
        print("\nErrors:")
        for error in result["error_log"]:
            print(f"  - {error}")

    if result.get("warnings"):
        print("\nWarnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
