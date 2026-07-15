# OpenAPI Contract Baseline

Base path: `/api/v1`. JSON only. All writes use `Idempotency-Key`; versioned writes also use `If-Match`.

| Domain | Operations |
|---|---|
| Projects | `POST /projects`, `POST /projects/demo`, `GET/PATCH/DELETE /projects/{project_id}` |
| Prompt sets | `POST /projects/{id}/prompt-sets:generate`, `GET/PATCH /prompt-sets/{id}`, `POST /prompt-sets/{id}:confirm` |
| Providers | `GET /provider-capabilities` |
| Runs | `POST /runs`, `GET /runs/{id}`, `POST /runs/{id}:cancel`, `POST /runs/{id}:retry-failed` |
| Diagnosis | `GET /runs/{id}/diagnosis` |
| Optimization | `POST /runs/{id}/optimization-drafts`, `GET/PATCH /optimization-drafts/{id}`, `POST /optimization-drafts/{id}:confirm` |
| Comparison | `POST /optimization-versions/{id}/comparisons`, `GET /comparisons/{id}` |
| Feedback | `POST /feedback` |
| Operations | `GET /operations/{operation_id}`, `GET /health`, `GET /ready` |

## Required Resource Fields

- Every resource: `id`, `created_at`, `updated_at`, `version` where mutable.
- Run: `state`, `mode`, `condition_fingerprint`, `question_count`, `repeat_count`, counts by state, `retryable_failure_count`.
- Metrics: value plus `state=value|na`, controlled `na_reason`, numerator, denominator, and rules version where applicable.
- Comparison: independent before/after metrics, `eligibility`, mismatch fields, absolute delta, and percentage delta only when valid.
- Feedback: controlled rating and reason codes; optional free text is stored separately and excluded from analytics.

## Error Codes

Minimum controlled codes: `validation_failed`, `version_conflict`, `provider_unavailable`, `provider_timeout`, `provider_rate_limited`, `provider_rejected`, `response_parse_failed`, `run_not_cancellable`, `insufficient_sample`, `condition_mismatch`, `stale_recommendation`, `not_found`, `operation_in_progress`, `internal_error`.

The executable `contracts/openapi.yaml` is created with the application scaffold after GATE-2.
