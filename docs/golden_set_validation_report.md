# Golden Set Validation Report

- Rows: 200
- Unique tweet IDs: 200
- Duplicate tweet IDs: 0
- Missing intent labels: 0
- Missing escalation decisions: 0
- Missing escalation reasons: 0
- Review status values: human_reviewed_provisional

## Intent counts

- `app_store_purchase_billing`: 18
- `apple_id_account_security`: 9
- `battery_and_charging`: 24
- `connectivity_and_communication`: 18
- `device_hardware_issue`: 8
- `icloud_backup_data`: 8
- `settings_and_how_to`: 37
- `software_update_issue`: 31
- `unknown_insufficient_context`: 47

## Escalation decision counts

- `auto_handle`: 103
- `escalate_human`: 97

## Escalation reason counts

- `account_security_or_privacy`: 4
- `high_risk_or_sensitive`: 10
- `insufficient_context`: 62
- `none`: 103
- `requires_account_specific_action`: 17
- `unsupported_or_out_of_scope`: 4

## Important interpretation

This report checks basic structural completeness and uniqueness. It does not establish that labels are semantically correct. The set is a provisional, manually reviewed benchmark; see `golden_set_methodology.md`.
