from typing import Any, Dict
from pydantic import BaseModel

class SubAgentResult(BaseModel):
    status:str
    agent_name:str
    summary: str
    data: Dict[str, Any]
    error: str | None = None


class BaseAgent:
    """Abstract base class enforcing the contract for all sub-agents."""
    async def execute(self, params: Dict[str, Any]) -> SubAgentResult:
        raise NotImplementedError("Sub-agents must implement the execute method.")