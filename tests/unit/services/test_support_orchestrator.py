from unittest.mock import MagicMock, patch

from app.schemas.escalation import EscalationAction
from app.services.customer_support_orchestrator import CustomerSupportOrchestrator


def test_process_customer_message_auto_handles_request():
    session = MagicMock()
    customer_message = "Where is my order?"

    classification = MagicMock()
    classification.intent.value = "order_status"

    escalation = MagicMock()
    escalation.action = EscalationAction.AUTO_HANDLE

    draft_response = "Your order is currently being processed."

    with (
        patch(
            "app.services.customer_support_orchestrator.IntentClassifier"
        ) as mock_classifier_class,
        patch(
            "app.services.customer_support_orchestrator.CustomerResponseGenerator"
        ) as mock_generator_class,
        patch(
            "app.services.customer_support_orchestrator.EscalationService.decide",
            return_value=escalation,
        ) as mock_decide,
        patch(
            "app.services.customer_support_orchestrator.OrchestratorResponse"
        ) as mock_response_class,
    ):
        mock_classifier_class.return_value.classify.return_value = classification
        mock_generator_class.return_value.generate_response.return_value = (
            draft_response
        )

        orchestrator = CustomerSupportOrchestrator()

        result = orchestrator.process_customer_message(session, customer_message)

        mock_classifier_class.return_value.classify.assert_called_once_with(
            customer_message
        )

        mock_decide.assert_called_once_with(classification)

        mock_generator_class.return_value.generate_response.assert_called_once_with(
            session,
            customer_message,
            classification.intent.value,
        )

        mock_response_class.assert_called_once_with(
            classification=classification,
            escalation=escalation,
            draft_response=draft_response,
        )

        assert result == mock_response_class.return_value


def test_process_customer_message_does_not_generate_response_when_escalation_required():
    session = MagicMock()
    customer_message = "I want to speak to a human agent."

    classification = MagicMock()
    classification.intent.value = "complaint"

    escalation = MagicMock()
    escalation.action = next(
        action for action in EscalationAction if action != EscalationAction.AUTO_HANDLE
    )

    with (
        patch(
            "app.services.customer_support_orchestrator.IntentClassifier"
        ) as mock_classifier_class,
        patch(
            "app.services.customer_support_orchestrator.CustomerResponseGenerator"
        ) as mock_generator_class,
        patch(
            "app.services.customer_support_orchestrator.EscalationService.decide",
            return_value=escalation,
        ) as mock_decide,
        patch(
            "app.services.customer_support_orchestrator.OrchestratorResponse"
        ) as mock_response_class,
    ):
        mock_classifier_class.return_value.classify.return_value = classification

        orchestrator = CustomerSupportOrchestrator()

        result = orchestrator.process_customer_message(session, customer_message)

        mock_classifier_class.return_value.classify.assert_called_once_with(
            customer_message
        )

        mock_decide.assert_called_once_with(classification)

        mock_generator_class.return_value.generate_response.assert_not_called()

        mock_response_class.assert_called_once_with(
            classification=classification,
            escalation=escalation,
            draft_response=None,
        )

        assert result == mock_response_class.return_value
