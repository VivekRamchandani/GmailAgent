from typing import Any, Dict, List , Optional
from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    source_id: str
    source_title: str
    source_url: str
    extracted_finding: str
    confidence: float = 1.0

class ResearchSubTask(BaseModel):
    sub_topic: str
    search_queries: List[str]
    status: str = "pending"

class DeepResearchState(BaseModel):
    topic: str
    max_depth: int = 3
    current_depth: int = 0
    research_plan: List[ResearchSubTask] = Field(default_factory=list)
    gathered_evidence: List[EvidenceItem] = Field(default_factory=list)
    visited_source_ids: set[str] = Field(default_factory=set)
    unresolved_questions: List[str] = Field(default_factory=list)
    final_report: Optional[str] = None
    status: str = "planning"