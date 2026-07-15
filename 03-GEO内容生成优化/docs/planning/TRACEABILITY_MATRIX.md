# P0 Traceability Matrix

Design nodes are real Figma nodes. Code, API, database, and executable test paths remain planned until GATE-2 is approved.

| Requirement | Figma nodes | Frontend module | Backend capability | Data object | Test IDs | Event | Status |
|---|---|---|---|---|---|---|---|
| REQ-001 Project | `42:2`, `56:60`, `56:182`, `51:52` | `projects` | Project CRUD and deletion | Project, ContentVersion | T-001, T-002, T-106 | `project_created` | design ready |
| REQ-002 Prompt set | `43:16`, `57:88`, `57:222`, `57:358` | `prompt-sets` | Generate, edit, confirm, invalidate | PromptSet, Prompt | T-003 | `prompts_generated` | design ready |
| REQ-003 Mode | `44:18`, `58:94`, `50:27` | `evaluations` | Provider capability and run conditions | RunCondition | T-101 | operation audit | design ready |
| REQ-004 Baseline run | `45:19`, `46:21`, `58:203`, `58:324` | `evaluations` | Run, progress, cancel, retry | EvaluationRun, Attempt | T-004, T-102 | `evaluation_completed` | design ready |
| REQ-005 Visibility | `47:23`, `60:99`, `75:578` | `diagnosis` | Mention, position, citation metrics | AnswerEvidence | T-005 | `diagnosis_viewed` | design ready |
| REQ-006 Rules | `47:23`, `59:99`, `60:297` | `diagnosis` | rules-v1 scoring and evidence | RuleDiagnosis | T-006, T-104 | `diagnosis_viewed` | design ready |
| REQ-007 Optimization | `75:2`, `75:194`, `55:58`, `75:386`, `59:295`, `75:578` | `optimization` | Draft, adopt, edit, stale, confirm | Recommendation, ContentVersion | T-007 | `optimization_generated`, `suggestion_actioned` | design ready |
| REQ-008 Comparable rerun | `75:386`, `61:99`, `61:237`, `61:378`, `49:25` | `comparisons` | Fingerprint, rerun, eligibility | RunCondition, Comparison | T-008, T-103, T-105 | `comparison_completed` | design ready |
| REQ-009 Report and feedback | `48:23`, `54:56`, `62:105`, `62:144`, `62:186` | `comparisons`, `feedback` | Report and idempotent feedback | Comparison, Feedback | T-009 | `comparison_completed`, `feedback_submitted` | design ready |
| REQ-010 Data control | `51:52` | `projects` | Cascade deletion and anonymized events | Project graph | T-106 | deletion audit | confirm state ready; terminal states planned |

## Responsive Mapping

- Form: `75:770` (1366), `75:1195` (1024).
- Diagnosis: `75:871` (1366), `75:1296` (1024 inspector drawer).
- Comparison: `75:1063` (1366), `75:1488` (1024).

## Build Gate

- GATE-2 must be explicitly approved by the user.
- Each frontend and backend module must be replaced with a real source path.
- OpenAPI operation IDs, database tables, and executable test paths must be added before verification.
