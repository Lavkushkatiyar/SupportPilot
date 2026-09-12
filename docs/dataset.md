# Dataset Exploration

## Dataset

- Source: Customer Support on Twitter
- File: `data/raw/twcs.csv`
- Total tweets: 2,811,774
- Selected support account: `AppleSupport`

The raw dataset is kept locally and is not committed to the repository.

---

## 1. Dataset Structure

The dataset contains 7 columns:

| Column | Type | Purpose |
|---|---|---|
| `tweet_id` | `i64` | Unique tweet identifier |
| `author_id` | `str` | Tweet author/account |
| `inbound` | `bool` | Indicates whether the tweet is inbound to the support account |
| `created_at` | `str` | Tweet creation timestamp |
| `text` | `str` | Tweet content |
| `response_tweet_id` | `str` | Identifier(s) of response tweet(s) |
| `in_response_to_tweet_id` | `i64` | Identifier of the tweet being replied to |

A row represents an individual tweet rather than an entire conversation.

---

## 2. Customer vs Support Messages

The `inbound` field provides the initial distinction between customer and support-side messages.

Observed examples show:

- `inbound = true` → customer/user message
- `inbound = false` → support/brand message

Dataset distribution:

| Direction | Count |
|---|---:|
| Inbound / customer | 1,537,843 |
| Outbound / support | 1,273,931 |
| **Total** | **2,811,774** |

This distinction will be used when reconstructing customer-support conversations.

---

## 3. Conversation Relationships

The dataset contains explicit tweet-to-tweet reply relationships through
`in_response_to_tweet_id`.

| Relationship | Count |
|---|---:|
| Tweets without a recorded parent | 794,335 |
| Tweets with a recorded parent | 2,017,439 |
| **Total** | **2,811,774** |

Therefore, approximately 71.7% of tweets have a recorded parent tweet.

The CSV row order is not chronological. Conversation order must therefore be reconstructed using tweet relationships and timestamps rather than relying on dataset row order.

---

## 4. Parent Reference Integrity

Among tweets with a recorded parent:

- Tweets with a parent: 2,017,439
- Parent references whose target tweet is missing: 3,862

This represents approximately 0.19% of tweets with a recorded parent.

Therefore, the vast majority of reply references point to tweets that are present in the dataset.

Missing parent references will need to be handled during conversation processing rather than assumed to be complete.

---

## 5. Support Account Discovery

Support-side tweets were grouped by `author_id` to identify the largest support accounts in the dataset.

Top candidates observed:

| Rank | Support account | Support tweets |
|---:|---|---:|
| 1 | `AmazonHelp` | 169,840 |
| 2 | `AppleSupport` | 106,860 |
| 3 | `Uber_Support` | 56,270 |
| 4 | `SpotifyCares` | 43,265 |
| 5 | `Delta` | 42,253 |
| 6 | `Tesco` | 38,573 |
| 7 | `AmericanAir` | 36,764 |
| 8 | `TMobileHelp` | 34,317 |
| 9 | `comcastcares` | 33,031 |
| 10 | `British_Airways` | 29,361 |
| 11 | `SouthwestAir` | 28,977 |
| 12 | `VirginTrains` | 27,817 |
| 13 | `Ask_Spectrum` | 25,860 |
| 14 | `XboxSupport` | 24,557 |
| 15 | `sprintcare` | 22,381 |

---

## 6. Brand Selection

### Selected brand: `AppleSupport`

`AppleSupport` was selected as the support account for the project.

The account has 106,860 support-side tweets, providing a substantial historical support corpus for the assignment.

The dataset also provides the necessary conversation structure:

- customer/support direction through `inbound`
- parent-child relationships through `in_response_to_tweet_id`
- response relationships through `response_tweet_id`
- timestamps for chronological ordering

The next stage will therefore focus on extracting and reconstructing usable historical `AppleSupport` conversations.

---

## 7. Key Findings

1. The dataset contains individual tweets rather than pre-built conversations.
2. Customer and support turns can be distinguished using `inbound`.
3. Most tweets participate in an explicit reply relationship.
4. Reply references are highly complete, with only 3,862 unresolved parent references among 2,017,439 parent-linked tweets.
5. Dataset row order cannot be used as conversation order.
6. Reply IDs and timestamps provide the basis for conversation reconstruction.
7. `AppleSupport` has sufficient support-side volume to serve as the project's selected brand.

---

## 8. Story 3 Outcome

Dataset exploration is complete.

The next stage is **Story 4 — Conversation Processing**, where the raw AppleSupport-related tweets will be transformed into structured, usable customer-support conversations.