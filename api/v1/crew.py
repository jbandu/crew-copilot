"""
Crew Member API Endpoints
"""
from fastapi import APIRouter

router = APIRouter(prefix="/crew", tags=["crew"])

@router.get("/")
async def list_crew():
    """List all crew members"""
    # TODO: Query database
    return {
        "crew_members": [
            {"id": "P12345", "name": "Sarah Chen", "role": "Captain"},
            {"id": "P12346", "name": "Mike Johnson", "role": "First Officer"},
            {"id": "F78901", "name": "Emma Wilson", "role": "Flight Attendant"}
        ]
    }

@router.get("/{crew_member_id}")
async def get_crew_member(crew_member_id: str):
    """Get specific crew member details"""
    return {
        "id": crew_member_id,
        "name": "Sarah Chen",
        "role": "Captain",
        "base": "BUR",
        "hourly_rate": 140.00,
        "monthly_guarantee": 70.0
    }
