"""
Flight Time Calculator Agent

Calculates flight pay based on block time from ACARS data.
"""

import time
from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal

from .base_agent import BaseAgent
from ..prompts.flight_time_prompts import FLIGHT_TIME_SYSTEM_PROMPT


class FlightTimeCalculator(BaseAgent):
    """Agent for calculating flight time and flight pay."""

    def __init__(self):
        super().__init__(agent_name="FlightTimeCalculator", temperature=0.1)

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate flight time and pay from flight assignments.

        Args:
            input_data: Dictionary containing:
                - crew_member_data: Crew member profile
                - flight_assignments: List of flights
                - execution_id: Execution tracking ID

        Returns:
            Dictionary with flight time calculations and pay
        """
        start_time = time.time()

        try:
            crew_member = input_data.get("crew_member_data", {})
            flights = input_data.get("flight_assignments", [])
            execution_id = input_data.get("execution_id")

            if not flights:
                self.logger.warning("No flight assignments provided")
                return {
                    "flights": [],
                    "totals": {
                        "total_flights": 0,
                        "total_actual_hours": 0.0,
                        "total_credit_hours": 0.0,
                        "hourly_rate": float(crew_member.get("hourly_rate", 0)),
                        "total_flight_pay": 0.0,
                    },
                    "discrepancies": [],
                    "confidence_score": 1.0,
                }

            # Prepare flight data for Claude
            flight_summary = self._prepare_flight_data(flights, crew_member)

            # Create user message
            user_message = f"""Calculate flight time and pay for the following crew member and flights:

CREW MEMBER:
- Employee ID: {crew_member.get('employee_id')}
- Name: {crew_member.get('first_name')} {crew_member.get('last_name')}
- Role: {crew_member.get('role')}
- Hourly Rate: ${crew_member.get('hourly_rate')}

FLIGHTS:
{flight_summary}

CONTRACT RULES:
- Minimum credit per segment: 1.0 hour
- Credit hours = MAX(actual block time, minimum credit)
- Flight pay = Total credit hours × Hourly rate

Please calculate:
1. Block time for each flight (actual arrival - actual departure)
2. Credit hours (apply 1.0 hour minimum per segment)
3. Total flight pay
4. Flag any discrepancies or data quality issues

Return results in the specified JSON format."""

            # Call Claude
            result = self.call_claude(
                system_prompt=FLIGHT_TIME_SYSTEM_PROMPT,
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
            self.logger.error(f"Error in flight time calculation: {str(e)}")
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

    def _prepare_flight_data(
        self, flights: List[Dict[str, Any]], crew_member: Dict[str, Any]
    ) -> str:
        """Format flight data for Claude prompt."""
        flight_lines = []

        for i, flight in enumerate(flights, 1):
            scheduled_departure = flight.get("scheduled_departure", "")
            actual_departure = flight.get("actual_departure", "")
            scheduled_arrival = flight.get("scheduled_arrival", "")
            actual_arrival = flight.get("actual_arrival", "")

            flight_lines.append(
                f"""
Flight {i}:
- Flight Number: {flight.get('flight_number')}
- Date: {flight.get('flight_date')}
- Route: {flight.get('origin_airport')} → {flight.get('destination_airport')}
- Scheduled Departure: {scheduled_departure}
- Actual Departure: {actual_departure}
- Scheduled Arrival: {scheduled_arrival}
- Actual Arrival: {actual_arrival}
- Scheduled Block Time: {flight.get('scheduled_block_time', 'N/A')} hours
- Actual Block Time: {flight.get('actual_block_time', 'N/A')} hours
- Position: {flight.get('position')}
"""
            )

        return "\n".join(flight_lines)

    def calculate_block_time(
        self, departure: datetime, arrival: datetime
    ) -> Decimal:
        """
        Calculate block time in hours.

        Args:
            departure: Actual departure time
            arrival: Actual arrival time

        Returns:
            Block time in hours (rounded to 2 decimals)
        """
        if not departure or not arrival:
            return Decimal("0.00")

        duration = arrival - departure
        hours = Decimal(str(duration.total_seconds() / 3600))
        return round(hours, 2)
