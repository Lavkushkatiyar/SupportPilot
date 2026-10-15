import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
REQUEST_TIMEOUT_SECONDS = 30


class LLMService:
    """Client for generating text through OpenRouter."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("MODEL")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        if not self.model:
            raise ValueError("OPENROUTER_MODEL is not configured.")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def generate_completion(self, message: list[dict[str, str]]) -> str:
        if not message:
            raise ValueError("message is empty")
        payload = {"model": self.model, "messages": message}
        try:
            response = self.session.post(
                API_URL, json=payload, timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            result = response.json()

        except requests.RequestException as exc:
            raise RuntimeError("The LLM provider request failed.") from exc

        except ValueError as exc:
            raise RuntimeError("The LLM provider returned invalid JSON.") from exc

        choices = result.get("choices", [])
        if not choices:
            raise RuntimeError("The LLM provider returned no completion choices.")

        content = choices[0].get("message", {}).get("content")

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("The LLM provider returned an empty response.")

        return content.strip()
