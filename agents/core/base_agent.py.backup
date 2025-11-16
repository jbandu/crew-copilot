"""
Base Agent class for all Crew Copilot agents.

Provides common functionality:
- Claude API integration
- Logging
- Error handling
- Structured outputs
"""

import os
import logging
import json
from typing import Dict, Any, Optional, Type
from datetime import datetime
from decimal import Decimal

from anthropic import Anthropic
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all crew pay calculation agents."""

    def __init__(self, agent_name: str, temperature: float = 0.1):
        """
        Initialize the base agent.

        Args:
            agent_name: Name of the agent (for logging)
            temperature: Claude temperature (default 0.1 for deterministic calculations)
        """
        self.agent_name = agent_name
        self.temperature = temperature
        self.client = self._initialize_client()

        # Configure logging
        self.logger = logging.getLogger(f"agents.{agent_name}")
        self.logger.setLevel(logging.INFO)

    def _initialize_client(self) -> Anthropic:
        """Initialize Anthropic client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        return Anthropic(api_key=api_key)

    def call_claude(
        self,
        system_prompt: str,
        user_message: str,
        response_model: Optional[Type[BaseModel]] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        Call Claude API with structured output.

        Args:
            system_prompt: System prompt defining agent behavior
            user_message: User message with task details
            response_model: Pydantic model for structured response (optional)
            max_tokens: Maximum tokens in response

        Returns:
            Parsed response as dictionary
        """
        try:
            self.logger.info(f"Calling Claude API for {self.agent_name}")

            messages = [{"role": "user", "content": user_message}]

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages,
            )

            # Extract text content
            content = response.content[0].text

            self.logger.debug(f"Claude response: {content[:200]}...")

            # Parse JSON response
            try:
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                    parsed = json.loads(json_str)
                    return parsed
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                    parsed = json.loads(json_str)
                    return parsed
                else:
                    raise ValueError(f"Could not parse JSON from response: {content[:200]}")

        except Exception as e:
            self.logger.error(f"Error calling Claude API: {str(e)}")
            raise

    def log_execution(
        self,
        execution_id: str,
        crew_member_id: Optional[str],
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: int,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Log agent execution for audit trail.

        Args:
            execution_id: UUID linking related agent executions
            crew_member_id: Crew member being processed
            input_data: Input data to agent
            output_data: Output from agent
            execution_time_ms: Execution time in milliseconds
            success: Whether execution succeeded
            error_message: Error message if failed
        """
        log_entry = {
            "agent_name": self.agent_name,
            "execution_id": execution_id,
            "crew_member_id": crew_member_id,
            "execution_time_ms": execution_time_ms,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }

        if error_message:
            log_entry["error_message"] = error_message

        self.logger.info(f"Execution log: {json.dumps(log_entry)}")

    def format_currency(self, amount: float) -> str:
        """Format amount as currency."""
        return f"${amount:,.2f}"

    def format_hours(self, hours: float) -> str:
        """Format hours with 2 decimal places."""
        return f"{hours:.2f}"

    def convert_to_json_safe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data to JSON-safe format (handles Decimal, datetime, etc.)."""
        result = {}
        for key, value in data.items():
            if isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = self.convert_to_json_safe(value)
            elif isinstance(value, list):
                result[key] = [
                    self.convert_to_json_safe(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main calculation method to be implemented by each agent.

        Args:
            input_data: Input data for calculation

        Returns:
            Calculation results

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement calculate()")
