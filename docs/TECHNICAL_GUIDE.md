# SupportPilot Technical Guide

This guide describes the repository as it is implemented today. It separates
working code and verified local checks from assignment requirements that still
need evidence. The project overview and quick demo are in the [README](../README.md).

## 1. Project overview

SupportPilot is an experimental support-agent backend for Apple Support-style
messages. The FastAPI endpoint classifies a message using an OpenRouter chat
completion, applies deterministic escalation rules, and, when the rules allow
auto-handling, retrieves similar cases from PostgreSQL/pgvector and asks the
configured chat model to draft a reply.

Current implementation status:

| Capability | Status |
|---|---|
| Versioned Python modules and API | Router code is organized under `app/api/v1`, but the router is mounted without an `/api/v1` URL prefix. |
| Intent classification | Implemented through an external chat-completion call and Pydantic validation. |
| Escalation | Implemented as deterministic rules for insufficient context, Apple ID/account security, and low confidence. |
| Retrieval and draft generation | Implemented; requires historical cases with 384-dimensional vectors, the sentence-transformer model, database connectivity, and OpenRouter configuration. |
| Authentication | Registration and login code exist. JWT validation helper exists but is not wired to the support route. |
| Golden set | A checked-in 200-row CSV and supporting methodology/validation documents exist; the set is provisional. |
| Evaluation results | No baseline runner, reply-quality judge, human-judge agreement result, or completed failure analysis was found. |

The service drafts text only. It does not perform account actions or claim to
represent official Apple policies.

## 2. Technology stack

| Technology | Use in this repository | Developer interaction / considerations |
|---|---|---|
| Python and `uv` | Application, scripts, and dependency management; package metadata is in `pyproject.toml`, with `uv.lock` for locked resolution. The project requires Python `>=3.14`. | Install/sync with `uv sync --locked`; invoke tools with `uv run`. CI currently installs Python 3.12, which conflicts with the declared minimum and needs reconciliation. |
| FastAPI / Pydantic | API routing, request validation, response schemas, and generated OpenAPI docs. | Run with `./dev.sh server`; inspect `/docs` and `/openapi.json`. Module folder `v1` does not currently make the public path versioned. |
| SQLAlchemy | ORM models, sessions, and database access. | Configure `DATABASE_URL`; sessions are created by `SessionLocal` and closed in the request dependency. |
| PostgreSQL and pgvector | Persistent users, conversations, messages, historical cases, and vector distance search. | Compose uses `pgvector/pgvector:pg16`, container port `5432`, host port `5433`, database `supportpilot`. |
| Alembic | Schema migration history and execution. | Use `uv run alembic current`, `uv run alembic heads`, and `uv run alembic upgrade head`. |
| Redis | Counter-based rate limiting on the authentication router. | `REDIS_URL` defaults to `redis://localhost:6379`; Compose exposes port `6379`. |
| Sentence Transformers | Generates 384-dimensional query/case vectors with `sentence-transformers/all-MiniLM-L6-v2`. | First use may need the model available from the Hugging Face model hub and local cache. |
| OpenRouter | Chat-completion endpoint used for intent classification and customer-facing draft text. | `app/services/generate_text.py` reads `OPENROUTER_API_KEY` and `MODEL`. The error message names `OPENROUTER_MODEL` for the latter, but the implementation reads `MODEL`. Requests have a 30-second timeout. |
| Polars | Reads the source CSV, processes conversations, and reads/writes Parquet. | Use the scripts under `scripts/dataset/` and `scripts/db_load/`. The full raw CSV is large; use the loader's `--limit` for a small DB load after processing. |
| Docker Compose | Local PostgreSQL/pgvector and Redis services. | Start with `./dev.sh infra` or `docker compose up -d postgres redis`. Set `POSTGRES_PASSWORD` in local configuration; it is not present in `.env.example`. |
| pytest, Ruff, Pyright | Test runner, linter/formatter, and static type checker. | CI runs Ruff and Pyright but currently does not run pytest. `pyproject.toml` contains an invalid/unknown pytest option `gpythonpath`, which pytest warns about. |
| Bruno | API request collection under `bruno/SupportPilot/`. | The checked-in collection contains registration and login requests only. Login currently has no request body even though the API schema requires email and password. |
| GitHub Actions | `.github/workflows/ci.yml` configures quality checks with PostgreSQL and Redis services. | CI migrates the DB and runs Ruff/Pyright. It sets Python 3.12 despite `requires-python = ">=3.14"`. |

