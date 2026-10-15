import os

import requests
from dotenv import load_dotenv

load_dotenv()


API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")


def main() -> None:
    if not API_KEY or not MODEL:
        raise RuntimeError("Set OPENROUTER_API_KEY and OPENROUTER_MODEL in .env")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a customer-support assistant. "
                    "Give concise, evidence-conscious responses. "
                    "Never invent company policies."
                ),
            },
            {
                "role": "user",
                "content": ("My spotify is not opening after update. Can you help me?"),
            },
        ],
    }

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

    except requests.RequestException as exc:
        raise RuntimeError(
            "OpenRouter request failed. Check the API key, "
            "model availability, network, and API limits."
        ) from exc

    choices = result.get("choices", [])
    if not choices:
        raise RuntimeError(f"No completion returned: {result}")

    message = choices[0].get("message", {})
    content = message.get("content")

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("The model returned no usable text.")

    print(f"Model: {result.get('model', MODEL)}")
    print(f"\nGenerated response:\n{content}")


if __name__ == "__main__":
    main()
