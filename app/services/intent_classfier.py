import json

from app.schemas.intent import IntentClassification, IntentLabel
from app.services.generate_text import LLMService


class IntentClassifier:
    def __init__(self) -> None:
        self.llm_service = LLMService()

    def classify(self, customer_message: str) -> IntentClassification:
        allowed_intents = [intent.value for intent in IntentLabel]
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intent classifier for Apple Support customer "
                    "messages.\n"
                    "Select exactly one intent from the allowed labels.\n"
                    "Choose the primary intent when multiple issues appear.\n"
                    "Do not infer information that the customer has not "
                    "provided. Use unknown_or_insufficient_context when the "
                    "message does not contain enough information to make a "
                    "defensible classification.\n\n"
                    f"Allowed intents: {json.dumps(allowed_intents)}\n\n"
                    "Return only a valid JSON object with these fields:\n"
                    '{"intent": "<allowed label>", '
                    '"confidence": "low|medium|high", '
                    '"rationale": "<brief explanation>"}'
                ),
            },
            {
                "role": "user",
                "content": f"Customer message:\n{customer_message}",
            },
        ]

        response = self.llm_service.generate_completion(messages)
        classification = IntentClassification.model_validate_json(response)

        return classification
