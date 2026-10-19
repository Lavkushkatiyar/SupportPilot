from app.schemas.intent import IntentClassification
from app.services.ai.get_prompt import SYSTEM_PROMPT
from app.services.ai.llm_factory import get_llm_service


class IntentClassifier:
    def __init__(self) -> None:
        self.llm_service = get_llm_service()

    def classify(self, customer_message: str) -> IntentClassification:
        print("classifying the intent of message -> ", customer_message)
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"Customer message:\n{customer_message}",
            },
        ]

        response = self.llm_service.generate_completion(
            messages, response_format=IntentClassification.model_json_schema()
        )
        classification = IntentClassification.model_validate_json(response)

        return classification
