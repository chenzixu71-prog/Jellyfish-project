# Prototype Interaction Map

## Status

`ready for product re-review; GATE-2 still requires explicit user approval`

Figma: [GEO Insight Studio Product UI](https://www.figma.com/design/9gT4hUvANiiiGrGGq1313l/GEO-Insight-Studio---Visual-Directions---Product-UI?node-id=31-4)

## Product Contract

- Prompt set: default 10, minimum 3, maximum 20.
- Real evaluation: one Provider; each question repeats 3 times.
- Partial success: diagnosis preview only; optimization confirmation, formal re-evaluation, and KPI are disabled.
- Formal comparison requires an identical condition fingerprint except for the approved content version.
- Invalid comparison shows independent results and `N/A`; it never reports improvement.
- Report metrics: GEO Rule Score (proxy), Brand Mention Rate, Relative Position, Citation Availability, and per-question differences.

## Screen Inventory

| Requirement | State | Figma node |
|---|---|---:|
| REQ-001 | project default / validation / saving error | `42:2`, `56:60`, `56:182` |
| REQ-002 | prompt editable / generating / empty / error | `43:16`, `57:88`, `57:222`, `57:358` |
| REQ-003/004 | run ready / running / partial / provider unavailable / cancelled / failed | `44:18`, `45:19`, `46:21`, `58:94`, `58:203`, `58:324` |
| REQ-005/006 | diagnosis success / loading / stale / no mention / empty suggestions | `47:23`, `59:99`, `59:295`, `60:99`, `60:297` |
| REQ-007 | editing / waiting confirmation / confirmed / partial read-only preview | `75:2`, `75:194`, `75:386`, `75:578` |
| REQ-008/009 | comparison success / invalid / running / partial / error | `48:23`, `49:25`, `61:99`, `61:237`, `61:378` |
| REQ-009 | feedback default / submitting / success / error | `54:56`, `62:105`, `62:144`, `62:186` |
| REQ-010 | delete confirmation | `51:52` |
| Shared | conditions drawer / exit dialog / revision dialog | `50:27`, `52:54`, `55:58` |

## Core Prototype Flow

1. `42:2` create project -> `43:16` prompt set.
2. `43:16` confirm prompts -> `44:18` run ready.
3. `44:18` start -> `45:19` running.
4. Full success enters `47:23`; partial success `46:21` can only enter read-only `75:578`.
5. `47:23` -> `75:2` editing -> `75:194` waiting confirmation.
6. `75:194` opens `55:58`; confirmation enters `75:386` frozen version.
7. `75:386` starts same-condition re-evaluation at `61:99`; completion enters `48:23`.
8. `48:23` opens feedback `54:56` -> `62:105` submitting -> `62:144` success. Error `62:186` retries to submitting.
9. Invalid conditions enter `49:25`; all deltas are `N/A` and the recovery action returns to condition selection.

The Figma flow starting point is `42:2` (`GEO MVP Core Flow`). Dialog cancel and close actions use `CLOSE`; transitions use 200 ms dissolve.

## Responsive Evidence

| Surface | 1366 | 1024 |
|---|---:|---:|
| Project form | `75:770` | `75:1195` |
| Diagnosis workspace | `75:871` | `75:1296` |
| Comparison report | `75:1063` | `75:1488` |

At 1024 px the global sidebar is removed and the diagnosis inspector becomes a drawer entry. Post-repair overflow audit returned zero compressed layout findings; residual long-text overflow was corrected in the responsive frames.

## Product Re-review Checklist

- Verify all counts and request estimates use 10 questions and 30 Real requests.
- Verify S03 ready, running, partial, cancelled, and failed data are internally consistent.
- Verify partial and invalid states never expose formal improvement.
- Verify baseline content is unchanged before optimization confirmation.
- Verify all feedback and retry paths are reachable.
- Verify GATE-2 remains blocked until the user explicitly approves it.
