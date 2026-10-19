import os

import requests
from dotenv import load_dotenv

load_dotenv()

REQUEST_TIMEOUT_SECONDS = 600

OLLAMA_URL = "http://localhost:11434/api/chat"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMService:
    """Generate text using Ollama or OpenRouter with automatic fallback."""

    def __init__(
        self,
        provider: str = "ollama",
        model: str | None = None,
        api_key: str | None = None,
        fallback_model: str | None = None,
        openrouter_limit: int = 50,
    ) -> None:
        self.provider = provider.lower()
        self.openrouter_limit = openrouter_limit
        self.openrouter_requests = 0

        if openrouter_limit < 0:
            raise ValueError("openrouter_limit cannot be negative.")

        self.fallback_model = fallback_model or os.getenv("OLLAMA_MODEL", "qwen3:8b")

        if self.provider == "ollama":
            self.model = model or self.fallback_model
            self.api_key = None

        elif self.provider == "openrouter":
            self.model = model or os.getenv("OPENROUTER_MODEL")
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY is not configured.")

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

        if not self.model:
            raise ValueError(f"Model is not configured for {self.provider}.")

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    def generate_completion(
        self,
        message: list[dict[str, str]],
        response_format: str | dict = "json",
    ) -> str:
        if not message:
            raise ValueError("message is empty")

        use_openrouter = (
            self.provider == "openrouter"
            and self.openrouter_requests < self.openrouter_limit
        )

        provider = "openrouter" if use_openrouter else "ollama"
        model = self.model if use_openrouter else self.fallback_model
        url = OPENROUTER_URL if use_openrouter else OLLAMA_URL

        if model is None:
            raise RuntimeError(f"Model is not configured for {provider}.")

        if use_openrouter:
            self.openrouter_requests += 1

        try:
            print(model, provider)
            return self._generate(
                provider,
                model,
                url,
                message,
                response_format,  # type: ignore
            )
        except (requests.RequestException, RuntimeError, ValueError) as exc:
            if not use_openrouter:
                raise

            print(f"OpenRouter failed: {exc}. Falling back to Ollama.")

            return self._generate(
                "ollama",
                self.fallback_model,
                OLLAMA_URL,
                message,
                response_format,
            )

    def _generate(
        self,
        provider: str,
        model: str,
        url: str,
        message: list[dict[str, str]],
        response_format: str | dict,
    ) -> str:
        payload = self._build_payload(provider, model, message, response_format)
        result = self._post_request(url, payload)
        content = self._extract_content(result, provider)

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(f"{provider} returned an empty response.")

        if provider == "ollama":
            self._print_ollama_metrics(result)

        return content.strip()

    def _build_payload(
        self,
        provider: str,
        model: str,
        message: list[dict[str, str]],
        response_format: str | dict,
    ) -> dict:
        if provider == "ollama":
            return {
                "model": model,
                "messages": message,
                "stream": False,
                "think": False,
                "format": response_format,
                "keep_alive": "30m",
                "options": {
                    "temperature": 0,
                    "num_ctx": 8192,
                },
            }

        payload = {
            "model": model,
            "messages": message,
            "stream": False,
            "temperature": 0,
        }

        if isinstance(response_format, dict):
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "intent_classification",
                    "strict": True,
                    "schema": response_format,
                },
            }
        elif response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        return payload

    def _post_request(self, url: str, payload: dict) -> dict:
        response = self.session.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if not response.ok:
            print(f"LLM endpoint: {url}")
            print(f"HTTP status: {response.status_code}")
            print(f"LLM error: {response.text}")

        response.raise_for_status()
        return response.json()

    @staticmethod
    def _extract_content(
        result: dict,
        provider: str,
    ) -> str | None:
        if provider == "ollama":
            return result.get("message", {}).get("content")

        choices = result.get("choices", [])
        return choices[0].get("message", {}).get("content") if choices else None

    @staticmethod
    def _print_ollama_metrics(result: dict) -> None:
        duration_keys = (
            "load_duration",
            "prompt_eval_duration",
            "eval_duration",
            "total_duration",
        )

        metrics = {
            key: (
                round(result[key] / 1_000_000_000, 3)
                if isinstance(result.get(key), (int, float))
                else None
            )
            for key in duration_keys
        }

        metrics["prompt_eval_count"] = result.get("prompt_eval_count")
        metrics["eval_count"] = result.get("eval_count")

        print(f"Ollama metrics: {metrics}")
