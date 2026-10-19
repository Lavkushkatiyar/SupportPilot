::: {align="center"}
# SupportPilot

### An evidence-grounded AI customer-support agent

**Classify the issue. Retrieve relevant history. Draft a response.
Escalate when needed.**

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-Vector_Search-336791?style=flat-square)](https://github.com/pgvector/pgvector)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
:::

------------------------------------------------------------------------

## Technology stack at a glance

SupportPilot brings together a Python API, a retrieval-backed data layer, and an LLM-powered response workflow.

- **Python + FastAPI** — API application and request handling.
- **Pydantic** — request/response schemas and structured data validation.
- **SQLAlchemy + Alembic** — relational data access and database schema migrations.
- **PostgreSQL + pgvector** — persistence and vector similarity search over embedded support cases.
- **Sentence Transformers** — generation of text embeddings for semantic retrieval.
- **OpenRouter** — access to hosted language models for intent and response-generation tasks.
- **Redis** — support for rate limiting and shared short-lived state.
- **Docker Compose** — local service orchestration for development.
- **uv** — Python dependency and environment management.
- **Ruff + Pyright + pytest** — linting/formatting, static type checking, and automated tests.
- **Bruno** — API request collections for manual endpoint testing.

The stack separates responsibilities: the API validates and coordinates requests, PostgreSQL stores application and historical-case data, vector search finds semantically related cases, and the language model uses the resulting context to help prepare a response. The escalation layer provides a separate decision point instead of treating every incoming message as suitable for automatic handling.

---

## The problem: support answers need evidence, not just fluent text

A general-purpose LLM can produce a plausible answer to a customer-support question, but plausibility is not the same as a useful support response. Without relevant context, a model may give a generic answer, overlook how the issue has appeared in the past, or sound confident without enough evidence to justify its recommendation.

**SupportPilot explores a more grounded approach:** use historical customer-support interactions to understand the incoming message, retrieve relevant examples, and shape a response draft around that context. It is not simply another chat interface placed in front of an LLM. It is a support workflow that combines classification, historical retrieval, response generation, and an explicit escalation decision.

### Why use a real support dataset?

The project starts from the [Customer Support on Twitter dataset on Kaggle](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter), which contains approximately **3 million tweets** across multiple brands and support conversations. The data is real-world and noisy: messages can be short, informal, incomplete, and spread across multiple turns. That makes it useful for exploring the kinds of ambiguity a support system must handle, rather than designing only around clean, synthetic questions.

For this prototype, **Apple Support is the selected brand**. The full dataset is the source corpus; the application uses a processed Apple Support subset for its current historical-case workflow. The approximately three million figure describes the source dataset, not the number of Apple Support records queried for every request.

### How historical conversations guide the response

The processed data preserves conversation relationships and turn order. A customer message and the support reply that followed it can therefore be interpreted as part of a historical interaction, rather than as unrelated snippets of text. SupportPilot uses this history in three ways:

1. **Categorize the request.** An intent classifier maps the incoming message to a defined support category so downstream logic can handle requests consistently.
2. **Find relevant precedents.** Semantic retrieval searches historical Apple Support cases for messages similar to the current issue.
3. **Plan the next step.** The retrieved examples provide context for drafting a response, while the escalation policy determines whether the request is eligible for an automatic draft or should be referred to a human.

Historical interactions are **guidance, not ground truth for current policy**. A past reply may be outdated, incomplete, or specific to a different situation. SupportPilot therefore treats retrieved cases as contextual evidence for a draft—not as proof that the same answer is correct today. The prototype does not send replies or perform actions on an Apple account.

---

## Overview

SupportPilot is an experimental AI support agent built around a
practical idea: **a customer-support model should have relevant evidence
before it drafts an answer**.

The current implementation uses historical Apple Support conversations
to classify incoming customer messages, find semantically similar cases,
draft a context-informed response, and decide whether the request should
be handled automatically or escalated to a human.

The system combines language-model reasoning with conventional backend
engineering: a versioned HTTP API, typed data contracts, relational
persistence, vector similarity search, deterministic escalation rules,
authentication utilities, rate limiting, and a repeatable local
development environment.

> **Important boundary:** SupportPilot produces a response draft; it
> does not send replies or take actions on an Apple account. Historical
> social-media conversations are examples of past interactions, not
> official Apple policy. This is an independent project and is not
> affiliated with or endorsed by Apple.

## The workflow

``` mermaid
flowchart TD
    A[Incoming customer message] --> B[FastAPI endpoint]
    B --> C[Support orchestrator]
    C --> D[LLM intent classification]
    D --> E[Deterministic escalation policy]
    E -->|Escalate| F[Return escalation decision and reason]
    E -->|Eligible for draft| G[Create message embedding]
    G --> H[PostgreSQL + pgvector similarity search]
    H --> I[Retrieve relevant historical cases]
    I --> J[Prompt construction with retrieved context]
    J --> K[LLM response generation]
    K --> L[Return draft, classification, evidence and routing decision]
```

The authentication path uses the relational database for user records
and Redis for rate limiting. Dataset processing and database-loading
scripts populate the historical-case store used by retrieval.

## Core capabilities

### 1. Intent classification

An LLM classifies an incoming message against a domain-specific Apple
Support intent taxonomy. The classification contract captures the
structured result used by the rest of the workflow, rather than leaving
downstream components to interpret free-form prose.

**Why it matters:** Support requests are not all the same. A structured
intent gives the application a consistent signal for routing,
escalation, response generation, and later analysis.

### 2. Semantic retrieval with embeddings

SupportPilot uses a Sentence Transformers embedding model to represent
text as numerical vectors. A query message is embedded and compared with
historical case embeddings stored in PostgreSQL through `pgvector`. The
current retrieval path selects up to five nearest cases.

**Why it matters:** Similar support issues can be expressed with
different words. Semantic retrieval can find related examples even when
the incoming message does not share exact keywords with the historical
message.

### 3. PostgreSQL and pgvector

PostgreSQL stores application data and historical cases. The `pgvector`
extension adds vector data types and similarity-search operations to the
same database, allowing the application to combine relational
persistence with embedding-based retrieval.

**Why it matters:** Keeping historical cases and their vectors in the
existing database avoids introducing a separate vector-database service
for this prototype. It also keeps the data lifecycle and deployment
topology simpler.

### 4. Retrieval-augmented response generation

The response generator receives the incoming request and retrieved
historical examples as context for the configured chat model. This is a
retrieval-augmented generation (RAG) pattern: retrieve relevant
information first, then use it to condition generation.

**Why it matters:** The model is not asked to draft a response in
isolation. Retrieved examples provide context that can make the draft
more relevant and consistent with previous support interactions. They
are still historical evidence---not a guarantee of correctness or an
authoritative source of policy.

### 5. Prompt engineering and structured outputs

Prompts define the task, provide the relevant context, and guide the
model toward the expected response format. Pydantic schemas provide
explicit contracts for structured application data.

**Why it matters:** Prompt design makes model behavior easier to reason
about, while typed contracts reduce ambiguity between model output and
application logic.

**Terminology note:** This project uses prompt engineering and iterative
prompt refinement. That is different from model fine-tuning, which
changes model weights through a training process. SupportPilot should
not be described as fine-tuned unless such a training process is
actually performed.

### 6. Deterministic escalation policy

Escalation is handled through explicit application rules, including
low-confidence or insufficient-context classifications and sensitive
account-security cases.

**Why it matters:** Not every request should proceed to automatic
drafting. Separating routing rules from generative model behavior makes
important decisions more inspectable and easier to test. The current
rules are a prototype policy, not a guarantee that every unsafe case
will be detected.

### 7. Workflow orchestration

The support orchestrator coordinates classification, escalation,
retrieval, and response generation. Individual components retain their
own responsibilities rather than embedding the entire workflow in an API
route.

**Why it matters:** This separation makes the request flow easier to
follow, test, and evolve. It also reduces the risk of duplicating
retrieval or business rules across multiple entry points.

### 8. API contracts and service boundaries

FastAPI exposes HTTP endpoints, while Pydantic schemas define request
and response shapes. SQLAlchemy models represent persisted entities,
keeping database structure distinct from API contracts.

**Why it matters:** Explicit boundaries help prevent persistence details
from leaking into the public API and make validation behavior easier to
document and test.

### 9. Authentication and rate limiting

The project includes user registration and login endpoints, JWT-related
security utilities, and Redis-backed rate limiting for authentication
requests.

**Why it matters:** Authentication and request throttling are important
backend concerns even in an AI-focused project. Redis provides a shared,
fast store for rate-limit state instead of relying only on process-local
memory.

The support endpoint should have appropriate authentication and
authorization applied before the service is exposed to real users or
customer data.

### 10. Dataset processing and ingestion

The data pipeline reconstructs conversation turns from the Customer
Support on Twitter dataset, writes processed data to Parquet, and
provides scripts for loading historical cases and backfilling
embeddings.

**Why it matters:** Retrieval quality depends on the data representation
and ingestion path---not only on the language model. Keeping processing
and database-loading scripts separate from request-time application code
makes these workflows easier to run and maintain.

## Technology choices

  -----------------------------------------------------------------------
  Technology              Role in SupportPilot    Why it fits
  ----------------------- ----------------------- -----------------------
  **Python**              Application and data    Strong ecosystem for
                          workflows               APIs, data processing,
                                                  embeddings, and LLM
                                                  integration

  **FastAPI**             HTTP API                Typed request handling,
                                                  validation, and
                                                  generated OpenAPI
                                                  documentation

  **Pydantic**            Data contracts          Explicit validation and
                                                  structured interfaces
                                                  between components

  **SQLAlchemy**          ORM and database access Pythonic persistence
                                                  models and database
                                                  interaction

  **Alembic**             Schema migrations       Versioned, repeatable
                                                  database schema changes

  **PostgreSQL**          Relational persistence  Stores application
                                                  records and historical
                                                  support cases

  **pgvector**            Vector similarity       Adds embedding storage
                          search                  and nearest-neighbor
                                                  search to PostgreSQL

  **Sentence              Text embeddings         Converts text into
  Transformers**                                  vectors for semantic
                                                  similarity

  **OpenRouter**          Chat-model access       Provides a configurable
                                                  API endpoint for
                                                  supported chat models

  **Redis**               Rate-limit state        Fast shared state for
                                                  request throttling

  **Docker Compose**      Local infrastructure    Reproducible local
                                                  services without
                                                  manually installing
                                                  each dependency

  **uv**                  Python environment and  Lockfile-based,
                          dependency management   repeatable project
                                                  setup

  **Ruff and Pyright**    Static quality checks   Catch style, common
                                                  code-quality, and
                                                  typing issues early

  **pytest**              Automated tests         Verifies individual
                                                  components and
                                                  important integrations

  **Bruno**               Manual API verification Keeps reusable HTTP
                                                  requests for exercising
                                                  endpoints
  -----------------------------------------------------------------------

## Architecture and repository organization

The application is organized around API handling, configuration and
infrastructure, persistence models, typed schemas, and service-level
workflow components.

``` text
app/
├── api/          # HTTP routes, dependencies and request-level controls
├── core/         # Configuration, logging, security and infrastructure clients
├── db/           # Database setup and session management
├── models/       # SQLAlchemy persistence models
├── schemas/      # Pydantic contracts
└── services/     # Authentication, AI capabilities, retrieval and support pipeline

alembic/          # Versioned database migrations
scripts/
├── dataset/      # Dataset analysis and conversation processing
├── db_load/      # Historical-case loading and embedding backfills
└── evaluation/   # Evaluation utilities
tests/
├── unit/
└── integrations/

docs/             # Dataset notes, technical guide and design documentation
bruno/            # Manual API requests
```

## Data source

SupportPilot uses the [Customer Support on Twitter
dataset](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter),
selecting Apple Support conversations for the current prototype.

The processing workflow reconstructs conversation turns from tweet
relationships and prepares records for historical-case retrieval. Raw
source data is kept local rather than committed to the repository.
Review the source dataset's terms before redistributing source-derived
data.

## Run locally

### Prerequisites

-   Python version specified by `pyproject.toml`
-   [uv](https://docs.astral.sh/uv/)
-   Docker with the Compose plugin
-   A local `.env` file
-   An OpenRouter API key and configured chat model for the LLM-backed
    support flow

### 1. Configure environment variables

On a fresh checkout:

``` bash
cp .env.example .env
```

Set the values required by the application, including:

-   `DATABASE_URL`
-   `POSTGRES_PASSWORD`
-   `REDIS_URL`
-   `JWT_SECRET_KEY`
-   `OPENROUTER_API_KEY`
-   `MODEL`

Use the variable names expected by the current configuration module.
Ensure the database URL matches the PostgreSQL service configured in
`docker-compose.yml`. Keep `.env` out of version control and never put
real credentials in `.env.example`.

### 2. Install dependencies and start infrastructure

``` bash
uv sync --locked
./dev.sh infra
uv run alembic upgrade head
```

### 3. Start the API

``` bash
./dev.sh server
```

### 4. Check the local API

``` bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready
```

Interactive API documentation is available at
`http://127.0.0.1:8000/docs` while the application is running.

The full support-message flow additionally requires a configured chat
provider and historical cases with embeddings in the database. Health
endpoints currently return status responses; do not treat them as proof
that every downstream dependency is available.

For exact environment requirements, endpoint schemas, test commands, and
operational details, see
[`docs/TECHNICAL_GUIDE.md`](docs/TECHNICAL_GUIDE.md).

## API overview

  -----------------------------------------------------------------------
  Method                  Path                    Purpose
  ----------------------- ----------------------- -----------------------
  `GET`                   `/health`               Liveness response

  `GET`                   `/ready`                Readiness-style status
                                                  response

  `POST`                  `/auth/register`        Register a user

  `POST`                  `/auth/login`           Authenticate and issue
                                                  a JWT

  `POST`                  `/support/messages`     Classify, route, and
                                                  optionally draft a
                                                  response
  -----------------------------------------------------------------------

The routers are organized under `app/api/v1/`; the current router
configuration does not necessarily add a `/v1` URL prefix. Check the
generated OpenAPI documentation for the exact request and response
schemas.

## Engineering principles

SupportPilot was built to explore an AI workflow while retaining the
practices expected of a maintainable backend:

-   **Separate responsibilities:** HTTP handling, schemas, persistence,
    model calls, retrieval, and workflow decisions have distinct roles.
-   **Make decisions inspectable:** return structured classification and
    escalation information rather than only free-form text.
-   **Use retrieval as evidence, not authority:** historical examples
    inform drafts but do not establish current technical truth or
    official policy.
-   **Prefer deterministic rules for explicit policy decisions:** use
    application logic where a decision should be predictable and
    testable.
-   **Keep infrastructure proportionate:** use PostgreSQL with pgvector
    rather than introducing a separate vector service for the current
    scope.
-   **Make setup repeatable:** use dependency locking, migrations,
    environment configuration, and Docker Compose.
-   **Test components and integrations:** use automated tests and manual
    API requests to check important behavior.

## Current scope and limitations

SupportPilot is a working prototype, not a production-ready
customer-support platform.

-   Generated replies are drafts and are not sent automatically.
-   Historical social-media examples can be outdated, incomplete, or
    unsuitable for a new case.
-   Model output and retrieval relevance can fail; a real deployment
    needs robust timeout handling, validation, monitoring, and fallback
    behavior.
-   The support route needs appropriate authentication and authorization
    before being exposed to real customer data.
-   Health/readiness responses do not currently verify all external
    dependencies.
-   A production pilot would need stronger operational controls, privacy
    review, tenant isolation if serving multiple companies, and
    evaluation of the full workflow.

## Documentation

-   [`docs/TECHNICAL_GUIDE.md`](docs/TECHNICAL_GUIDE.md) --- request
    flow, data pipeline, configuration, database setup, testing, and
    implementation details.
-   [`docs/dataset.md`](docs/dataset.md) --- dataset source and
    processing notes.
-   [`docs/intent_taxonomy.md`](docs/intent_taxonomy.md) --- intent
    labels and their definitions.

## Attribution

The source conversations originate from the [Customer Support on Twitter
dataset](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter).
Application code, processing outputs, embeddings, and response drafts
are project work. Follow the dataset's license and terms when using or
redistributing derived data.

SupportPilot is an independent project and is not affiliated with or
endorsed by Apple.