No separate LLM framework or evaluation package is configured in the dependency
manifest.

## 3. Repository structure

| Path | Responsibility |
|---|---|
| `app/main.py` | Creates the FastAPI application, mounts the API router, and defines `/health` and `/ready`. |
| `app/api/v1/` | Authentication and support endpoint routers; paths currently mount as `/auth/...` and `/support/...`. |
| `app/schemas/` | Pydantic request and response types, intent labels, and escalation values. |
| `app/services/` | Orchestration, classifier, escalation, LLM client, retrieval, embeddings, response generation, auth, and rate-limit logic. |
| `app/models/`, `app/db/` | SQLAlchemy models, base metadata, engine, and session dependency. |
| `alembic/` | Migration environment and revision history. |
| `scripts/dataset/` | Source exploration and tweet-thread processing. |
| `scripts/db_load/` | Processed conversation loader, historical-case generation, and vector backfill. |
| `scripts/evaluation/create_golden_set.py` | Candidate-sampling/export script. It writes a new candidate file with blank annotation fields; it is not a metrics/evaluation runner. |
| `docs/` | Dataset notes, intent taxonomy, sampling/methodology/annotation guidance, and validation report. |
| `data/` | Contains local raw/processed artifacts (raw and processed paths are ignored) and checked-in sample/evaluation CSVs. |
| `bruno/SupportPilot/` | Bruno collection metadata and auth requests. There is no support-message request in the collection. |
| `tests/` | Health, unit, and integration tests. Some tests call PostgreSQL, Redis, or load the embedding model. |
| `dev.sh`, `docker-compose.yml` | Development shell shortcuts and local infrastructure definition. |

## 4. Application lifecycle and request flow

### Startup

`app/main.py` loads settings, configures logging, creates `FastAPI(title, version)`,
and mounts `app.api.v1.router.router`. It does not run migrations or verify
dependencies at startup. `/health` returns `{"status":"ok"}` and `/ready`
returns `{"status":"ready"}` without dependency checks.

### `POST /support/messages`

1. `app/api/v1/customer_request.py` validates a `CustomerSupportRequest`.
   `customer_message` must be non-empty after trimming and at most 5,000
   characters; extra request fields are rejected.
2. The route obtains a SQLAlchemy session through `get_db`.
3. `CustomerSupportOrchestrator` constructs an `IntentClassifier` and
   `CustomerResponseGenerator`. Both construct an `LLMService`; its constructor
   requires the OpenRouter API key and model setting.
4. `IntentClassifier.classify()` sends the allowed labels and incoming message
   to OpenRouter, then validates the response as `IntentClassification`.
5. `EscalationService.decide()` escalates unknown/insufficient context, Apple ID
   security, or low-confidence classifications. Other supported intents with
   medium/high confidence are auto-handled.
6. Only for an auto-handle decision, the response generator embeds the incoming
   message, fetches the nearest historical cases, and asks OpenRouter for a
   draft. For escalation, `draft_response` is `null`.
7. FastAPI serializes the `OrchestratorResponse`; the DB dependency closes its
   session in `finally`.

The route has no JWT authorization dependency and no Redis rate-limit
dependency. Validation errors use FastAPI's 422 response. Missing provider
configuration and downstream failures can fail the request; they are not
converted to a successful fallback.

### Authentication requests

`/auth/register` and `/auth/login` have a router-level Redis rate-limit
dependency. Registration validates email/password, hashes the password, and
returns a user response; duplicate email is mapped to 409. Login validates
credentials and returns a bearer JWT or 401. `get_current_user()` and
`decode_access_token()` are implemented in helper modules but are not applied
to any currently registered route.

## 5. Data pipeline

### Source and conversation processing

The source is Kaggle's `thoughtvector/customer-support-on-twitter`, a dataset
of approximately three million tweets. The repository's `docs/dataset.md`
records 2,811,774 source rows and 106,860 support-side `AppleSupport` tweets.
Those figures describe the source/exploration notes, not database records.
The raw file is `data/raw/twcs.csv`; it is not committed.

`scripts/dataset/processing/conversation_processing.py` reads the full CSV
with Polars. `ConversationBuilder` in
`scripts/dataset/processing/construct_conversation.py` follows
`in_response_to_tweet_id` links to roots, then follows a parent-to-child lookup
to form threads. It keeps threads containing an AppleSupport tweet, at least
one inbound customer message, a support message, and non-empty text. The
flattened Parquet rows represent **tweets/messages**, not whole conversations;
each has a `conversation_id` (the root tweet ID) and `turn_index`.

