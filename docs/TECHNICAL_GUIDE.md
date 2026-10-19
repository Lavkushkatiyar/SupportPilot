**# SupportPilot Technical Guide**



This guide describes the repository as it is implemented today. It separates

working code and verified local checks from assignment requirements that still

need evidence. The project overview and quick demo are in the [README]\(../README.md).



**## 1. Project overview**



SupportPilot is an experimental support-agent backend for Apple Support-style

messages. The current documented request path classifies a message using an

OpenRouter chat completion, applies deterministic escalation rules, and, when

the rules allow auto-handling, retrieves similar cases from PostgreSQL/pgvector

and asks the configured chat model to draft a reply. Ollama with the local

`qwen3:8b` model is the intended fallback provider, but automatic provider

failover must not be considered active until the Ollama adapter and fallback

routing are integrated and tested.



Current implementation status:



\| Capability | Status |

\|---|---|

\| Versioned Python modules and API | Router code is organized under \`app/api/v1\`, but the router is mounted without an \`/api/v1\` URL prefix. |

\| Intent classification | Implemented through an external chat-completion call and Pydantic validation. |

\| Escalation | Implemented as deterministic rules for insufficient context, Apple ID/account security, and low confidence. |

\| Retrieval and draft generation | Implemented; requires historical cases with 384-dimensional vectors, the sentence-transformer model, database connectivity, and OpenRouter configuration. |

\| Authentication and rate limiting | The latest project update states that API routes are rate-limited and protected operations require authentication. Company/tenant-aware authorization is planned; verify the current dependency wiring and route exceptions against the implementation before release. |

\| Golden set | A checked-in 200-row CSV and supporting methodology/validation documents exist; the set is provisional. |

\| Evaluation results | The project reports 85%+ intent-classification accuracy. The checked-in guide artifacts do not establish the evaluation run, sample size, per-class metrics, or reproducible command; reply-quality evaluation and failure analysis remain separate concerns. |



The service drafts text only. It does not perform account actions or claim to

represent official Apple policies.



**## 2. Technology stack**



\| Technology | Use in this repository | Developer interaction / considerations |

\|---|---|---|

\| Python and \`uv\` | Application, scripts, and dependency management; package metadata is in \`pyproject.toml\`, with \`uv.lock\` for locked resolution. The project requires Python \`>=3.14\`. | Install/sync with \`uv sync --locked\`; invoke tools with \`uv run\`. CI currently installs Python 3.12, which conflicts with the declared minimum and needs reconciliation. |

\| FastAPI / Pydantic | API routing, request validation, response schemas, and generated OpenAPI docs. | Run with \`./dev.sh server\`; inspect \`/docs\` and \`/openapi.json\`. Module folder \`v1\` does not currently make the public path versioned. |

\| SQLAlchemy | ORM models, sessions, and database access. | Configure \`DATABASE_URL\`; sessions are created by \`SessionLocal\` and closed in the request dependency. |

\| PostgreSQL and pgvector | Persistent users, conversations, messages, historical cases, and vector distance search. | Compose uses \`pgvector/pgvector:pg16\`, container port \`5432\`, host port \`5433\`, database \`supportpilot\`. |

\| Alembic | Schema migration history and execution. | Use \`uv run alembic current\`, \`uv run alembic heads\`, and \`uv run alembic upgrade head\`. |

\| Redis | Counter-based rate limiting on the authentication router. | \`REDIS_URL\` defaults to \`redis\://localhost:6379\`; Compose exposes port \`6379\`. |

\| Sentence Transformers | Generates 384-dimensional query/case vectors with \`sentence-transformers/all-MiniLM-L6-v2\`. | First use may need the model available from the Hugging Face model hub and local cache. |

\| OpenRouter | Chat-completion endpoint used for intent classification and customer-facing draft text. | \`app/services/generate_text.py\` reads \`OPENROUTER_API_KEY\` and \`MODEL\`. The error message names \`OPENROUTER_MODEL\` for the latter, but the implementation reads \`MODEL\`. Requests have a 30-second timeout. |

\| Ollama + Qwen3:8b | Local LLM option intended as a fallback for hosted model calls. | Ollama must be running on a host reachable by the API process, and the application needs an Ollama-compatible provider adapter and explicit fallback routing. A direct Ollama request was tested, but Python service integration/failover must be re-tested before deployment. |

\| Polars | Reads the source CSV, processes conversations, and reads/writes Parquet. | Use the scripts under \`scripts/dataset/\` and \`scripts/db_load/\`. The full raw CSV is large; use the loader's \`--limit\` for a small DB load after processing. |

\| Docker Compose | Local PostgreSQL/pgvector and Redis services. | Start with \`./dev.sh infra\` or \`docker compose up -d postgres redis\`. Set \`POSTGRES_PASSWORD\` in local configuration; it is not present in \`.env.example\`. |

\| pytest, Ruff, Pyright | Test runner, linter/formatter, and static type checker. | CI runs Ruff and Pyright but currently does not run pytest. \`pyproject.toml\` contains an invalid/unknown pytest option \`gpythonpath\`, which pytest warns about. |

\| Bruno | API request collection under \`bruno/SupportPilot/\`. | The checked-in collection contains registration and login requests only. Login currently has no request body even though the API schema requires email and password. |

\| GitHub Actions | \`.github/workflows/ci.yml\` configures quality checks with PostgreSQL and Redis services. | CI migrates the DB and runs Ruff/Pyright. It sets Python 3.12 despite \`requires-python = ">=3.14"\`. |



No separate LLM framework or evaluation package is configured in the dependency

manifest.

**### Local LLM fallback: Ollama + Qwen3:8b**

The intended provider arrangement is OpenRouter as the primary hosted provider and
Ollama running `qwen3:8b` on our own machine/server as the fallback. Ollama serves
the model through its local HTTP API; the FastAPI process must be able to reach
that endpoint. If the API is deployed remotely while Ollama remains on a developer
laptop, the deployed service will not be able to reach `localhost` on that laptop.
For a remote deployment, run Ollama on the same host/network as the API or expose
it through a private, access-controlled network. Do not expose an unauthenticated
Ollama endpoint publicly.

**Current implementation boundary:** the inspected `LLMService` path initializes
OpenRouter from `OPENROUTER_API_KEY` and `MODEL`. Installing Ollama and pulling
`qwen3:8b` does not by itself enable fallback. The service needs a provider adapter
that sends compatible chat requests to Ollama, plus explicit routing that selects
Ollama when the primary provider fails. The direct Ollama model request was tested,
but the Python service integration/failover still requires verification. Until
that test passes, describe Ollama as the planned local fallback—not as automatic
failover already available in production.

**Verification checklist**

1. Confirm the model is installed with `ollama list` and responds to `ollama run qwen3:8b`.
2. Confirm the FastAPI runtime can reach the Ollama HTTP endpoint; `localhost` means
   the current runtime/container, not another computer.
3. Test both intent-classification and response-drafting prompts through the actual
   Python provider adapter, including schema/JSON validation.
4. Simulate an OpenRouter timeout or provider error and verify that fallback is
   attempted only for appropriate transient failures.
5. Verify that invalid model output still fails safely and that deterministic
   escalation rules, retrieval context, authentication, and rate limiting remain
   unchanged.
6. Log which provider handled a request, without logging API keys or sensitive
   customer content.



**## 3. Repository structure**



\| Path | Responsibility |

\|---|---|

\| \`app/main.py\` | Creates the FastAPI application, mounts the API router, and defines \`/health\` and \`/ready\`. |

\| \`app/api/v1/\` | Authentication and support endpoint routers; paths currently mount as \`/auth/...\` and \`/support/...\`. |

\| \`app/schemas/\` | Pydantic request and response types, intent labels, and escalation values. |

\| \`app/services/\` | Orchestration, classifier, escalation, LLM client, retrieval, embeddings, response generation, auth, and rate-limit logic. |

\| \`app/models/\`, \`app/db/\` | SQLAlchemy models, base metadata, engine, and session dependency. |

\| \`alembic/\` | Migration environment and revision history. |

\| \`scripts/dataset/\` | Source exploration and tweet-thread processing. |

\| \`scripts/db_load/\` | Processed conversation loader, historical-case generation, and vector backfill. |

\| \`scripts/evaluation/create_golden_set.py\` | Candidate-sampling/export script. It writes a new candidate file with blank annotation fields; it is not a metrics/evaluation runner. |

\| \`docs/\` | Dataset notes, intent taxonomy, sampling/methodology/annotation guidance, and validation report. |

\| \`data/\` | Contains local raw/processed artifacts (raw and processed paths are ignored) and checked-in sample/evaluation CSVs. |

\| \`bruno/SupportPilot/\` | Bruno collection metadata and auth requests. There is no support-message request in the collection. |

\| \`tests/\` | Health, unit, and integration tests. Some tests call PostgreSQL, Redis, or load the embedding model. |

\| \`dev.sh\`, \`docker-compose.yml\` | Development shell shortcuts and local infrastructure definition. |



**## 4. Application lifecycle and request flow**



**### Startup**



\`app/main.py\` loads settings, configures logging, creates \`FastAPI(title, version)\`,

and mounts \`app.api.v1.router.router\`. It does not run migrations or verify

dependencies at startup. \`/health\` returns \`{"status":"ok"}\` and \`/ready\`

returns \`{"status":"ready"}\` without dependency checks.



**### \`POST /support/messages\`**



1\. \`app/api/v1/customer_request.py\` validates a \`CustomerSupportRequest\`.

&#x20;  \`customer_message\` must be non-empty after trimming and at most 5,000

&#x20;  characters; extra request fields are rejected.

2\. The route obtains a SQLAlchemy session through \`get_db\`.

3\. \`CustomerSupportOrchestrator\` constructs an \`IntentClassifier\` and

&#x20;  \`CustomerResponseGenerator\`. Both construct an \`LLMService\`; its constructor

&#x20;  requires the OpenRouter API key and model setting.

4\. \`IntentClassifier.classify()\` sends the allowed labels and incoming message

&#x20;  to OpenRouter, then validates the response as \`IntentClassification\`.

5\. \`EscalationService.decide()\` escalates unknown/insufficient context, Apple ID

&#x20;  security, or low-confidence classifications. Other supported intents with

&#x20;  medium/high confidence are auto-handled.

6\. Only for an auto-handle decision, the response generator embeds the incoming

&#x20;  message, fetches the nearest historical cases, and asks OpenRouter for a

&#x20;  draft. For escalation, \`draft_response\` is \`null\`.

7\. FastAPI serializes the \`OrchestratorResponse\`; the DB dependency closes its

&#x20;  session in \`finally\`.



The latest project update states that API routes are rate-limited and protected
operations require authentication. Rate limiting and authentication are separate
controls: rate limiting constrains request volume, while authentication
identifies the caller. Registration and login should remain reachable without an
existing bearer token; support operations should validate the bearer token before
processing customer data. Validation errors use FastAPI's 422 response. Missing
provider configuration and downstream failures can fail the request; they are
not converted to a successful fallback.



**### Authentication requests**



\`/auth/register\` and \`/auth/login\` are credential-acquisition endpoints and
should be rate-limited without requiring a pre-existing bearer token.
Registration validates email/password, hashes the password, and returns a user
response; duplicate email is mapped to 409. Login validates credentials and
returns a bearer JWT or 401. Verify that \`get_current_user()\` is attached to
each protected route and that no support route remains publicly accessible by
mistake.



**## 5. Data pipeline**



**### Source and conversation processing**



The source is Kaggle's \`thoughtvector/customer-support-on-twitter\`, a dataset

of approximately three million tweets. The repository's \`docs/dataset.md\`

records 2,811,774 source rows and 106,860 support-side \`AppleSupport\` tweets.

Those figures describe the source/exploration notes, not database records.

The raw file is \`data/raw/twcs.csv\`; it is not committed.



\`scripts/dataset/processing/conversation_processing.py\` reads the full CSV

with Polars. \`ConversationBuilder\` in

\`scripts/dataset/processing/construct_conversation.py\` follows

\`in_response_to_tweet_id\` links to roots, then follows a parent-to-child lookup

to form threads. It keeps threads containing an AppleSupport tweet, at least

one inbound customer message, a support message, and non-empty text. The

flattened Parquet rows represent **\*\*tweets/messages\*\***, not whole conversations;

each has a \`conversation_id\` (the root tweet ID) and \`turn_index\`.



The child lookup is a single-child mapping. If a parent has multiple replies,

later rows overwrite earlier children in the mapping; branching threads are

therefore not fully represented by the current reconstruction algorithm.



**### Loading and historical cases**



The processed file is \`data/processed/apple_support_conversations.parquet\`.

On the inspected local workspace it has 5 rows across 2 conversation IDs; this

is an ignored development artifact, not a checked-in corpus-size guarantee.



From the repository root, these are the script entry points:



\`\`\`bash

uv run python -m scripts.dataset.processing.conversation_processing

uv run python -m scripts.db_load.load_to_db --limit 100

uv run python -m scripts.db_load.historical_case

uv run python -m scripts.db_load.backfill_embeddings

\`\`\`



The processing command reads the complete raw CSV and has no sample-size

argument, so it can be memory intensive. The DB loader reads the processed

Parquet and supports \`--dataset PATH\` and \`--limit N\` (default 1,000 message

rows). Run it only after migrations and data processing.



The database has separate \`Conversation\`, \`Message\`, and \`HistoricalCase\`

models. The loader inserts unique conversations by source ID and unique

messages by tweet ID. \`historical_case.py\` groups stored messages, uses the

first inbound message as \`customer_message\`, joins outbound messages into

\`support_response\`, and sets \`resolution\` to \`"Outcome not recorded"\`. This

creates an approximate historical case, not an independently verified

resolution label.



The checked-in \`data/evaluation/golden_set_annotations.csv\` contains 200 rows

and stores message identifiers/text, sampling metadata, intent/escalation

labels, annotation confidence, and review status. It is distinct from raw

source tweets and generated Parquet.



**## 6. Embeddings and retrieval**



\`EmbeddingServices\` loads \`sentence-transformers/all-MiniLM-L6-v2\` once per

process and verifies the output is a finite 384-value vector.

\`HistoricalCase.embedding\` maps to \`Vector(384)\` from pgvector. The backfill

script selects cases with no embedding and saves generated vectors.



\`RetrievalServices.retrieve_similar_cases()\` embeds the current message,

filters out cases without embeddings, orders by PostgreSQL cosine distance,

and returns up to five records by default. \`CustomerResponseGenerator\`

formats their customer message, support response, and resolution as context.

If there are no matching rows, the prompt explicitly says no similar cases

were found; it does not retrieve raw \`Message\` records.



Retrieval therefore depends on the historical-case creation and embedding

steps being completed. An empty historical-case table means no evidence is

available to ground a draft. No retrieval-quality metric or relevance threshold

is implemented.



**## 7. API usage**



The paths below reflect the route names recorded in the inspected guide;
verify them against the current OpenAPI schema after recent authentication and
rate-limiting changes. The \`v1\` directory name was not reflected in the route
prefix in the inspected version. Generated schemas are available at \`/docs\`
and \`/openapi.json\`. The latest project update states that API routes are
rate-limited; support operations require authentication.



\| Method and path | Request | Success | Auth / notable errors |

\|---|---|---|---|

\| \`GET /health\` | None | \`200 {"status":"ok"}\` | Rate-limited per latest update; typically public for health checks. |

\| \`GET /ready\` | None | \`200 {"status":"ready"}\` | Rate-limited per latest update; static response in the inspected implementation. Confirm whether deployment policy keeps it public. |

\| \`POST /auth/register\` | \`UserRegistration\`: \`email\`, \`password\` | \`201 {"id": 1, "email": "person\@example.com"}\` | Public registration; rate-limited. \`400\` client IP unavailable, \`409\` duplicate email, \`422\` invalid request, \`429\` rate limit. |

\| \`POST /auth/login\` | \`UserLogin\`: \`email\`, \`password\` | \`200 {"access_token":"\<JWT>", "token_type":"bearer"}\` | Public login; rate-limited. \`400\` client IP unavailable, \`401\` invalid credentials, \`422\` invalid request, \`429\` rate limit. |

\| \`POST /support/messages\` | \`CustomerSupportRequest\`: \`customer_message\` | \`200 OrchestratorResponse\` | Requires authentication and is rate-limited per latest project update. \`422\` invalid request; missing LLM settings or downstream failures can become \`500\`. Requires database and configured LLM; auto-handling also requires an available embedding model. Company-level data authorization is planned. |



Support request example:



\`\`\`bash

curl -sS http\://127.0.0.1:8000/support/messages \\

&#x20; -H 'Content-Type: application/json' \\

&#x20; -d '{"customer_message":"My iPhone will not charge."}'

\`\`\`



The success object has this schema (values below are illustrative, not a

measured model result):



\`\`\`json

{

&#x20; "classification": {

&#x20;   "intent": "battery_and_charging",

&#x20;   "confidence": "medium",

&#x20;   "rationale": "The customer reports a charging problem."

&#x20; },

&#x20; "escalation": {

&#x20;   "action": "auto_handle",

&#x20;   "risk_level": "low",

&#x20;   "reason": "The issue has a supported intent and the classifier reports medium or high confidence."

&#x20; },

&#x20; "draft_response": "\<generated reply>"

}

\`\`\`



An escalated response has the same classification/escalation objects and

\`"draft_response": null\`. The valid intents and enum values are defined in

\`app/schemas/intent.py\` and \`app/schemas/escalation.py\`.



**### Bruno**



Open \`bruno/SupportPilot/\` as a Bruno collection. The existing requests are

registration and login. Register before login if using a new account. The login

request currently specifies \`body: none\` even though the API requires JSON

\`email\` and \`password\`; add that body locally before relying on it. The

collection does not include a support-message request or environment

configuration. Do not store real credentials in committed Bruno files.



**## 8. Database and migrations**



\`app/db/session.py\` builds the engine from \`DATABASE_URL\` with

\`pool_pre_ping=True\`. \`get_db()\` yields one session per request and closes it

afterward. Alembic's \`env.py\` imports model metadata and the same engine.

Models include:



\- \`User\`: unique email, password hash, and creation time.

\- \`Conversation\`: unique source ID and a one-to-many message relationship.

\- \`Message\`: conversation foreign key, unique tweet ID, turn index, inbound

&#x20; flag, timestamp, and text.

\- \`HistoricalCase\`: conversation foreign key, customer message, support

&#x20; response, resolution text, and nullable 384-dimensional vector.



The database revision was inspected locally at

\`307d2f46f1dd\` (\`head\`). Useful commands:



\`\`\`bash

uv run alembic current

uv run alembic heads

uv run alembic upgrade head

\`\`\`



For a model change, update the SQLAlchemy model, create/review a migration,

apply it to a development database, then run relevant tests. Autogeneration

can be used with \`uv run alembic revision --autogenerate -m "describe change"\`,

but always inspect the generated migration before applying it. Avoid deleting

or recreating the Compose volume to solve a migration mismatch.



**## 9. Authentication, security, and rate limiting**



Passwords are hashed and verified through \`pwdlib.PasswordHash.recommended()\`.

\`create_access_token()\` signs an HS256 JWT with \`sub\`, \`type\`, \`iat\`, and

\`exp\`; token lifetime is configured by \`ACCESS_TOKEN_EXPIRE_MINUTES\` (default

60 minutes). \`get_current_user()\` decodes the bearer token and loads the user.

The latest project update says protected API operations require
authentication and all API routes are rate-limited. Because this differs from
the previously inspected implementation, verify the actual route dependencies
and middleware before treating this guide as a code-level audit.

Redis-backed rate limiting previously used \`RATE_LIMIT_REQUESTS\` (default 10)
per \`RATE_LIMIT_WINDOW_SECONDS\` (default 60) and an IP identifier. Confirm
whether the current implementation applies the limiter globally or attaches it
separately to each router, and verify how client IPs are derived behind a
reverse proxy.



Security/configuration considerations from the code (not a security audit):



\- Replace the example/default JWT signing key with a strong private value.

\- Verify that every protected endpoint has an authentication dependency; public registration/login and any intentionally public health endpoints should be explicit exceptions.

\- \`.env.example\` omits \`POSTGRES_PASSWORD\`, \`OPENROUTER_API_KEY\`, and \`MODEL\`.

\- The LLM client sends requests to the configured OpenRouter endpoint.

\- Historical conversation text is passed to the model. The reply prompt calls

&#x20; retrieved text untrusted reference material, but the application has no

&#x20; separate redaction or privacy filtering layer.

\- The rate limiter relies on Redis availability and trusts the request's

&#x20; client IP as supplied by the ASGI server/proxy setup.



**### Company-aware authorization: planned work**



The source corpus contains support conversations associated with multiple
companies, while the current application is focused on Apple Support. Before
opening the service to additional companies, introduce an explicit company or
tenant identity and associate each user with the company they are permitted to
serve. Authorization must scope historical-case retrieval and any persisted
customer/support data to that company; filtering only in the prompt is not an
access-control boundary. Define how users are assigned to a company, how
cross-company access is rejected, and how tenant scope is enforced in database
queries. Add tests proving that a user from one company cannot retrieve another
company's cases. Until these controls are implemented and tested, multi-company
support should be described as planned rather than complete.



**## 10. Testing and CI**



**### Local tests**



The following focused command passed in the inspected workspace:



\`\`\`bash

uv run pytest -q \\

&#x20; tests/test_health.py \\

&#x20; tests/unit/services/test_support_orchestrator.py \\

&#x20; tests/unit/services/test_escalation.py \\

&#x20; tests/unit/services/test_retrieval.py \\

&#x20; tests/unit/services/test_embeddings.py \\

&#x20; tests/unit/core/test_security.py

\`\`\`



PostgreSQL and Redis integration tests also passed when the repository root was

explicitly included on \`PYTHONPATH\`:



\`\`\`bash

PYTHONPATH=. uv run pytest -q \\

&#x20; tests/integrations/test_database.py \\

&#x20; tests/integrations/test_rate_limiter.py

\`\`\`



The \`test_sentence_transformer\` integration test may need model-hub access on

first run. \`pyproject.toml\`'s \`gpythonpath\` pytest option is not recognized by

pytest, and invoking tests directly from \`tests/integrations/\` without

\`PYTHONPATH=.\` resulted in \`ModuleNotFoundError: app\` in this workspace.



**### CI-equivalent quality checks**



The workflow runs the following commands:



\`\`\`bash

uv run ruff check .

uv run ruff format --check .

uv run pyright

uv run alembic upgrade head

\`\`\`



These checks passed locally for Ruff lint, Ruff format, and Pyright; the current

database revision was already at Alembic head. CI does **\*\*not\*\*** invoke pytest,

despite defining PostgreSQL and Redis service containers. It also installs

Python 3.12 while the project metadata requires Python 3.14 or newer, so a

clean CI dependency sync is not currently aligned with the manifest.



**## 11. Evaluation and experimentation**



**### Existing artifacts**



\- \`data/evaluation/golden_set_annotations.csv\`: 200 rows, with identifiers,

&#x20; message text, sampling metadata, labels, annotation confidence, and review

&#x20; status.

\- \`docs/golden_set_sampling_plan.md\`: intended 200-message target and

&#x20; sampling controls.

\- \`docs/golden_set_methodology.md\`: describes AI-assisted drafts followed by

&#x20; one author's manual review, and acknowledges that the labels are

&#x20; provisional and not independently adjudicated.

\- \`docs/golden_set_annotation_guidelines.md\`: intent and escalation rules.

\- \`docs/golden_set_validation_report.md\`: structural counts and label

&#x20; distributions; explicitly says this does not establish semantic correctness.

\- \`docs/intent_taxonomy.md\`: eight core intents plus unknown/insufficient

&#x20; context.



**### Gaps and naming drift**



The project reports **85%+ intent-classification accuracy**. Treat this as a
reported result until the evaluation command, dataset split, sample size, label
mapping, and metric output are documented and reproducible. The checked-in
evaluation CSV's 200 rows are not themselves a model score. Intent accuracy does
not measure generated-response quality, retrieval relevance, escalation
correctness, or end-to-end support resolution. The previously inspected
artifacts did not contain a complete prediction runner, baseline comparison,
LLM-as-judge rubric, judge-human agreement report, or example-backed failure
analysis; update this status if those artifacts have since been added. The sampling

documentation refers to \`scripts/dataset/sample_golden_set.py\`, which is not

present; the existing \`scripts/evaluation/create_golden_set.py\` writes a

candidate CSV under \`data/golden/\` with blank annotation fields. It is not the

checked-in annotated CSV at \`data/evaluation/\`.



Intent names also drift: the runtime enum uses

\`unknown_or_insufficient_context\`, while the dataset annotation/taxonomy docs

use \`unknown_insufficient_context\`. The candidate script includes the extra

\`app_or_media_issue\` keyword group, and the annotation docs mention a different

script path. Resolve this before using the CSV as an automated ground-truth

target.



To satisfy the original assignment, next work should reconcile the schema and

artifact paths, freeze a reviewed evaluation split, implement prediction

capture and trivial/simple baselines, report intent and escalation metrics,

define reply-quality criteria and assess judge-human agreement, and publish

five real failure examples with hypotheses. A report must include the exact

section title **\*\*“What is misleading about my headline number?”\*\***.
The reported headline metric is 85%+ intent-classification accuracy; its
reproducibility and evaluation methodology should be documented before it is
presented as a benchmark. Do not present it as end-to-end response accuracy.



**## 12. Troubleshooting**



\| Symptom | Evidence-based check |

\|---|---|

\| Compose Postgres fails to initialize | Set \`POSTGRES_PASSWORD\`; it is referenced by \`docker-compose.yml\` but absent from \`.env.example\`. |

\| API database connection fails | Compose maps host port \`5433\` to container port \`5432\` and creates \`supportpilot\`. Ensure \`DATABASE_URL\` uses the host mapping and database name. \`.env.example\` currently points at port \`5432\`/\`supportpilot_test\`. |

\| Redis rate limit errors | Check \`REDIS_URL\` and \`docker exec supportpilot-redis redis-cli ping\`. Auth endpoints require Redis; health routes do not. |

\| \`/ready\` returns ready but dependencies are unavailable | This route is static and does not perform readiness checks. Verify PostgreSQL/Redis separately. |

\| LLM initialization fails | Set \`OPENROUTER_API_KEY\` and \`MODEL\` in the private environment. The implementation reads \`MODEL\` although the missing-setting message refers to \`OPENROUTER_MODEL\`. |

\| Ollama fallback is unavailable | Confirm Ollama is running, `qwen3:8b` is installed, and the API process can reach the Ollama endpoint. Verify the provider adapter and fallback routing; installing the model alone does not activate failover. |

\| First vector operation is slow or fails offline | The Sentence Transformers model may need to be downloaded and cached. |

\| Alembic cannot connect | Check \`DATABASE_URL\`, port, DB credentials, and service state; inspect \`uv run alembic current\` before applying migrations. |

\| Pytest cannot import \`app\` from an integration subdirectory | Run pytest from the repository root with \`PYTHONPATH=.\`. Also note pytest warns that \`gpythonpath\` is an unknown configuration option. |

\| Login request in Bruno gets 422 | Its saved request has no body; send JSON with the schema's email and password fields. |



**## 13. Development workflow**



1\. Create or update the relevant schema/service/route and keep request and

&#x20;  response types in \`app/schemas/\`.

2\. Add or update focused tests. Use mocks for deterministic unit behavior;

&#x20;  integration tests should explicitly require configured PostgreSQL/Redis or

&#x20;  the model cache.

3\. If a model changed, generate and review an Alembic revision, then apply

&#x20;  \`uv run alembic upgrade head\` against a development database.

4\. Start infrastructure with \`./dev.sh infra\` and the server with

&#x20;  \`./dev.sh server\`. The helper's usage text currently says \`infra-up\`, but

&#x20;  its actual accepted argument is \`infra\`.

5\. Verify health at \`/health\` and inspect routes/schemas at \`/docs\`. Use Bruno

&#x20;  for auth after correcting its login request body; use the documented curl

&#x20;  request for the support route once the LLM and historical-vector

&#x20;  prerequisites are configured.

6\. Run focused pytest checks, then CI-equivalent Ruff and Pyright commands.

&#x20;  Remember the current CI Python-version mismatch and that CI omits pytest.

7\. Review \`git diff\` and commit only intentional files with a descriptive

&#x20;  message. Never commit \`.env\`, credentials, or source data.



The shell helper currently accepts \`server\`, \`infra\`, \`db-shell\`, and

\`lint-fix\`; \`lint-fix\` modifies files, while \`db-shell\` opens an interactive

\`psql\` session against the Compose container.
