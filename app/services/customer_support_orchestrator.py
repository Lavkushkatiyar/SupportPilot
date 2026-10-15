from sqlalchemy.orm import Session

from app.schemas.customer_support_orchestrator import OrchestratorResponse
from app.services.customer_response_generator import CustomerResponseGenerator
from app.services.escalation_service import EscalationService
from app.services.intent_classifier import IntentClassifier


class CustomerSupportOrchestrator:
    def __init__(self) -> None:
        self.intent_classifier = IntentClassifier()
        self.response_generator = CustomerResponseGenerator()

    def process_customer_message(
        self, session: Session, customer_message: str
    ) -> OrchestratorResponse:
        classification = self.intent_classifier.classify(customer_message)
        escalation = EscalationService.decide(classification)
        draft_response = None

        if escalation == "auto_handle":
            draft_response = self.response_generator.generate_response(
                session, customer_message, classification.intent.value
            )

        return OrchestratorResponse(
            classification=classification,
            escalation=escalation,
            draft_response=draft_response,
        )
