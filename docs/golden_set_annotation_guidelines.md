# Golden Evaluation Set — Annotation Guidelines

## Purpose

Create a human-labelled evaluation set for SupportPilot's Apple Support intent
classification and escalation decisions. Labels must represent human judgement,
not keyword matches or model predictions.

## Unit of annotation

One row represents one incoming customer message. Preserve its original
`tweet_id` and `conversation_id`. The `text` field must be the original message.
Only customer/inbound messages are eligible classification inputs.

## Intent labels

Use the existing taxonomy in `docs/intent_taxonomy.md`. Do not create new
intent labels during annotation without updating and reviewing the taxonomy.

- `software_update_issue`
- `battery_and_charging`
- `device_hardware_issue`
- `icloud_backup_data`
- `apple_id_account_security`
- `app_store_purchase_billing`
- `connectivity_and_communication`
- `settings_and_how_to`
- `unknown_insufficient_context` — use when the available message does not
  provide enough information to reliably select one of the eight intents.

The last value is a machine-friendly name for the taxonomy's
“Unknown / Insufficient Context” outcome. If a message is understandable but
does not fit any supported intent, flag it for review in `annotation_notes`
rather than silently forcing it into a category. Resolve whether a separate
out-of-scope label is needed before finalising the set.

## Intent decision rules

1. Select the customer's primary support problem, not every topic mentioned.
2. Use the customer's explicit complaint or request as the strongest evidence.
3. A contextual mention does not automatically determine the intent. For
   example, battery drain after an OS update is `battery_and_charging` when
   battery drain is the main complaint.
4. Use `software_update_issue` when installing, upgrading, or rolling back the
   operating system is itself the main problem.
5. Use `settings_and_how_to` for a request for configuration instructions;
   use a more specific intent when the customer reports a concrete failure.
6. Do not infer a cause that the message does not establish.
7. If multiple intents seem plausible, choose the best-supported primary
   intent and explain the ambiguity in `annotation_notes`.
8. Use `unknown_insufficient_context` for messages such as “please fix this”
   when the message alone does not identify the problem. If surrounding
   conversation context is supplied during annotation, apply one consistent
   context policy to every example and record the actual classification input.

## Escalation annotation

These fields are separate from intent. Do not assume that an intent always
requires or never requires escalation.

`escalation_decision`:
- `auto_handle` — a bounded, low-risk response can reasonably be drafted
  without a human taking over.
- `escalate_human` — a human should review or handle the case.

`escalation_reason`:
- `none` — use when `escalation_decision` is `auto_handle`.
- `insufficient_context` — the issue cannot be handled reliably with the
  available information.
- `account_security_or_privacy` — account compromise, sensitive access, or
  privacy concerns need human review.
- `high_risk_or_sensitive` — the message indicates a potentially harmful or
  otherwise sensitive situation that should not be auto-handled.
- `requires_account_specific_action` — resolution requires an account-specific
  action or verification that the agent cannot safely perform.
- `unsupported_or_out_of_scope` — the request is outside the supported intents
  or the agent's defined capabilities.
- `other` — use only when none of the above fits; explain in `annotation_notes`.

These are initial operational guidelines and should be reviewed against the
assignment's intended escalation policy before annotation starts.

## Annotation notes

`annotation_notes` is optional. Add a concise explanation for ambiguous,
borderline, or out-of-scope examples. Leave it empty for straightforward cases.

## Quality-control checklist

Before accepting a row:
- Confirm the message is an inbound customer message.
- Preserve `tweet_id`, `conversation_id`, and the original text.
- Assign exactly one valid intent label.
- Assign an escalation decision and a compatible reason.
- Explain ambiguous decisions in `annotation_notes`.
- Do not use keyword/model output as the ground-truth label.

## Important evaluation practice

Keep the golden set separate from data used to tune prompts, rules, or models.
Once finalised, version it and avoid repeated tuning against its labels. Report
the sampling method and acknowledge that a deliberately balanced or
difficulty-enriched sample does not represent natural production prevalence.
