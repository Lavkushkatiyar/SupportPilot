# Golden Evaluation Set — Sampling Plan

## Target

200 unique incoming customer messages from the processed Apple Support
conversation dataset.

## Candidate groups

Use these as initial targets, then adjust based on the real dataset:
- 120 clear-intent candidates, distributed across the eight taxonomy labels
  according to available examples while ensuring rare categories are reviewed.
- 50 candidates where keyword analysis matches multiple intents.
- 30 difficult candidates, such as short/noisy messages, unmatched messages,
  and messages that may lack enough context.

A message may qualify for more than one candidate group. Deduplicate by
`tweet_id` and document the final allocation rather than counting it twice.

## Sampling controls

- Exclude outbound support messages (`inbound = false`).
- Keep original `tweet_id`, `conversation_id`, and `text`.
- Use a fixed random seed and record it in the sampling script/report.
- Avoid duplicate tweet IDs.
- If a separate development partition is introduced, keep all messages from
  a conversation in the same partition.
- Use keyword matches only to locate candidate examples; annotators assign
  ground-truth labels independently.
- Do not claim the set reflects production prevalence if it is balanced or
  enriched with difficult examples.

## Before sampling

Review the current taxonomy and keyword analysis for label-name drift. The
existing keyword script may use labels that differ from the current taxonomy.
Do not silently map old keyword names to new intent names without checking
their meaning.

## Final validation

Record:
- total rows and unique tweet IDs;
- missing text, identifiers, intents, or escalation labels;
- invalid labels and incompatible escalation/reason combinations;
- intent and escalation distributions;
- counts of multi-intent and difficult candidates;
- random seed and sampling method;
- annotation review limitations.
