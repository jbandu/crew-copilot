"""
Duty Time Monitor Agent

Tracks and enforces FAA Part 117 duty time and rest requirements.
"""

import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

from .base_agent import BaseAgent
from ..prompts.duty_time_prompts import DUTY_TIME_SYSTEM_PROMPT


class DutyTimeMonitor(BaseAgent):
    """Agent for monitoring FAA Part 117 compliance."""

    def __init__(self):
        super().__init__(agent_name="DutyTimeMonitor", temperature=0.1)

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor duty time and validate FAA Part 117 compliance.

        Args:
            input_data: Dictionary containing:
                - crew_member_data: Crew member profile
                - flight_assignments: List of flights
                - historical_duty_data: Past 30 days duty history (optional)
                - execution_id: Execution tracking ID

        Returns:
            Dictionary with duty time analysis and compliance status
        """
        start_time = time.time()

        try:
            crew_member = input_data.get("crew_member_data", {})
            flights = input_data.get("flight_assignments", [])
            historical_data = input_data.get("historical_duty_data", [])
            execution_id = input_data.get("execution_id")

            if not flights:
                self.logger.warning("No flight assignments to monitor")
                return self._empty_result()

            # Prepare duty period data
            duty_summary = self._prepare_duty_data(flights)
            historical_summary = self._prepare_historical_data(historical_data)

            # Create user message
            user_message = f"""Analyze duty time compliance for the following crew member:

CREW MEMBER:
- Employee ID: {crew_member.get('employee_id')}
- Name: {crew_member.get('first_name')} {crew_member.get('last_name')}
- Role: {crew_member.get('role')}
- Base: {crew_member.get('base_airport')}

CURRENT PERIOD DUTY DATA:
{duty_summary}

HISTORICAL DUTY DATA (Past 30 days):
{historical_summary}

FAA PART 117 REQUIREMENTS TO VALIDATE:
1. FDP Limits (Table B based on start time and segments)
2. Minimum 10-hour rest between duties (8-hour sleep opportunity)
3. 30-hour rest requirement at least once per 7 days
4. Cumulative limits:
   - Max 60 hours FDP in 7 days
   - Max 190 hours FDP in 28 days
   - Max 100 hours flight time in 28 days
   - Max 1,000 hours flight time in 365 days

Please:
1. Validate each duty period against FDP limits
2. Verify rest periods meet minimums
3. Calculate cumulative duty/flight time
4. Flag any violations or warnings
5. Assess fatigue risk
6. Provide compliance status

Return results in the specified JSON format."""

            # Call Claude
            result = self.call_claude(
                system_prompt=DUTY_TIME_SYSTEM_PROMPT,
                user_message=user_message,
                max_tokens=4096,
            )

            # Log execution
            execution_time = int((time.time() - start_time) * 1000)
            self.log_execution(
                execution_id=execution_id,
                crew_member_id=crew_member.get("id"),
                input_data={"duty_period_count": len(flights)},
                output_data={"compliance_status": result.get("compliance_status")},
                execution_time_ms=execution_time,
                success=True,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in duty time monitoring: {str(e)}")
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

    def _prepare_duty_data(self, flights: List[Dict[str, Any]]) -> str:
        """Format duty period data for Claude prompt."""
        # Group flights by duty period (trip_id)
        trips = {}
        for flight in flights:
            trip_id = flight.get("trip_id", "UNKNOWN")
            if trip_id not in trips:
                trips[trip_id] = []
            trips[trip_id].append(flight)

        trip_lines = []
        for trip_id, trip_flights in trips.items():
            trip_flights.sort(key=lambda f: f.get("sequence_number", 0))

            first_flight = trip_flights[0]
            last_flight = trip_flights[-1]

            report_time = first_flight.get("duty_report_time", "N/A")
            release_time = last_flight.get("duty_end_time", "N/A")
            fdp_hours = first_flight.get("flight_duty_period", "N/A")
            num_segments = len(trip_flights)

            trip_lines.append(
                f"""
Trip {trip_id}:
- Duty Report: {report_time}
- Duty Release: {release_time}
- FDP Hours: {fdp_hours}
- Number of Segments: {num_segments}
- Flights: {', '.join([f.get('flight_number') for f in trip_flights])}
"""
            )

        return "\n".join(trip_lines) if trip_lines else "No duty periods"

    def _prepare_historical_data(self, historical_data: List[Dict[str, Any]]) -> str:
        """Format historical duty data."""
        if not historical_data:
            return "No historical data available (first period for crew member)"

        # Summarize historical data
        total_fdp = sum(d.get("fdp_hours", 0) for d in historical_data)
        total_flight_time = sum(d.get("flight_hours", 0) for d in historical_data)

        return f"""
Past 30 Days Summary:
- Total FDP Hours: {total_fdp:.2f}
- Total Flight Hours: {total_flight_time:.2f}
- Number of Duty Periods: {len(historical_data)}
"""

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "duty_periods": [],
            "rest_periods": [],
            "cumulative_limits": {
                "fdp_7_days": {
                    "actual": 0.0,
                    "limit": 60.0,
                    "compliant": True,
                    "utilization_percent": 0.0,
                },
                "fdp_28_days": {
                    "actual": 0.0,
                    "limit": 190.0,
                    "compliant": True,
                    "utilization_percent": 0.0,
                },
                "flight_time_28_days": {
                    "actual": 0.0,
                    "limit": 100.0,
                    "compliant": True,
                    "utilization_percent": 0.0,
                },
                "flight_time_365_days": {
                    "actual": 0.0,
                    "limit": 1000.0,
                    "compliant": True,
                    "utilization_percent": 0.0,
                },
            },
            "violations": [],
            "fatigue_assessment": {
                "overall_risk": "low",
                "contributing_factors": [],
                "recommendations": [],
            },
            "compliance_status": "compliant",
            "confidence_score": 1.0,
        }
