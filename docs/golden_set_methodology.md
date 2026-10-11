# Golden Evaluation Set: Annotation Methodology

## Purpose

This document records how SupportPilot's initial golden evaluation set was assembled and reviewed. The set is intended to support iterative evaluation of intent classification and escalation decisions; it is not presented as a perfectly adjudicated or independently validated benchmark.

## Dataset construction

- Target size: 200 incoming customer messages.
- Source: the processed Apple Support conversations dataset.
- Sampling script: `scripts/dataset/sample_golden_set.py`.
- Sampling approach: incoming, non-empty messages; deduplication by `tweet_id`; one message per conversation where possible; a mixture of keyword candidates, potentially overlapping intents, short/unmatched messages, and random examples.
- `candidate_intents` and `sampling_group` are sampling aids only. They are not ground-truth labels and must not be used as evaluation targets.

## Annotation and review

Labels were drafted with AI assistance and then manually reviewed by the project author. The labels are retained as a pragmatic first benchmark after review, with the understanding that some ambiguity and classification errors may remain. The annotations have not been independently double-labelled, adjudicated by multiple reviewers, or validated by a domain expert.

`review_status=human_reviewed_provisional` means the dataset has received a practical manual review and is approved for the current development/evaluation workflow, while remaining provisional rather than authoritative ground truth.

## Label schema

### Intent

The supported intent taxonomy is:

- `software_update_issue`
- `battery_and_charging`
- `device_hardware_issue`
- `icloud_backup_data`
- `apple_id_account_security`
- `app_store_purchase_billing`
- `connectivity_and_communication`
- `settings_and_how_to`
- `unknown_insufficient_context`

`unknown_insufficient_context` is an operational label for messages that do not provide enough evidence to confidently assign one of the supported intents. It should be treated as an explicit fallback label, not as a catch-all for every out-of-scope topic.

Some messages may fall outside the eight core intent categories. Those examples can expose taxonomy gaps; do not silently reinterpret them as strong examples of a supported intent. Record notable gaps in evaluation findings and revisit the taxonomy if they materially affect results.

### Escalation

- `escalation_decision`: `auto_handle` or `escalate_human`
- `escalation_reason`: `none`, `insufficient_context`, `account_security_or_privacy`, `high_risk_or_sensitive`, `requires_account_specific_action`, `unsupported_or_out_of_scope`, or `other`

For `auto_handle`, the expected escalation reason is `none`. For `escalate_human`, the reason should explain why automation is not appropriate.

## Limitations

1. The sample is drawn from Apple Support social conversations and may not represent all customer-support channels or products.
2. Sampling is partly stratified using keyword heuristics; it is not a random sample of the source population.
3. AI-assisted draft annotations and a single-person review can leave residual errors and reviewer bias.
4. Some messages are short, sarcastic, context-dependent, or missing the preceding conversation.
5. The intent taxonomy may not cover every topic present in the source data.
6. Metrics on this set should be reported as development-benchmark results, not as proof of production performance.

## Evaluation safeguards

- Keep this annotation file versioned and do not change labels merely to improve model scores.
- If a label is changed after an evaluation reveals an error, document the reason and re-run the evaluation against the updated version.
- Report per-intent metrics and confusion patterns, not only aggregate accuracy.
- Track escalation precision/recall and review false negatives carefully.
- Treat `unknown_insufficient_context` as a meaningful class and report its performance separately.
- Record model/provider version, prompt version, and evaluation date for each run.

