import json
from src.core.registry import AgentRegistry

def build_dynamic_prompt(query: str, registry: AgentRegistry) -> str:
    capabilities = [
        {"agent_id": cap.agent_id, "description": cap.description, "actions": cap.supported_actions}
        for cap in registry.get_all()
    ]

    return f"""You are a query routing engine. Given the available agents:
               {json.dumps(capabilities, indent=2)}
                Analyze the user query and output a valid JSON object matching the target agent and parameters:
                User Query: "{query}"

                respond ONLY with valid JSON in format:
                {{"target_agent": "agent_id", "confidence": 0.95, "extracted_params": {{}}}}
"""