SupportLens Golden Set V2 — Review Draft
Status
This is a second-pass annotation draft, not yet a finalized gold-standard benchmark.
It preserves the original 200 messages and source annotations, adds the new
other_or_out_of_scope label, and records proposed V2 labels with review notes.
Every row remains marked needs_human_adjudication; the draft must not be
presented as independently human-validated.
Label definitions
- software_update_issue: installing/updating/rolling back an OS, or a problem explicitly caused by an OS update.
- battery_and_charging: battery life, battery behavior, charging, or charger problems.
- device_hardware_issue: physical/device-level hardware failure, excluding primary battery/charging issues.
- icloud_backup_data: iCloud, backups, restore, transfer, or loss/access to personal data.
- apple_id_account_security: Apple ID access/authentication/recovery/security.
- app_store_purchase_billing: App Store downloads/updates, purchases, refunds, subscriptions, and billing.
- connectivity_and_communication: Wi-Fi, Bluetooth, cellular, calls, iMessage, FaceTime, or connection failures.
- settings_and_how_to: how to configure, enable/disable, or use a device feature; not a direct technical failure.
- unknown_or_insufficient_context: the message lacks enough detail to identify the issue.
- other_or_out_of_scope: the issue is understandable but falls outside the eight defined support intents, such as order delivery or a standalone support-process complaint.
Annotation rules
1. Label the primary issue stated in the message, not a guessed cause.
2. Do not infer that an issue was caused by an OS update merely because an update is mentioned.
3. Use unknown_or_insufficient_context when the issue itself cannot be identified.
4. Use other_or_out_of_scope when the issue is identifiable but outside the taxonomy.
5. Preserve the original labels and notes for auditability. Do not overwrite historical annotations.
6. Resolve low-confidence and ambiguous rows through independent human review before using this as the final benchmark.
7. For conversations where a single tweet depends on prior turns, retrieve the conversation context before finalizing its label; the current classifier input may still be the individual message, so document that limitation.
Draft label counts
- app_store_purchase_billing: 17
- apple_id_account_security: 9
- battery_and_charging: 24
- connectivity_and_communication: 18
- device_hardware_issue: 8
- icloud_backup_data: 8
- other_or_out_of_scope: 4
- settings_and_how_to: 37
- software_update_issue: 30
- unknown_or_insufficient_context: 45
Validation
- Rows: 200
- Unique tweet IDs: 200
- Proposed labels valid against the V2 label inventory: yes
- Rows marked for human adjudication: 200
Important limitation
Most labels are provisional carry-forwards from the previous annotation. The notes identify
the need to verify each row; this file is a structured review draft, not evidence that
all 200 examples have already been independently relabeled.