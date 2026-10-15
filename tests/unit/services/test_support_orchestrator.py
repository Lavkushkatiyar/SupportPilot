from unittest.mock import MagicMock, patch

from app.services.customer_support_orchestrator import (
    CustomerSupportOrchestrator,
)


def test_process_customer_message_auto_handle():
    session = MagicMock()
    customer_message = "I need help with my payment."

    classification = MagicMock()
    classification.intent.value = "billing"

    with (
        patch(
            "app.services.customer_support_orchestrator.IntentClassifier"
        ) as mock_classifier,
        patch(
            "app.services.customer_support_orchestrator.CustomerResponseGenerator"
        ) as mock_generator,
        patch(
            "app.services.customer_support_orchestrator.EscalationService.decide",
            return_value="auto_handle",
        ),
        patch(
            "app.services.customer_support_orchestrator.OrchestratorResponse"
        ) as mock_response,
    ):
        mock_classifier.return_value.classify.return_value = classification
        mock_generator.return_value.generate_response.return_value = (
            "Your payment was successful."
        )

        orchestrator = CustomerSupportOrchestrator()

        result = orchestrator.process_customer_message(session, customer_message)

        mock_classifier.return_value.classify.assert_called_once_with(customer_message)

        mock_generator.return_value.generate_response.assert_called_once_with(
            session, customer_message, "billing"
        )

        mock_response.assert_called_once_with(
            classification=classification,
            escalation="auto_handle",
            draft_response="Your payment was successful.",
        )

        assert result == mock_response.return_value


def test_process_customer_message_escalation():
    session = MagicMock()
    customer_message = "I want to speak to a human."

    classification = MagicMock()
    classification.intent.value = "complaint"

    with (
        patch(
            "app.services.customer_support_orchestrator.IntentClassifier"
        ) as mock_classifier,
        patch(
            "app.services.customer_support_orchestrator.CustomerResponseGenerator"
        ) as mock_generator,
        patch(
            "app.services.customer_support_orchestrator.EscalationService.decide",
            return_value="escalate",
        ),
        patch(
            "app.services.customer_support_orchestrator.OrchestratorResponse"
        ) as mock_response,
    ):
        mock_classifier.return_value.classify.return_value = classification

        orchestrator = CustomerSupportOrchestrator()

        result = orchestrator.process_customer_message(session, customer_message)

        mock_generator.return_value.generate_response.assert_not_called()

        mock_response.assert_called_once_with(
            classification=classification,
            escalation="escalate",
            draft_response=None,
        )

        assert result == mock_response.return_value
