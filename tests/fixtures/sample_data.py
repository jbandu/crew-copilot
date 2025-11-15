"""
Test Data Fixtures

Sample data for testing agents.
"""

from datetime import datetime, date

# Sample crew member
SAMPLE_CREW_MEMBER = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "employee_id": "P12345",
    "first_name": "Sarah",
    "last_name": "Chen",
    "email": "sarah.chen@aveloair.com",
    "role": "Captain",
    "crew_type": "line_holder",
    "hourly_rate": 105.00,
    "monthly_guarantee": 75.00,
    "base_airport": "BUR",
}

# Sample flight assignments
SAMPLE_FLIGHTS = [
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
    {
        "flight_number": "XP102",
        "flight_date": "2025-11-04",
        "origin_airport": "PDX",
        "destination_airport": "BUR",
        "scheduled_departure": "2025-11-04 15:00:00",
        "actual_departure": "2025-11-04 15:10:00",
        "scheduled_arrival": "2025-11-04 17:45:00",
        "actual_arrival": "2025-11-04 17:55:00",
        "scheduled_block_time": 2.75,
        "actual_block_time": 2.75,
        "duty_report_time": "2025-11-04 14:00:00",
        "duty_end_time": "2025-11-04 18:30:00",
        "flight_duty_period": 4.50,
        "position": "captain",
        "overnight_location": None,
        "is_redeye": False,
        "is_international": False,
        "trip_id": "TRIP-001",
        "sequence_number": 2,
    },
]

# Expected results for validation
EXPECTED_FLIGHT_TIME_HOURS = 5.33  # 2.58 + 2.75
EXPECTED_CREDIT_HOURS = 5.33  # Both flights > 1.0 minimum
EXPECTED_BASE_PAY = 105.00 * 5.33  # $559.65
