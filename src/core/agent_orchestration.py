from typing import Literal, Optional

from pydantic import BaseModel
from intent_classifier import IntentClassification
class AgentOrchestrationState(BaseModel):
    request_id: str
    user_query: str
    intent: IntentClassification
    sub_agent_calls: list[dict] = []
    status: Literal["pending","routing","executing", "done", "failed", "needs_review"]
    attempts: int = 0
    max_attempts: int = 3
    error_message: Optional[str] = None


def master_agent_loop(state: AgentOrchestrationState):
    pass