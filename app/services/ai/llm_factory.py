from functools import lru_cache

from app.services.ai.generate_text import LLMService


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    """Return the shared LLM service instance."""
    return LLMService(
        provider="openrouter",
        model="nvidia/nemotron-3.5-lightning:free",
        fallback_model="qwen3:8b",
        openrouter_limit=50,
    )
