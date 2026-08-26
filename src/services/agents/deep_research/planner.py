import json
import logging
from typing import List, Optional
from llama_cpp import Llama
from pydantic import BaseModel, Field
from src.services.agents.deep_research.state import ResearchSubTask

logger = logging.getLogger(__name__)

class GeneratedPlanSchema(BaseModel):
    sub_task: List[dict] = Field(
        ...,
        description="List of dynamic sub-tasks with sub_topic and search_queries"
    )

class DynamicResearchPlanner:
    """
    Dynamically decomposes any research topic into domain-specific sub-tasks
    using a quantized local SLM running directly on CPU.
    """

    def __init__(self, model_path: str = "./models/qwen2.5-0.5b-instruct-q8_0.gguf", n_threads: int = 4):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=n_threads,
            verbose=False
        )

    def _build_planning_prompt(self, topic: str, max_subtasks: int = 3) -> str:
        return f"""<|im_start|>system
You are an expert research planner. Decompose the user's research topic into {max_subtasks} targeted, non-overlapping investigation angles.
For each sub-topic, provide 2 distinct keyword search queries suitable for arXiv or academic databases.

Output ONLY a single valid JSON object following this exact schema:
{{
  "sub_tasks": [
    {{
      "sub_topic": "Concise angle title",
      "search_queries": ["specific search query 1", "specific search query 2"]
    }}
  ]
}}<|im_end|>
<|im_start|>user
Research Topic: "{topic}"<|im_end|>
<|im_start|>assistant
"""

    def _generate_fallback_plan(self, topic: str) -> List[ResearchSubTask]:
        """Algorithmic fallback if the SLM output cannot be parsed."""
        cleaned = " ".join(topic.split()[:5])
        return [
            ResearchSubTask(
                sub_topic=f"Core Methodology: {cleaned}",
                search_queries=[f"{cleaned} state of the art", f"{cleaned} architecture"],
            ),
            ResearchSubTask(
                sub_topic=f"Evaluation & Applications: {cleaned}",
                search_queries=[f"{cleaned} benchmark results", f"{cleaned} production implementation"],
            ),
        ]

    async def create_plan(
            self, topic:str, max_subtasks: int = 3
    ) -> List[ResearchSubTask]:
        """
        Generates dynamic subtasks tailored to the given topic.
        """

        prompt = self._build_planning_prompt(topic, max_subtasks)

        try: 

            response = self.llm(
                prompt,
                max_tokens=300,
                temprature=0.2,
                stop=["<|im_end|>"],
                echo=False,
            )

            raw_output = response["choices"][0]["text"].strip()

            if raw_output.startswith("```json"):
                raw_output = raw_output[7:]
            if raw_output.startswith("```"):
                raw_output = raw_output[3:]
            if raw_output.endswith("```"):
                raw_output = raw_output[:-3]
            raw_output = raw_output.strip()

            parsed_data = json.loads(raw_output)

            subtasks: List[ResearchSubTask] = []
            for item in parsed_data.get("sub_tasks", []):
                sub_topic = item.get("sub_topic", "General Investigation")
                queries = item.get("search_queries", [topic])

                valid_queries = [q.strip() for q in queries if q and isinstance(q, str)]
                if not valid_queries:
                    valid_queries = [sub_topic]

                subtasks.append(
                    ResearchSubTask(
                        sub_topic=sub_topic,
                        search_queries=valid_queries,
                        status="pending",
                    )
                )

                if subtasks:
                    return subtasks

        except Exception as e:
            logger.warning(
               f"Dynamic SLM planning failed: {str(e)}. Falling back to dynamic heuristic generator." 
            )

        return self._generate_fallback_plan(topic)