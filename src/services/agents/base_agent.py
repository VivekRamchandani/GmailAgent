import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from tenacity import (
    retry, 
    stop_after_attempt,
    wait_exponential, 
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_token: int = 0
    total_tokens: int = 0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            prompt_tokens = self.prompt_tokens + other.prompt_tokens,
            completion_token = self.completion_token + other.completion_token
            total_tokens = self.total_tokens + other.total_tokens
        ) 

    

class AgentState(BaseModel):
    """Shared State object passed through the orchestrator/pipeline"""
    session_id: str 
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any]  = Field(default_factory=dict)
    cumulative_usage: TokenUsage = Field(default_factory=TokenUsage)


class AgentResopnse(BaseModel):
    """Normalized response contract for every concrete agent. """
    agent_name:str
    content:str
    structured_data: Optional[Dict[str, Any]] = None
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    status: str
    error: Optinal[str] = None


class BaseAgent(ABC):
    def __init__(self, name: str, max_retries: float, backoff_min: float = 1.0, backoff_max: float = 10.0):
        self.name = name
        self.max_retries = max_retries
        self.backoff_min = backoff_min
        self.backoff_max = backoff_max

    
    def invoke(self, state: AgentState ) -> AgentResopnse:

        start_time = time.perf_counter()
        logger.info(f"[{self.name}] Started processing session: {state.session_id}")

        try: 

            response = self._retry_wrapper()(self._execute_agent)(state)

            response.latency_ms = round((time.perf_counter() - start_time) * 1000 , 2)

            state.cumulative_usage += response.token_usage

            logger.info(
                f"[{self.name}] Completed successfully in {response.latency_ms}ms "
                f"(Tokens: {response.token_usage.total_tokens})"
                )
            return response
        
        except Exception as exc: 
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"[{self.name}] Failed after retries: {exc}", exc_info=True)
            return self.handle_fallback(exc, state, latency_ms)

    
    def _retry_wrapper(self):
        """Constructs an exponential backoff decorator"""
        return retry(
            reraise=True,
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=self.backoff_min, max=self.backoff_max),
            retry=retry_if_exception_type((TimeoutError, ConnectionError, RuntimeError)),
            before_sleep=before_sleep_log(logger, logging.WARNING),     
        )
    
    @abstractmethod
    def _execute_agent(self, state: AgentState) -> AgentState:
        """Concrete agnets MUST Implement their core prompt engineering,"""
        raise NotImplementedError

    
    def handle_fallback( self, error: Exception, state: AgentState, latency_ms: float) -> AgentResopnse:
        return AgentResopnse(
            agent_name=self.name,
            content="Agent encountered unrecoverable error",
            token_usage=TokenUsage(),
            latency_ms=latency_ms,
            error=str(error) 
        )
