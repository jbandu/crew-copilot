"""
Per Diem Calculator Agent

Calculates per diem allowances for layovers using GSA and State Department rates.
"""

import time
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..prompts.per_diem_prompts import PER_DIEM_SYSTEM_PROMPT


class PerDiemCalculator(BaseAgent):
    """Agent for calculating per diem allowances."""

    def __init__(self):
        super().__init__(agent_name="PerDiemCalculator", temperature=0.1)

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate per diem allowances for layovers.

        Args:
            input_data: Dictionary containing:
                - crew_member_data: Crew member profile
                - flight_assignments: List of flights
                - per_diem_rates: Rate table from database
                - execution_id: Execution tracking ID

        Returns:
            Dictionary with per diem calculations
        """
        start_time = time.time()

        try:
            crew_member = input_data.get("crew_member_data", {})
            flights = input_data.get("flight_assignments", [])
            rates = input_data.get("per_diem_rates", {})
            execution_id = input_data.get("execution_id")

            # Find layovers (flights with overnight_location)
            layovers = [f for f in flights if f.get("overnight_location")]

            if not layovers:
                self.logger.info("No layovers found, no per diem to calculate")
                return self._empty_result()

            # Prepare layover data
            layover_summary = self._prepare_layover_data(layovers, rates)

            # Create user message
            user_message = f"""Calculate per diem allowances for the following crew member:

CREW MEMBER:
- Employee ID: {crew_member.get('employee_id')}
- Name: {crew_member.get('first_name')} {crew_member.get('last_name')}

LAYOVERS:
{layover_summary}

PER DIEM RULES:
- Domestic: Use GSA rates
- International: Use State Department rates
- First/Last day of trip: 75% of full rate
- Full days: 100% of rate
- Deduct for airline-provided meals (if applicable)

AVAILABLE RATES:
{self._format_rates(rates)}

Please calculate:
1. Per diem for each layover
2. Apply first/last day proration
3. Calculate total per diem
4. Document rates used

Return results in the specified JSON format."""

            # Call Claude
            result = self.call_claude(
                system_prompt=PER_DIEM_SYSTEM_PROMPT,
                user_message=user_message,
                max_tokens=4096,
            )

            # Log execution
            execution_time = int((time.time() - start_time) * 1000)
            self.log_execution(
                execution_id=execution_id,
                crew_member_id=crew_member.get("id"),
                input_data={"layover_count": len(layovers)},
                output_data=result.get("totals", {}),
                execution_time_ms=execution_time,
                success=True,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in per diem calculation: {str(e)}")
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

    def _prepare_layover_data(
        self, layovers: List[Dict[str, Any]], rates: Dict[str, Any]
    ) -> str:
        """Format layover data for Claude prompt."""
        layover_lines = []

        for i, flight in enumerate(layovers, 1):
            overnight_location = flight.get("overnight_location")
            arrival = flight.get("actual_arrival") or flight.get("scheduled_arrival")
            # Find the departure flight from this location
            # For now, just use the arrival time
            layover_lines.append(
                f"""
Layover {i}:
- Location: {overnight_location}
- Arrival: {arrival}
- International: {flight.get('is_international', False)}
- Flight: {flight.get('flight_number')}
"""
            )

        return "\n".join(layover_lines)

    def _format_rates(self, rates: Dict[str, Any]) -> str:
        """Format available per diem rates."""
        if not rates:
            return "Using default rates: Domestic $74-84, International $110-125"

        # Format rate data
        rate_lines = []
        for airport_code, rate_info in rates.items():
            rate_lines.append(
                f"- {airport_code}: ${rate_info.get('rate', 0):.2f} "
                f"({rate_info.get('city', 'Unknown')})"
            )

        return "\n".join(rate_lines) if rate_lines else "No specific rates provided"

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "layovers": [],
            "totals": {
                "total_layovers": 0,
                "total_days": 0.0,
                "total_gross_per_diem": 0.0,
                "total_meal_deductions": 0.0,
                "total_net_per_diem": 0.0,
            },
            "rate_sources": [],
            "notes": ["No layovers in this period"],
            "confidence_score": 1.0,
        }
