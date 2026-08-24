from typing import Callable, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentCapability(BaseModel):
    agent_id: str
    description: str
    supported_actions: List[str]
    sample_queries: List[str] = Field(default_factory=list)
    endpoint_or_handler: Optional[str] = None


class AgentRegistry:
    def __init__(self):
        self._registry: Dict[str, AgentCapability] = {}

    def register(self, capability: AgentCapability):
        self._registry[capability.agent_id] = capability

    def get_all(self) -> List[AgentCapability]:
        return list(self._registry.values())
    