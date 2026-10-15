from app.services.generate_text import LLMService


class ResponseGenerator:
    def __init__(self, llm: LLMService) -> None:
        self.llm = llm

    def generate_reply(
        self, customer_message: str, intent: str, historical_cases
    ) -> str:
        evidence = [
            f"Historical case {index}:\n{case}"
            for index, case in enumerate(historical_cases, start=1)
        ]

        evidence = "\n\n".join(evidence)

        if not evidence:
            evidence = "No relevant historical cases were retrieved."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a customer-support reply assistant. "
                    "Draft concise, professional responses. "
                    "Use historical cases as evidence, not as official policy. "
                    "Do not invent policies, guarantees, or resolutions. "
                    "If the evidence is insufficient, ask a clarifying "
                    "question or recommend human review. "
                    "Return only the proposed customer-facing reply."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Customer message:\n{customer_message}\n\n"
                    f"Predicted intent:\n{intent}\n\n"
                    f"Retrieved historical cases:\n{evidence}\n\n"
                    "Draft an appropriate support reply."
                ),
            },
        ]

        return self.llm.generate_completion(messages)
