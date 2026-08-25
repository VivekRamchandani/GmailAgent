import asyncio
from typing import Any, Dict, List

from pydantic import BaseModel, Field
from enum import Enum

import numpy as np
from sentence_transformers import SentenceTransformer
from registry import AgentRegistry
from fastembed import TextEmbedding



class IntentType(str, Enum):

    RESEARCH = "research"
    ORGANIZE = "organize"
    MULTI_INTENT = "multi_intent"
    UNKNOWN = "unknown"

class IntentClassification(BaseModel):
    intent: IntentType
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    extracted_entities: dict = {}


async def classify_intent(query: str) -> IntentClassification:
    """
    Classifies the intent using structured LLM output or semantic routing (naive Approach).
    """



    q_lower = query.lower()
    if "arxiv" in q_lower or "paper" in q_lower or "search" in q_lower or "research" in q_lower:
        return IntentClassification(
            intent=IntentType.RESEARCH,
            confidence=0.95,
            reasoning="Query requests academic or external literature search.",
            extracted_entities={"query": query}
        )
    elif "organize" in q_lower or "schedule" in q_lower or "format" in q_lower:
        return IntentClassification(
            intent=IntentType.ORGANIZE,
            confidence=0.90,
            reasoning="Query requests sorting or organizing.",
            extracted_entities={"query": query}
        )
    return IntentClassification(intent=IntentType.UNKNOWN, confidence=0.5)


class DynamicSemanticRouter:
    def __init__(self, registry:AgentRegistry, model_name: str = "all-MiniLM-L6-v2"):
        self.registry = registry
        self.encoder = SentenceTransformer(model_name)
        self.agent_embeddings: np.ndarray = np.empty((0, 384))
        self.agent_keys = List[str] = []
        self.refresh_index()


    def refresh_index(self):
        """Re-indexes all agent capabilities dynamically."""

        capabilities = self.registry.get_all()
        if not capabilities:
            return 

        descriptions = []
        keys = []
        for cap in capabilities:
            doc = f"{cap.description}. Actions: {', '.join(cap.supported_actions)}."
            descriptions.append(doc)
            keys.append(cap.agent_id)

        embeddings = self.encoder.encode(descriptions, normalize_embeddings=True)
        self.agent_embeddings = np.array(embeddings)
        self.agent_keys = keys

    def route_query(self, query: str, threshold: float = 0.45) -> Dict[str, Any]:
        """Dynamically matches query to agent vectors"""

        if len(self.agent_keys) == 0:
            return {"agent_id": "unknown", "confidence": 0.0, "reason": "No agent registered."}

        query_vec = self.encoder.encode([query], normalize_embeddings=True)
        similarities = np.dot(self.agent_embeddings, query_vec)
        best_idx = int(np.argmax(similarities))
        best_scores = float(similarities[best_idx])

        if best_scores < threshold:
            return {
                "agent_id" : "unknown",
                "confidence": best_scores,
                "reason": "Query does not match anu registered capability."
            }

        return {
            "agent_id": self.agent_keys[best_idx],
            "confidence": best_scores,
            "reason": f"Matched Dynamically with score {best_scores:.3f}"
        }

class CPUSemanticRouter:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

        self.encoder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.agent_embeddings: np.ndarray = np.empty((0, 384))
        self.agent_keys: list[str] = []
        self.refresh_index()

    def refresh_index(self):
        """Re-indexes all agent capabilities dynamically."""
        capabilities = self.registry.get_all()
        if not capabilities:
            return

        descriptions = [
            f"{cap.description}. Actions: {', '.join(cap.supported_actions)}." 
            for cap in capabilities
        ]
        self.agent_keys = [cap.agent_id for cap in capabilities]

        # FastEmbed returns a generator, we cast to a list of numpy arrays
        embeddings_list = list(self.encoder.embed(descriptions))
        
        self.agent_embeddings = np.array([
            emb / np.linalg.norm(emb) for emb in embeddings_list
        ])

    def route_query(self, query: str, threshold: float = 0.5) -> dict:
        """Matches query using CPU vector math"""
        if not self.agent_keys:
            return {"agent_id": "unknown", "confidence": 0.0}

        query_vec = list(self.encoder.embed([query]))[0]
        query_vec = query_vec / np.linalg.norm(query_vec)

        similarities = np.dot(self.agent_embeddings, query_vec)
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score < threshold:
            return {"agent_id": "unknown", "confidence": best_score}

        return {"agent_id": self.agent_keys[best_idx], "confidence": best_score}

    async def route_query_async(self, query: str) -> Dict[str, Any]:
        return await asyncio.to_thread(self.route_query, query)
    



    