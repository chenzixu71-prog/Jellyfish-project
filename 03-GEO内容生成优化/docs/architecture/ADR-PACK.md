# GEO Insight Studio Architecture Decision Pack

Status: `accepted for TECH_PLANNING; implementation starts only after GATE-2`

## ADR-001 Repository And Runtime

- Modular monorepo with `frontend/`, `backend/`, `contracts/`, and `infra/`.
- Frontend: React, TypeScript, Vite, npm lockfile, Node Active LTS pinned in `.nvmrc` at initialization.
- Backend: Python, FastAPI, Pydantic v2, dependency versions pinned at initialization.
- Exact package versions are resolved and locked together during scaffold creation; no floating production dependencies.

## ADR-002 Backend And Jobs

- Modular FastAPI monolith: projects, prompts, providers, evaluations, diagnostics, optimizations, comparisons, feedback, events, persistence.
- Long evaluations use persistent database jobs and polling endpoints.
- MVP does not use Celery, Redis, microservices, or ephemeral FastAPI `BackgroundTasks` for durable work.
- Cancellation is cooperative and persisted; terminal jobs cannot return to a running state.

## ADR-003 API Contract

- OpenAPI is the contract source of truth; TypeScript clients and schemas are generated from it.
- All writes accept an `Idempotency-Key`; mutable resources include an integer `version` for optimistic concurrency.
- Errors use `{code, message, field_errors, retryable, request_id}`.
- IDs are opaque UUIDs; timestamps are UTC ISO-8601.

## ADR-004 Persistence

- SQLAlchemy 2 and Alembic.
- SQLite for local development; managed PostgreSQL for public pilot.
- Migrations must run against both databases in CI.
- Core tables: projects, content_versions, prompt_sets, prompts, run_conditions, evaluation_runs, attempts, answer_evidence, diagnoses, recommendations, optimization_versions, comparisons, feedback, analytics_events.

## ADR-005 Provider Boundary

- `LLMProvider` isolates Mock and Real implementations.
- First Real implementation is OpenAI-compatible, configured only on the server; model alias and parameters remain environment configuration.
- Per attempt: explicit timeout, bounded retry category, token/cost accounting, and redacted logs.
- No silent Real-to-Mock fallback.

## ADR-006 Evaluation And Comparison

- A logical run owns question-level attempts; Real uses 3 repeats, Mock uses 1.
- The comparison fingerprint includes mode, provider, model alias/version, model parameters, prompt template version, prompt-set version/order, repeat count, rules version, and Mock version.
- Formal comparison is eligible only when the fingerprint matches and every required sample is valid.
- Partial or mismatched comparisons return independent results and KPI `N/A`.

## ADR-007 Analytics And Privacy

- Analytics never stores article content, full prompts/answers, API keys, identity data, or raw free-text feedback.
- Event identity uses anonymous session and operation IDs. `project_id` and `run_mode` are optional until they exist.
- Project deletion removes project-linked data; retained aggregate events cannot be re-associated with a project or person.
- Suggestion impressions and actions are separate events so adoption-rate denominators are reproducible.

## ADR-008 Frontend Architecture

- Modules: app-shell, projects, prompt-sets, evaluations, diagnosis, optimization, comparisons, feedback, analytics, shared/api, shared/ui.
- React Router for routes; TanStack Query for server state; React Hook Form plus Zod for forms; MSW for contract mocks.
- CSS variables and CSS Modules implement Figma tokens; Lucide provides interface icons.
- Grid columns use `minmax(0, 1fr)`; flex content uses `min-width: 0`; inspector becomes a drawer at 1024 px.
- Vitest, Testing Library, and Playwright cover unit, component, and browser flows.

## ADR-009 Deployment And Operations

- Frontend is statically hosted; backend and PostgreSQL are independently hosted.
- Provider credentials exist only in backend secrets.
- Explicit CORS allowlist, structured redacted logs, request IDs, health/readiness endpoints, migration step, rollback command, backup policy, and 30-day pilot retention.
- Hosting vendor is selected in the release ADR after local and staging verification.

## Build Admission

BUILD requires explicit user approval of GATE-2, a validated OpenAPI draft, generated frontend types, an initial Alembic migration, executable smoke tests, and a populated requirement traceability matrix.
