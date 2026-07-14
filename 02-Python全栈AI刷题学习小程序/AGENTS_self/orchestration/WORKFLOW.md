# Project Workflow

States: `INIT → DISCOVERY_DEBATE → PRODUCT_APPROVAL → PRD_REVIEW → DESIGN → VISUAL_APPROVAL → TECH_PLANNING → BUILD → INTEGRATION → VERIFICATION → RELEASE_APPROVAL → DEPLOYMENT_AND_PILOT → DATA_REVIEW → ACCEPTED`.

Use `BLOCKED` when the same blocking condition has exhausted the allowed attempts and no safe work remains. Every transition requires current-state outputs, accepted handoff, event record and gate report when applicable.

Debate and rework are limited by `workflow.yaml`. Do not skip user gates. For non-UI work, GATE-2 may be N/A only with explicit user confirmation recorded in the gate report.

At each state, assign one accountable owner and the reviewers listed in `workflow.yaml`. Ownership changes with the state.


