"""
Compliance Validator Agent

Validates all calculations against FAA regulations and union contracts.
"""

import time
from typing import Dict, Any

from .base_agent import BaseAgent
from ..prompts.compliance_prompts import COMPLIANCE_SYSTEM_PROMPT


class ComplianceValidator(BaseAgent):
    """Agent for validating compliance with regulations and contracts."""

    def __init__(self):
        super().__init__(agent_name="ComplianceValidator", temperature=0.1)

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all calculations for compliance.

        Args:
            input_data: Dictionary containing:
                - crew_member_data: Crew member profile
                - flight_time_data: Flight time results
                - duty_time_data: Duty time results
                - per_diem_data: Per diem results
                - premium_pay_data: Premium pay results
                - guarantee_data: Guarantee results
                - execution_id: Execution tracking ID

        Returns:
            Dictionary with compliance validation results
        """
        start_time = time.time()

        try:
            crew_member = input_data.get("crew_member_data", {})
            flight_time_data = input_data.get("flight_time_data", {})
            duty_time_data = input_data.get("duty_time_data", {})
            per_diem_data = input_data.get("per_diem_data", {})
            premium_pay_data = input_data.get("premium_pay_data", {})
            guarantee_data = input_data.get("guarantee_data", {})
            execution_id = input_data.get("execution_id")

            # Prepare comprehensive summary for validation
            summary = self._prepare_validation_summary(
                crew_member,
                flight_time_data,
                duty_time_data,
                per_diem_data,
                premium_pay_data,
                guarantee_data,
            )

            # Create user message
            user_message = f"""Validate all calculations for compliance:

{summary}

VALIDATION REQUIREMENTS:

1. FAA COMPLIANCE:
   - All FDP limits followed
   - Rest requirements met
   - Cumulative limits not exceeded
   - No violations of Part 117 or Part 121

2. CONTRACT COMPLIANCE:
   - Correct hourly rates applied
   - Minimum guarantees enforced
   - Premium pay rules followed correctly
   - Per diem rates are current
   - All contractual protections honored

3. CALCULATION ACCURACY:
   - Flight time math is correct
   - Premium calculations are accurate
   - Per diem calculations are correct
   - Guarantee properly applied
   - No duplicate or missing payments

Please perform thorough validation and:
1. Check each calculation against rules
2. Verify all regulations are followed
3. Flag any violations or warnings
4. Recommend corrections if needed
5. Provide overall compliance status
6. Determine if human review is needed

Return results in the specified JSON format."""

            # Call Claude
            result = self.call_claude(
                system_prompt=COMPLIANCE_SYSTEM_PROMPT,
                user_message=user_message,
                max_tokens=4096,
            )

            # Log execution
            execution_time = int((time.time() - start_time) * 1000)
            self.log_execution(
                execution_id=execution_id,
                crew_member_id=crew_member.get("id"),
                input_data={"validation_scope": "full"},
                output_data={
                    "overall_compliance": result.get("overall_compliance"),
                    "violations_count": len(result.get("violations", [])),
                },
                execution_time_ms=execution_time,
                success=True,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in compliance validation: {str(e)}")
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

    def _prepare_validation_summary(
        self,
        crew_member: Dict[str, Any],
        flight_time_data: Dict[str, Any],
        duty_time_data: Dict[str, Any],
        per_diem_data: Dict[str, Any],
        premium_pay_data: Dict[str, Any],
        guarantee_data: Dict[str, Any],
    ) -> str:
        """Prepare comprehensive summary for validation."""
        return f"""
CREW MEMBER:
- Employee ID: {crew_member.get('employee_id')}
- Role: {crew_member.get('role')}
- Crew Type: {crew_member.get('crew_type')}
- Hourly Rate: ${crew_member.get('hourly_rate')}

FLIGHT TIME DATA:
- Total Flights: {flight_time_data.get('totals', {}).get('total_flights', 0)}
- Total Actual Hours: {flight_time_data.get('totals', {}).get('total_actual_hours', 0)}
- Total Credit Hours: {flight_time_data.get('totals', {}).get('total_credit_hours', 0)}
- Total Flight Pay: ${flight_time_data.get('totals', {}).get('total_flight_pay', 0)}
- Discrepancies: {len(flight_time_data.get('discrepancies', []))}

DUTY TIME DATA:
- Compliance Status: {duty_time_data.get('compliance_status', 'unknown')}
- Violations: {len(duty_time_data.get('violations', []))}
- Fatigue Risk: {duty_time_data.get('fatigue_assessment', {}).get('overall_risk', 'unknown')}
- FDP 7-day: {duty_time_data.get('cumulative_limits', {}).get('fdp_7_days', {}).get('actual', 0)} / 60 hours
- FDP 28-day: {duty_time_data.get('cumulative_limits', {}).get('fdp_28_days', {}).get('actual', 0)} / 190 hours

PER DIEM DATA:
- Total Layovers: {per_diem_data.get('totals', {}).get('total_layovers', 0)}
- Total Per Diem: ${per_diem_data.get('totals', {}).get('total_net_per_diem', 0)}

PREMIUM PAY DATA:
- Total Premium Pay: ${premium_pay_data.get('totals', {}).get('total_premium_pay', 0)}
- Holiday Pay: ${premium_pay_data.get('totals', {}).get('total_holiday_pay', 0)}
- Red-Eye Premium: ${premium_pay_data.get('totals', {}).get('total_redeye_premium', 0)}
- International Premium: ${premium_pay_data.get('totals', {}).get('total_international_premium', 0)}

GUARANTEE DATA:
- Actual Hours: {guarantee_data.get('actual_hours', 0)}
- Guarantee Hours: {guarantee_data.get('guarantee_applied', {}).get('hours', 0)}
- Paid Hours: {guarantee_data.get('paid_hours', 0)}
- Guarantee Triggered: {guarantee_data.get('guarantee_triggered', False)}
- Base Pay: ${guarantee_data.get('calculation', {}).get('base_pay', 0)}
"""
