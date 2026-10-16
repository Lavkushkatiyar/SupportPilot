from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict


class IntentLabel(StrEnum):
    SOFTWARE_UPDATE_ISSUE = "software_update_issue"
    BATTERY_AND_CHARGING = "battery_and_charging"
    DEVICE_HARDWARE_ISSUE = "device_hardware_issue"
    ICLOUD_BACKUP_DATA = "icloud_backup_data"
    APPLE_ID_ACCOUNT_SECURITY = "apple_id_account_security"
    APP_STORE_PURCHASE_BILLING = "app_store_purchase_billing"
    CONNECTIVITY_AND_COMMUNICATION = "connectivity_and_communication"
    SETTINGS_AND_HOW_TO = "settings_and_how_to"
    UNKNOWN_OR_INSUFFICIENT_CONTEXT = "unknown_or_insufficient_context"
    OTHER_OR_OUT_OF_SCOPE = "other_or_out_of_scope"


class IntentClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: IntentLabel
    confidence: Literal["low", "medium", "high"]
    rationale: str
