import json
from pathlib import Path

from app.schemas.intent import IntentLabel

ALLOWED_INTENT = [intent.value for intent in IntentLabel]

PROMPT_FILE = Path(__file__).with_name("intent_prompt.txt")


def load_system_prompt() -> str:
    prompt_template = PROMPT_FILE.read_text(encoding="utf-8")
    allowed_intents = json.dumps(ALLOWED_INTENT)

    return prompt_template.replace(
        "__ALLOWED_INTENTS__",
        allowed_intents,
    )


SYSTEM_PROMPT = load_system_prompt()
