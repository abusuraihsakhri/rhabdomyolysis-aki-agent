"""
Deterministic offline demonstration adapter with regex-based identifier checks.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Rhabdomyolysis Aki Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} Demonstration]: Received query: '{prompt[:60]}...'. No clinical validation or model inference was performed."


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Rhabdomyolysis Aki Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError("Only the deterministic mock provider is implemented. No external LLM integrations are configured.")
