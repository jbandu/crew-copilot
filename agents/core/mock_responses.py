"""
Mock responses for testing without Claude API
"""

def get_mock_flight_time_response():
    return {
        "total_block_time": 16.0,
        "total_flight_pay": 1680.00,
        "flight_segments": [
            {"flight_number": "CM101", "block_time": 4.0, "pay": 420.00},
            {"flight_number": "CM102", "block_time": 4.5, "pay": 472.50},
            {"flight_number": "CM103", "block_time": 3.5, "pay": 367.50},
            {"flight_number": "CM104", "block_time": 4.0, "pay": 420.00}
        ],
        "hourly_rate": 105.00,
        "calculation_details": "4 segments, 16.0 total hours @ $105/hr"
    }

def get_mock_duty_time_response():
    return {
        "fdp_hours_7_days": 58.5,
        "fdp_limit_7_days": 60.0,
        "fdp_hours_28_days": 175.0,
        "fdp_limit_28_days": 190.0,
        "compliance_status": "COMPLIANT",
        "violations": [],
        "rest_requirements_met": True,
        "fatigue_risk_score": 0.35
    }

def get_mock_per_diem_response():
    return {
        "total_amount": 352.00,
        "layovers": [
            {"city": "LAS", "nights": 1, "rate": 74.00, "amount": 74.00},
            {"city": "SFO", "nights": 1, "rate": 98.00, "amount": 98.00},
            {"city": "PHX", "nights": 1, "rate": 69.00, "amount": 69.00},
            {"city": "LAS", "nights": 1, "rate": 74.00, "amount": 74.00}
        ],
        "first_day_proration": 0.75,
        "last_day_proration": 0.75,
        "meal_deductions": 37.00
    }

def get_mock_premium_pay_response():
    return {
        "total_premium": 150.00,
        "premiums": [
            {"type": "red_eye", "count": 2, "rate": 75.00, "total": 150.00}
        ],
        "holiday_pay": 0.00,
        "international_pay": 0.00,
        "training_pay": 0.00
    }

def get_mock_guarantee_response():
    return {
        "monthly_guarantee": 70.0,
        "hours_flown": 16.0,
        "guarantee_applied": False,
        "guarantee_amount": 0.00,
        "reason": "Mid-month calculation, final guarantee applies at month-end"
    }

def get_mock_compliance_response():
    return {
        "overall_compliance": "PASS",
        "faa_part_117": "PASS",
        "union_contract": "PASS",
        "company_policy": "PASS",
        "violations": [],
        "warnings": [],
        "audit_trail": "All checks passed successfully"
    }

def get_mock_claims_response():
    return {
        "claims_processed": 0,
        "claims_resolved": 0,
        "pending_claims": [],
        "auto_corrections": []
    }
