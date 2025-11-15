"""
Guarantee Calculator Agent

Ensures crew members receive minimum guaranteed pay per union contract.
"""

import time
from typing import Dict, Any

from .base_agent import BaseAgent
from ..prompts.guarantee_prompts import GUARANTEE_SYSTEM_PROMPT


class GuaranteeCalculator(BaseAgent):
    """Agent for calculating minimum pay guarantees."""

    def __init__(self):
        super().__init__(agent_name="GuaranteeCalculator", temperature=0.1)

    # Guarantee hours by role and crew type
    MONTHLY_GUARANTEES = {
        ("Captain", "line_holder"): 75.0,
        ("Captain", "reserve"): 73.0,
        ("First Officer", "line_holder"): 75.0,
        ("First Officer", "reserve"): 73.0,
        ("Flight Attendant", "line_holder"): 70.0,
        ("Flight Attendant", "reserve"): 70.0,
        ("Lead Flight Attendant", "line_holder"): 70.0,
        ("Lead Flight Attendant", "reserve"): 70.0,
    }

    DAILY_GUARANTEE = 4.0  # hours

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate minimum guarantee and ensure it's applied.

        Args:
            input_data: Dictionary containing:
                - crew_member_data: Crew member profile
                - flight_time_data: Flight time calculation results
                - pay_period_start: Start date
                - pay_period_end: End date
                - execution_id: Execution tracking ID

        Returns:
            Dictionary with guarantee calculations
        """
        start_time = time.time()

        try:
            crew_member = input_data.get("crew_member_data", {})
            flight_time_data = input_data.get("flight_time_data", {})
            execution_id = input_data.get("execution_id")

            role = crew_member.get("role")
            crew_type = crew_member.get("crew_type")
            hourly_rate = crew_member.get("hourly_rate", 0)

            # Get actual credit hours
            actual_hours = flight_time_data.get("totals", {}).get(
                "total_credit_hours", 0.0
            )

            # Get applicable guarantee
            monthly_guarantee = self.MONTHLY_GUARANTEES.get(
                (role, crew_type), 70.0
            )

            # Prepare summary
            summary = f"""
CREW MEMBER:
- Employee ID: {crew_member.get('employee_id')}
- Name: {crew_member.get('first_name')} {crew_member.get('last_name')}
- Role: {role}
- Crew Type: {crew_type}
- Hourly Rate: ${hourly_rate}

ACTUAL HOURS:
- Total Credit Hours: {actual_hours}

APPLICABLE GUARANTEES:
- Monthly Guarantee: {monthly_guarantee} hours ({crew_type})
- Daily Guarantee: {self.DAILY_GUARANTEE} hours per duty period

CALCULATION:
- Paid Hours = MAX(Actual Hours, Monthly Guarantee)
- Paid Hours = MAX({actual_hours}, {monthly_guarantee})
- Base Pay = Paid Hours × Hourly Rate
"""

            # Create user message
            user_message = f"""{summary}

Please calculate:
1. Determine which guarantee applies
2. Compare actual hours vs guarantee
3. Calculate paid hours (the greater amount)
4. Calculate base pay
5. Show if guarantee was triggered
6. Provide day-by-day breakdown if needed

Return results in the specified JSON format."""

            # Call Claude
            result = self.call_claude(
                system_prompt=GUARANTEE_SYSTEM_PROMPT,
                user_message=user_message,
                max_tokens=4096,
            )

            # Log execution
            execution_time = int((time.time() - start_time) * 1000)
            self.log_execution(
                execution_id=execution_id,
                crew_member_id=crew_member.get("id"),
                input_data={
                    "actual_hours": actual_hours,
                    "guarantee_hours": monthly_guarantee,
                },
                output_data=result.get("calculation", {}),
                execution_time_ms=execution_time,
                success=True,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in guarantee calculation: {str(e)}")
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
