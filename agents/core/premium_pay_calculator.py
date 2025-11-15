"""
Premium Pay Calculator Agent

Calculates all premium pay components (holiday, red-eye, international, etc.).
"""

import time
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from ..prompts.premium_pay_prompts import PREMIUM_PAY_SYSTEM_PROMPT


class PremiumPayCalculator(BaseAgent):
    """Agent for calculating premium pay."""

    def __init__(self):
        super().__init__(agent_name="PremiumPayCalculator", temperature=0.1)

    # US Federal Holidays for 2025
    HOLIDAYS_2025 = [
        "2025-01-01",  # New Year's Day
        "2025-01-20",  # MLK Day
        "2025-02-17",  # Presidents Day
        "2025-05-26",  # Memorial Day
        "2025-06-19",  # Juneteenth
        "2025-07-04",  # Independence Day
        "2025-09-01",  # Labor Day
        "2025-10-13",  # Columbus Day
        "2025-11-11",  # Veterans Day
        "2025-11-27",  # Thanksgiving
        "2025-12-25",  # Christmas
    ]

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all premium pay components.

        Args:
            input_data: Dictionary containing:
                - crew_member_data: Crew member profile
                - flight_assignments: List of flights
                - flight_time_data: Flight time calculation results
                - premium_rules: Premium pay rules from database
                - execution_id: Execution tracking ID

        Returns:
            Dictionary with premium pay calculations
        """
        start_time = time.time()

        try:
            crew_member = input_data.get("crew_member_data", {})
            flights = input_data.get("flight_assignments", [])
            flight_time_data = input_data.get("flight_time_data", {})
            premium_rules = input_data.get("premium_rules", {})
            execution_id = input_data.get("execution_id")

            if not flights:
                self.logger.warning("No flights to calculate premium pay")
                return self._empty_result()

            # Identify premium-eligible flights
            premium_summary = self._prepare_premium_data(flights, crew_member)

            # Create user message
            user_message = f"""Calculate premium pay for the following crew member:

CREW MEMBER:
- Employee ID: {crew_member.get('employee_id')}
- Name: {crew_member.get('first_name')} {crew_member.get('last_name')}
- Role: {crew_member.get('role')}
- Hourly Rate: ${crew_member.get('hourly_rate')}
- Total Credit Hours: {flight_time_data.get('totals', {}).get('total_credit_hours', 0)}

FLIGHTS WITH PREMIUM ELIGIBILITY:
{premium_summary}

PREMIUM RULES:
{self._format_premium_rules(premium_rules, crew_member.get('role'))}

HOLIDAYS IN PERIOD: {', '.join(self.HOLIDAYS_2025)}

Please calculate:
1. Holiday pay (1.5x rate for work on holidays)
2. Red-eye premiums (flights departing 2200-0559)
3. International premiums (15% of trip value)
4. Training pay (if applicable)
5. Deadhead pay (if applicable)
6. Any other applicable premiums

Return results in the specified JSON format with itemized breakdown."""

            # Call Claude
            result = self.call_claude(
                system_prompt=PREMIUM_PAY_SYSTEM_PROMPT,
                user_message=user_message,
                max_tokens=4096,
            )

            # Log execution
            execution_time = int((time.time() - start_time) * 1000)
            self.log_execution(
                execution_id=execution_id,
                crew_member_id=crew_member.get("id"),
                input_data={"flight_count": len(flights)},
                output_data=result.get("totals", {}),
                execution_time_ms=execution_time,
                success=True,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in premium pay calculation: {str(e)}")
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

    def _prepare_premium_data(
        self, flights: List[Dict[str, Any]], crew_member: Dict[str, Any]
    ) -> str:
        """Format premium eligibility data for Claude prompt."""
        flight_lines = []

        for flight in flights:
            flight_date = flight.get("flight_date", "")
            flight_number = flight.get("flight_number")
            is_holiday = str(flight_date) in self.HOLIDAYS_2025
            is_redeye = flight.get("is_redeye", False)
            is_international = flight.get("is_international", False)
            is_deadhead = flight.get("is_deadhead", False)

            premiums = []
            if is_holiday:
                premiums.append("HOLIDAY")
            if is_redeye:
                premiums.append("RED-EYE")
            if is_international:
                premiums.append("INTERNATIONAL")
            if is_deadhead:
                premiums.append("DEADHEAD")

            if premiums:
                flight_lines.append(
                    f"""
Flight {flight_number} ({flight_date}):
- Route: {flight.get('origin_airport')} → {flight.get('destination_airport')}
- Departure: {flight.get('actual_departure')}
- Block Time: {flight.get('actual_block_time', 0):.2f} hours
- Premium Types: {', '.join(premiums)}
"""
                )

        if not flight_lines:
            return "No flights qualify for premium pay in this period."

        return "\n".join(flight_lines)

    def _format_premium_rules(self, rules: Dict[str, Any], role: str) -> str:
        """Format premium pay rules."""
        return f"""
Holiday Pay: 1.5x hourly rate
Red-Eye Premium: ${100 if role == 'Captain' else 75 if role == 'First Officer' else 50} per segment
International Premium: 15% of base trip pay
Deadhead Pay: 50% of hourly rate
Training Pay: ${125 if role == 'Captain' else 100 if role == 'First Officer' else 75} per session
"""

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "premium_components": [],
            "totals": {
                "total_holiday_pay": 0.0,
                "total_redeye_premium": 0.0,
                "total_international_premium": 0.0,
                "total_training_pay": 0.0,
                "total_deadhead_pay": 0.0,
                "total_cancellation_pay": 0.0,
                "total_overtime_pay": 0.0,
                "total_premium_pay": 0.0,
            },
            "breakdown_by_type": {},
            "notes": ["No premium pay eligible in this period"],
            "confidence_score": 1.0,
        }
