"""Agent prompts for Claude API calls."""

from .flight_time_prompts import FLIGHT_TIME_SYSTEM_PROMPT
from .duty_time_prompts import DUTY_TIME_SYSTEM_PROMPT
from .per_diem_prompts import PER_DIEM_SYSTEM_PROMPT
from .premium_pay_prompts import PREMIUM_PAY_SYSTEM_PROMPT
from .guarantee_prompts import GUARANTEE_SYSTEM_PROMPT
from .compliance_prompts import COMPLIANCE_SYSTEM_PROMPT
from .claim_resolution_prompts import CLAIM_RESOLUTION_SYSTEM_PROMPT

__all__ = [
    "FLIGHT_TIME_SYSTEM_PROMPT",
    "DUTY_TIME_SYSTEM_PROMPT",
    "PER_DIEM_SYSTEM_PROMPT",
    "PREMIUM_PAY_SYSTEM_PROMPT",
    "GUARANTEE_SYSTEM_PROMPT",
    "COMPLIANCE_SYSTEM_PROMPT",
    "CLAIM_RESOLUTION_SYSTEM_PROMPT",
]
