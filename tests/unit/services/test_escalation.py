from typing import Literal

import pytest

from app.schemas.escalation import (
    EscalationAction,
    RiskLevel,
)
from app.schemas.intent import IntentClassification, IntentLabel
from app.services.response_pipeline.escalation_service import EscalationService


def test_unknown_intent_escalates_with_medium_risk() -> None:
    classification = IntentClassification(
        intent=IntentLabel.UNKNOWN_OR_INSUFFICIENT_CONTEXT,
        confidence="high",
        rationale="Insufficient information",
    )

    decision = EscalationService.decide(classification)

    assert decision.action == EscalationAction.ESCALATE
    assert decision.risk_level == RiskLevel.MEDIUM
    assert "not contain enough information" in decision.reason


def test_apple_id_security_escalates_with_high_risk() -> None:
    classification = IntentClassification(
        intent=IntentLabel.APPLE_ID_ACCOUNT_SECURITY,
        confidence="high",
        rationale="Account security issue",
    )

    decision = EscalationService.decide(classification)

    assert decision.action == EscalationAction.ESCALATE
    assert decision.risk_level == RiskLevel.HIGH
    assert "account access or security" in decision.reason


def test_low_confidence_escalates_with_medium_risk() -> None:
    classification = IntentClassification(
        intent=IntentLabel.DEVICE_HARDWARE_ISSUE,
        confidence="low",
        rationale="Uncertain device issue",
    )

    decision = EscalationService.decide(classification)

    assert decision.action == EscalationAction.ESCALATE
    assert decision.risk_level == RiskLevel.MEDIUM
    assert "low confidence" in decision.reason


@pytest.mark.parametrize("confidence", ["medium", "high"])
def test_supported_intent_with_sufficient_confidence_auto_handles(
    confidence: Literal["medium", "high"],
) -> None:
    classification = IntentClassification(
        intent=IntentLabel.DEVICE_HARDWARE_ISSUE,
        confidence=confidence,
        rationale="Hardware issue",
    )

    decision = EscalationService.decide(classification)

    assert decision.action == EscalationAction.AUTO_HANDLE
    assert decision.risk_level == RiskLevel.LOW
