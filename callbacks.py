from typing import Any, Dict, List
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult


class AgentCallbackHandler(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        print(f"on_llm_start: {prompts=}")
        print("************\n")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        print(f"on_llm_end: {response.generations[0][0].text}")
        print("************\n")
