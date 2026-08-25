import json
from llama_cpp import Llama
from src.core.registry import AgentRegistry


class CPULocalSLM:
    def __init__(self, model_path: str = "./models/qwen2.5-0.5b-instruct-q8_0.gguf"):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )

    def extract_intent_and_params(self, query: str, registry: AgentRegistry) -> dict:
        capabilities = [
            {
                "agent_id": cap.agent_id, "actions": cap.supported_actions
            } 
            for cap in registry.get_all()
        ]

        prompt = f"""
                  <|im_start|> system You are a routing engine. Available agents: {json.dumps(capabilities)}
                  Output ONLY valid JSON containing "target_agent" and "extracted_params". <|im_end|>
                  <|im_start|> user Query: "{query}"<|im_end|>
                  <|im_start|>assistant
                  """

        response = self.llm(
            prompt,
            max_tokens=150,
            temperature=0.0,
            stop=["<|im_end|>"],
            echo=False
        )

        try: 
            result_text = response['choices'][0]['text'].strip()
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {"target_agent": "unknown", "error": "SLM failed to output JSON"}