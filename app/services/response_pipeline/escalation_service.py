from app.schemas.escalation import EscalationAction, EscalationDecision, RiskLevel
from app.schemas.intent import IntentClassification, IntentLabel


class EscalationService:
    @staticmethod
    def decide(classification: IntentClassification) -> EscalationDecision:
        print("Escalation service in Action")
        if classification.intent == IntentLabel.UNKNOWN_OR_INSUFFICIENT_CONTEXT:
            return EscalationDecision(
                action=EscalationAction.ESCALATE,
                risk_level=RiskLevel.MEDIUM,
                reason=(
                    "The message does not contain enough information "
                    "to classify the customer's issue reliably."
                ),
            )
        if classification.intent == IntentLabel.APPLE_ID_ACCOUNT_SECURITY:
            return EscalationDecision(
                action=EscalationAction.ESCALATE,
                risk_level=RiskLevel.HIGH,
                reason=(
                    "The issue involves account access or security "
                    "and requires cautious human review."
                ),
            )
        if classification.confidence == "low":
            return EscalationDecision(
                action=EscalationAction.ESCALATE,
                risk_level=RiskLevel.MEDIUM,
                reason=(
                    "The intent classifier has low confidence, "
                    "so automated handling is not sufficiently reliable."
                ),
            )

        return EscalationDecision(
            action=EscalationAction.AUTO_HANDLE,
            risk_level=RiskLevel.LOW,
            reason=(
                "The issue has a supported intent and the classifier "
                "reports medium or high confidence."
            ),
        )