The child lookup is a single-child mapping. If a parent has multiple replies,
later rows overwrite earlier children in the mapping; branching threads are
therefore not fully represented by the current reconstruction algorithm.

### Loading and historical cases

The processed file is `data/processed/apple_support_conversations.parquet`.
On the inspected local workspace it has 5 rows across 2 conversation IDs; this
is an ignored development artifact, not a checked-in corpus-size guarantee.

From the repository root, these are the script entry points:

```bash
uv run python -m scripts.dataset.processing.conversation_processing
uv run python -m scripts.db_load.load_to_db --limit 100
uv run python -m scripts.db_load.historical_case
uv run python -m scripts.db_load.backfill_embeddings
```

The processing command reads the complete raw CSV and has no sample-size
argument, so it can be memory intensive. The DB loader reads the processed
Parquet and supports `--dataset PATH` and `--limit N` (default 1,000 message
rows). Run it only after migrations and data processing.

The database has separate `Conversation`, `Message`, and `HistoricalCase`
models. The loader inserts unique conversations by source ID and unique
messages by tweet ID. `historical_case.py` groups stored messages, uses the
first inbound message as `customer_message`, joins outbound messages into
`support_response`, and sets `resolution` to `"Outcome not recorded"`. This
creates an approximate historical case, not an independently verified
resolution label.

The checked-in `data/evaluation/golden_set_annotations.csv` contains 200 rows
and stores message identifiers/text, sampling metadata, intent/escalation
labels, annotation confidence, and review status. It is distinct from raw
source tweets and generated Parquet.

## 6. Embeddings and retrieval

`EmbeddingServices` loads `sentence-transformers/all-MiniLM-L6-v2` once per
process and verifies the output is a finite 384-value vector.
`HistoricalCase.embedding` maps to `Vector(384)` from pgvector. The backfill
script selects cases with no embedding and saves generated vectors.

`RetrievalServices.retrieve_similar_cases()` embeds the current message,
filters out cases without embeddings, orders by PostgreSQL cosine distance,
and returns up to five records by default. `CustomerResponseGenerator`
formats their customer message, support response, and resolution as context.
If there are no matching rows, the prompt explicitly says no similar cases
were found; it does not retrieve raw `Message` records.

Retrieval therefore depends on the historical-case creation and embedding
steps being completed. An empty historical-case table means no evidence is
available to ground a draft. No retrieval-quality metric or relevance threshold
is implemented.

## 7. API usage

The actual registered paths are below. The `v1` directory name is not reflected
in the route prefix. Generated schemas are also available at `/docs` and
`/openapi.json`.

| Method and path | Request | Success | Auth / notable errors |
|---|---|---|---|
| `GET /health` | None | `200 {"status":"ok"}` | No authentication. |
| `GET /ready` | None | `200 {"status":"ready"}` | No authentication; static response only. |
| `POST /auth/register` | `UserRegistration`: `email`, `password` | `201 {"id": 1, "email": "person@example.com"}` | No bearer auth; Redis rate-limited. `400` client IP unavailable, `409` duplicate email, `422` invalid request, `429` rate limit. |
| `POST /auth/login` | `UserLogin`: `email`, `password` | `200 {"access_token":"<JWT>", "token_type":"bearer"}` | No bearer auth; Redis rate-limited. `400` client IP unavailable, `401` invalid credentials, `422` invalid request, `429` rate limit. |
| `POST /support/messages` | `CustomerSupportRequest`: `customer_message` | `200 OrchestratorResponse` | No authentication dependency currently applied. `422` invalid request; missing LLM settings or downstream failures can become `500`. Requires database and configured LLM; auto-handling also requires an available embedding model. |

Support request example:

```bash
curl -sS http://127.0.0.1:8000/support/messages \
  -H 'Content-Type: application/json' \
  -d '{"customer_message":"My iPhone will not charge."}'
```

The success object has this schema (values below are illustrative, not a
measured model result):

```json
{
  "classification": {
    "intent": "battery_and_charging",
    "confidence": "medium",
    "rationale": "The customer reports a charging problem."
  },
  "escalation": {
    "action": "auto_handle",
    "risk_level": "low",
    "reason": "The issue has a supported intent and the classifier reports medium or high confidence."
  },
  "draft_response": "<generated reply>"
}
```

An escalated response has the same classification/escalation objects and
`"draft_response": null`. The valid intents and enum values are defined in
`app/schemas/intent.py` and `app/schemas/escalation.py`.

