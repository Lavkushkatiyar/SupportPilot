from pydantic import BaseModel, ConfigDict

from app.schemas.escalation import EscalationDecision
from app.schemas.intent import IntentClassification


class OrchestratorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    classification: IntentClassification
    escalation: EscalationDecision
    draft_response: str | None = None
