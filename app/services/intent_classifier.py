from app.schemas.intent import IntentClassification
from app.services.generate_text import LLMService
from app.services.get_prompt import SYSTEM_PROMPT


class IntentClassifier:
    def __init__(self) -> None:
        self.llm_service = LLMService()

    def classify(self, customer_message: str) -> IntentClassification:
        print(customer_message)
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