### Bruno

Open `bruno/SupportPilot/` as a Bruno collection. The existing requests are
registration and login. Register before login if using a new account. The login
request currently specifies `body: none` even though the API requires JSON
`email` and `password`; add that body locally before relying on it. The
collection does not include a support-message request or environment
configuration. Do not store real credentials in committed Bruno files.

## 8. Database and migrations

`app/db/session.py` builds the engine from `DATABASE_URL` with
`pool_pre_ping=True`. `get_db()` yields one session per request and closes it
afterward. Alembic's `env.py` imports model metadata and the same engine.
Models include:

- `User`: unique email, password hash, and creation time.
- `Conversation`: unique source ID and a one-to-many message relationship.
- `Message`: conversation foreign key, unique tweet ID, turn index, inbound
  flag, timestamp, and text.
- `HistoricalCase`: conversation foreign key, customer message, support
  response, resolution text, and nullable 384-dimensional vector.

The database revision was inspected locally at
`307d2f46f1dd` (`head`). Useful commands:

```bash
uv run alembic current
uv run alembic heads
uv run alembic upgrade head
```

For a model change, update the SQLAlchemy model, create/review a migration,
apply it to a development database, then run relevant tests. Autogeneration
can be used with `uv run alembic revision --autogenerate -m "describe change"`,
but always inspect the generated migration before applying it. Avoid deleting
or recreating the Compose volume to solve a migration mismatch.

## 9. Authentication, security, and rate limiting

Passwords are hashed and verified through `pwdlib.PasswordHash.recommended()`.
`create_access_token()` signs an HS256 JWT with `sub`, `type`, `iat`, and
`exp`; token lifetime is configured by `ACCESS_TOKEN_EXPIRE_MINUTES` (default
60 minutes). `get_current_user()` decodes the bearer token and loads the user.
That dependency is not attached to `/support/messages` or another current
route, so authentication is not currently enforced for support requests.

Redis-backed rate limiting uses `RATE_LIMIT_REQUESTS` (default 10) per
`RATE_LIMIT_WINDOW_SECONDS` (default 60) and IP identifier. It is attached at
the auth router, not to the support route. The current counter increments and
sets expiry when the count first reaches one.

Security/configuration considerations from the code (not a security audit):

- Replace the example/default JWT signing key with a strong private value.
- The support endpoint is unauthenticated despite the available JWT helper.
- `.env.example` omits `POSTGRES_PASSWORD`, `OPENROUTER_API_KEY`, and `MODEL`.
- The LLM client sends requests to the configured OpenRouter endpoint.
- Historical conversation text is passed to the model. The reply prompt calls
  retrieved text untrusted reference material, but the application has no
  separate redaction or privacy filtering layer.
- The rate limiter relies on Redis availability and trusts the request's
  client IP as supplied by the ASGI server/proxy setup.

## 10. Testing and CI

### Local tests

The following focused command passed in the inspected workspace:

```bash
uv run pytest -q \
  tests/test_health.py \
  tests/unit/services/test_support_orchestrator.py \
  tests/unit/services/test_escalation.py \
  tests/unit/services/test_retrieval.py \
  tests/unit/services/test_embeddings.py \
  tests/unit/core/test_security.py
```

PostgreSQL and Redis integration tests also passed when the repository root was
explicitly included on `PYTHONPATH`:

```bash
PYTHONPATH=. uv run pytest -q \
  tests/integrations/test_database.py \
  tests/integrations/test_rate_limiter.py
```

The `test_sentence_transformer` integration test may need model-hub access on
first run. `pyproject.toml`'s `gpythonpath` pytest option is not recognized by
pytest, and invoking tests directly from `tests/integrations/` without
`PYTHONPATH=.` resulted in `ModuleNotFoundError: app` in this workspace.

### CI-equivalent quality checks

