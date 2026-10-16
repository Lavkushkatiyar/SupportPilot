import os

import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_URL = "http://localhost:11434/api/chat"
REQUEST_TIMEOUT_SECONDS = 120


class LLMService:
    """Client for generating text through OpenRouter or Ollama."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        provider: str | None = None,
    ) -> None:
        self.provider = (provider or os.getenv("LLM_PROVIDER", "openrouter")).lower()

        if self.provider == "ollama":
            self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:8b")
            print(self.model)
            self.api_key = None
        elif self.provider == "openrouter":
            self.model = model or os.getenv("OPENROUTER_MODEL")
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

        if not self.model:
            raise ValueError("MODEL is not configured.")

        if self.provider == "openrouter" and not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        if self.provider == "openrouter":
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    def generate_completion(self, message: list[dict[str, str]]) -> str:
        if not message:
            raise ValueError("message is empty")

        if self.provider == "ollama":
            payload = {
                "model": self.model,
                "messages": message,
                "stream": False,
                "think": False,
                "format": "json",
                "options": {"temperature": 0},
            }
            url = OLLAMA_URL
        else:
            payload = {"model": self.model, "messages": message}
            url = OPENROUTER_URL

        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as exc:
            raise RuntimeError("The LLM provider request failed.") from exc
        except ValueError as exc:
            raise RuntimeError("The LLM provider returned invalid JSON.") from exc

        if self.provider == "ollama":
            content = result.get("message", {}).get("content")
        else:
            choices = result.get("choices", [])
            content = choices[0].get("message", {}).get("content") if choices else None

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("The LLM provider returned an empty response.")

        return content.strip()
