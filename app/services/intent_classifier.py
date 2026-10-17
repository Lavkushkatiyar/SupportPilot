import json

from app.schemas.intent import IntentClassification, IntentLabel
from app.services.generate_text import LLMService


class IntentClassifier:
    def __init__(self) -> None:
        self.llm_service = LLMService()

    def classify(self, customer_message: str) -> IntentClassification:
        allowed_intents = [intent.value for intent in IntentLabel]
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intent classifier for Apple Support customer"
                    "messages.\n"
                    "Select exactly one intent from the allowed labels.\n"
                    "Classify the customer's primary support problem, "
                    "not every topic mentioned.\n"
                    "Do not infer causes or details that the customer "
                    "has not provided.\n\n"
                    "Use these classification rules:\n"
                    "1. software_update_issue: Problems installing, updating, "
                    "upgrading, or rolling back iOS/macOS, or problems "
                    "clearly caused by an OS update.\n"
                    "2. battery_and_charging: Battery life, rapid drain, "
                    "charging, or charger problems.\n"
                    "3. device_hardware_issue: Physical damage or hardware "
                    "failure, excluding battery/charging problems when "
                    "those are the primary issue.\n"
                    "4. icloud_backup_data: iCloud, backups, restoring, "
                    "transferring, or losing personal data.\n"
                    "5. apple_id_account_security: Apple ID access, "
                    "authentication, recovery, passwords, or account security.\n"
                    "6. app_store_purchase_billing: App Store downloads/updates, "
                    "purchases, refunds, subscriptions, or billing.\n"
                    "7. connectivity_and_communication: Wi-Fi, Bluetooth, "
                    "cellular, calls, iMessage, FaceTime, or connection failures.\n"
                    "8. settings_and_how_to: Requests for instructions to "
                    "configure, enable, disable, or use a feature. "
                    "Do not use this for a direct technical failure "
                    "that needs troubleshooting.\n"
                    "9. unknown_or_insufficient_context: The message does "
                    "not provide enough information to identify the "
                    "customer's primary issue.\n"
                    "10. other_or_out_of_scope: The issue is understandable, "
                    "but it does not fit any of the eight defined support "
                    "intents, such as an order-delivery complaint or a "
                    "standalone support-process complaint.\n\n"
                    "Important distinctions:\n"
                    "- Mentioning an OS update does not prove that the "
                    "update caused the problem.\n"
                    "- An identifiable app-specific problem unrelated "
                    "to purchases is not app_store_purchase_billing.\n"
                    "- Use unknown_or_insufficient_context when the issue "
                    "is unclear.\n"
                    "- Use other_or_out_of_scope when the issue is clear "
                    "but outside the taxonomy.\n"
                    "- Choose the best-supported primary intent; do not guess.\n\n"
                    f"Allowed intents: {json.dumps(allowed_intents)}\n\n"
                    "Return only a valid JSON object with these fields:\n"
                    '{"intent": "<allowed label>", '
                    '"confidence": "low|medium|high", '
                    '"rationale": "<brief explanation>"}'
                ),
            },
            {
                "role": "user",
                "content": f"Customer message:\n{customer_message}",
            },
        ]

        response = self.llm_service.generate_completion(messages)
        classification = IntentClassification.model_validate_json(response)

        return classification