The workflow runs the following commands:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run alembic upgrade head
```

These checks passed locally for Ruff lint, Ruff format, and Pyright; the current
database revision was already at Alembic head. CI does **not** invoke pytest,
despite defining PostgreSQL and Redis service containers. It also installs
Python 3.12 while the project metadata requires Python 3.14 or newer, so a
clean CI dependency sync is not currently aligned with the manifest.

## 11. Evaluation and experimentation

### Existing artifacts

- `data/evaluation/golden_set_annotations.csv`: 200 rows, with identifiers,
  message text, sampling metadata, labels, annotation confidence, and review
  status.
- `docs/golden_set_sampling_plan.md`: intended 200-message target and
  sampling controls.
- `docs/golden_set_methodology.md`: describes AI-assisted drafts followed by
  one author's manual review, and acknowledges that the labels are
  provisional and not independently adjudicated.
- `docs/golden_set_annotation_guidelines.md`: intent and escalation rules.
- `docs/golden_set_validation_report.md`: structural counts and label
  distributions; explicitly says this does not establish semantic correctness.
- `docs/intent_taxonomy.md`: eight core intents plus unknown/insufficient
  context.

### Gaps and naming drift

There is no prediction/evaluation runner, baseline comparison, LLM-as-judge
rubric, judge-human agreement report, or example-backed failure analysis.
The evaluation CSV's 200 rows are not a model score. The sampling
documentation refers to `scripts/dataset/sample_golden_set.py`, which is not
present; the existing `scripts/evaluation/create_golden_set.py` writes a
candidate CSV under `data/golden/` with blank annotation fields. It is not the
checked-in annotated CSV at `data/evaluation/`.

Intent names also drift: the runtime enum uses
`unknown_or_insufficient_context`, while the dataset annotation/taxonomy docs
use `unknown_insufficient_context`. The candidate script includes the extra
`app_or_media_issue` keyword group, and the annotation docs mention a different
script path. Resolve this before using the CSV as an automated ground-truth
target.

To satisfy the original assignment, next work should reconcile the schema and
artifact paths, freeze a reviewed evaluation split, implement prediction
capture and trivial/simple baselines, report intent and escalation metrics,
define reply-quality criteria and assess judge-human agreement, and publish
five real failure examples with hypotheses. A report must include the exact
section title **“What is misleading about my headline number?”**. No
headline performance metric or failure example is claimed in this repository
guide.

## 12. Troubleshooting

| Symptom | Evidence-based check |
|---|---|
| Compose Postgres fails to initialize | Set `POSTGRES_PASSWORD`; it is referenced by `docker-compose.yml` but absent from `.env.example`. |
| API database connection fails | Compose maps host port `5433` to container port `5432` and creates `supportpilot`. Ensure `DATABASE_URL` uses the host mapping and database name. `.env.example` currently points at port `5432`/`supportpilot_test`. |
| Redis rate limit errors | Check `REDIS_URL` and `docker exec supportpilot-redis redis-cli ping`. Auth endpoints require Redis; health routes do not. |
| `/ready` returns ready but dependencies are unavailable | This route is static and does not perform readiness checks. Verify PostgreSQL/Redis separately. |
| LLM initialization fails | Set `OPENROUTER_API_KEY` and `MODEL` in the private environment. The implementation reads `MODEL` although the missing-setting message refers to `OPENROUTER_MODEL`. |
| First vector operation is slow or fails offline | The Sentence Transformers model may need to be downloaded and cached. |
| Alembic cannot connect | Check `DATABASE_URL`, port, DB credentials, and service state; inspect `uv run alembic current` before applying migrations. |
| Pytest cannot import `app` from an integration subdirectory | Run pytest from the repository root with `PYTHONPATH=.`. Also note pytest warns that `gpythonpath` is an unknown configuration option. |
| Login request in Bruno gets 422 | Its saved request has no body; send JSON with the schema's email and password fields. |

## 13. Development workflow

1. Create or update the relevant schema/service/route and keep request and
   response types in `app/schemas/`.
2. Add or update focused tests. Use mocks for deterministic unit behavior;
   integration tests should explicitly require configured PostgreSQL/Redis or
   the model cache.
3. If a model changed, generate and review an Alembic revision, then apply
   `uv run alembic upgrade head` against a development database.
4. Start infrastructure with `./dev.sh infra` and the server with
   `./dev.sh server`. The helper's usage text currently says `infra-up`, but
   its actual accepted argument is `infra`.
5. Verify health at `/health` and inspect routes/schemas at `/docs`. Use Bruno
   for auth after correcting its login request body; use the documented curl
   request for the support route once the LLM and historical-vector
   prerequisites are configured.
6. Run focused pytest checks, then CI-equivalent Ruff and Pyright commands.
   Remember the current CI Python-version mismatch and that CI omits pytest.
7. Review `git diff` and commit only intentional files with a descriptive
   message. Never commit `.env`, credentials, or source data.

The shell helper currently accepts `server`, `infra`, `db-shell`, and
`lint-fix`; `lint-fix` modifies files, while `db-shell` opens an interactive
`psql` session against the Compose container.
