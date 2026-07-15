# Pilot Event Dictionary v2

## Common Envelope

Required: `event_id`, anonymous `session_id`, `occurred_at`, `app_version`.

Conditional: `operation_id` for user or system operations; `project_id` only after project creation; `run_id` and `run_mode` only after a run exists.

Never record article content, full prompts or answers, API keys, names, email, phone, raw Provider responses, stack traces, or raw free-text feedback in analytics.

## Funnel Events

| Event | Trigger | Required properties |
|---|---|---|
| `project_created` | Demo or manual project persisted once | `source`, content-length bucket, competitor count |
| `prompts_generated` | Candidate batch becomes visible | count, intent count, generation mode |
| `prompt_set_confirmed` | A 3-20 question set is frozen | count, prompt-set version |
| `evaluation_completed` | Run enters success or partial success | run ID, mode, success/failure counts, repeats, duration bucket |
| `diagnosis_viewed` | Diagnosis first viewed for a run | run ID, diagnosis count, citation state, confidence state |
| `optimization_generated` | Actionable suggestions become visible | run ID, suggestion count, generation state |
| `suggestion_impression` | A suggestion is first visible and actionable | suggestion ID, rule dimension |
| `suggestion_actioned` | First adopt, edit-after-adopt, reject, undo, or stale action | suggestion ID, controlled action, rule dimension |
| `optimization_confirmed` | A changed optimization version is frozen | optimization version, changed-block count |
| `comparison_completed` | Eligible formal comparison is persisted | before/after run IDs, rules version, before score, after score, absolute delta, optional percentage delta |
| `feedback_submitted` | Feedback persists once | stage, useful rating, controlled reason code |

`comparison_completed` is not emitted for condition mismatch or partial samples. Those outcomes are recorded by `operation_finished` with a controlled reason.

## Reliability Event

`operation_finished` records one terminal outcome per idempotent operation: operation ID/type, outcome (`success`, `failed`, `cancelled`, `validation_rejected`), controlled error category, retry-of ID, and optional run ID. Raw errors and Provider payloads are prohibited.

## Metric Definitions

- Valid value session: an invited target user uses real content and Real mode, completes baseline plus diagnosis, and either confirms an optimization version or explicitly stops and submits a controlled reason. Demo, Mock, internal QA, and duplicate debugging sessions are excluded.
- Core completion rate: valid sessions with `comparison_completed` / sessions that created a real project and started a Real baseline. Always report numerator, denominator, and unique-user count separately.
- Suggestion adoption rate: first `suggestion_actioned` with action `adopt` or `edit_after_adopt` / first `suggestion_impression` events.
- System error rate: failed executable operations attributable to system or Provider / successful plus failed executable operations. Cancellation, validation rejection, and unavailable credentials are excluded.
- GEO Rule Score improvement: for eligible Real comparisons report before, after, absolute delta, and `(after-before)/before`; baseline zero is excluded from percentage averages.

Project deletion removes project-linked events or irreversibly anonymizes retained aggregates so they cannot be associated with the project or user.
