"""
Claim Dispute Resolution Agent

Automatically investigates and resolves crew pay claims.
"""

import time
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..prompts.claim_resolution_prompts import CLAIM_RESOLUTION_SYSTEM_PROMPT


class ClaimResolutionAgent(BaseAgent):
    """Agent for resolving crew pay claims."""

    def __init__(self):
        super().__init__(agent_name="ClaimResolutionAgent", temperature=0.1)

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Investigate and resolve crew pay claims.

        Args:
            input_data: Dictionary containing:
                - crew_member_data: Crew member profile
                - claim_data: Claim details
                - flight_assignments: Flight data
                - pay_calculations: Current pay calculations
                - execution_id: Execution tracking ID

        Returns:
            Dictionary with claim resolution analysis
        """
        start_time = time.time()

        try:
            crew_member = input_data.get("crew_member_data", {})
            claim_data = input_data.get("claim_data", {})
            flight_assignments = input_data.get("flight_assignments", [])
            pay_calculations = input_data.get("pay_calculations", {})
            execution_id = input_data.get("execution_id")

            if not claim_data:
                self.logger.info("No claims to process")
                return self._no_claims_result()

            # Prepare claim investigation summary
            investigation_summary = self._prepare_investigation_data(
                claim_data, crew_member, flight_assignments, pay_calculations
            )

            # Create user message
            user_message = f"""Investigate and resolve the following crew pay claim:

{investigation_summary}

INVESTIGATION STEPS:
1. Categorize the claim type
2. Gather all relevant evidence
3. Analyze root cause
4. Determine if claim is valid
5. Calculate correct amount if applicable
6. Recommend resolution (approve/deny/escalate)
7. Identify if this is a pattern/systemic issue

AUTO-RESOLUTION CRITERIA:
- Can auto-resolve if confidence > 0.9 and amount < $500
- Must escalate complex cases or amounts > $500

Please provide:
1. Complete investigation findings
2. Root cause analysis
3. Resolution recommendation
4. Corrected calculation if needed
5. Pattern analysis
6. Crew member communication

Return results in the specified JSON format."""

            # Call Claude
            result = self.call_claude(
                system_prompt=CLAIM_RESOLUTION_SYSTEM_PROMPT,
                user_message=user_message,
                max_tokens=4096,
            )

            # Log execution
            execution_time = int((time.time() - start_time) * 1000)
            self.log_execution(
                execution_id=execution_id,
                crew_member_id=crew_member.get("id"),
                input_data={"claim_id": claim_data.get("claim_id")},
                output_data={
                    "resolution_type": result.get("resolution", {}).get(
                        "resolution_type"
                    )
                },
                execution_time_ms=execution_time,
                success=True,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in claim resolution: {str(e)}")
            execution_time = int((time.time() - start_time) * 1000)
            self.log_execution(
                execution_id=input_data.get("execution_id"),
                crew_member_id=input_data.get("crew_member_data", {}).get("id"),
                input_data=input_data,
                output_data={},
                execution_time_ms=execution_time,
                success=False,
                error_message=str(e),
            )
            raise

    def _prepare_investigation_data(
        self,
        claim_data: Dict[str, Any],
        crew_member: Dict[str, Any],
        flight_assignments: List[Dict[str, Any]],
        pay_calculations: Dict[str, Any],
    ) -> str:
        """Prepare investigation data summary."""
        return f"""
CLAIM DETAILS:
- Claim ID: {claim_data.get('claim_id', 'N/A')}
- Claim Type: {claim_data.get('claim_type', 'unknown')}
- Amount Claimed: ${claim_data.get('amount_claimed', 0):.2f}
- Description: {claim_data.get('description', 'No description provided')}
- Filed Date: {claim_data.get('filed_date', 'N/A')}

CREW MEMBER:
- Employee ID: {crew_member.get('employee_id')}
- Name: {crew_member.get('first_name')} {crew_member.get('last_name')}
- Role: {crew_member.get('role')}

RELEVANT FLIGHT DATA:
{self._format_flight_data(flight_assignments)}

CURRENT PAY CALCULATIONS:
- Total Flight Pay: ${pay_calculations.get('total_flight_pay', 0):.2f}
- Total Premium Pay: ${pay_calculations.get('total_premium_pay', 0):.2f}
- Total Per Diem: ${pay_calculations.get('total_per_diem', 0):.2f}
- Total Pay: ${pay_calculations.get('total_pay', 0):.2f}
"""

    def _format_flight_data(self, flights: List[Dict[str, Any]]) -> str:
        """Format flight data for investigation."""
        if not flights:
            return "No flight data available"

        flight_lines = []
        for flight in flights[:10]:  # Limit to 10 flights
            flight_lines.append(
                f"- {flight.get('flight_number')} on {flight.get('flight_date')}: "
                f"{flight.get('origin_airport')}→{flight.get('destination_airport')} "
                f"({flight.get('actual_block_time', 0):.2f} hrs)"
            )

        return "\n".join(flight_lines)

    def _no_claims_result(self) -> Dict[str, Any]:
        """Return result when no claims to process."""
        return {
            "claim_analysis": None,
            "investigation": None,
            "resolution": {
                "resolution_type": "no_claims",
                "approved_amount": 0.0,
                "denial_reason": None,
                "escalation_reason": None,
            },
            "pattern_analysis": {
                "is_recurring_issue": False,
                "similar_claims_found": 0,
                "systemic_issue": False,
            },
            "requires_human_review": False,
            "confidence_score": 1.0,
        }
