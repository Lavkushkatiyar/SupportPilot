from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EscalationAction(StrEnum):
    AUTO_HANDLE = "auto_handle"
    ESCALATE = "escalate"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EscalationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: EscalationAction
    risk_level: RiskLevel
    reason: str = Field(min_length=1)
