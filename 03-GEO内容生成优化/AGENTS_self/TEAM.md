# GEO Insight Studio MGX Team

Run mode: `full`.

## Enabled Roles

| Role | File | Accountable stages | Veto |
|---|---|---|---|
| Research | `geo-ai-agents/01-市场分析与用户研究专家.md` | discovery evidence, user validation, pilot interpretation | unsupported user or market assumptions |
| Product | `geo-ai-agents/02-产品经理与PRD负责人.md` | product decision, PRD, atomic backlog, acceptance | scope outside the approved loop |
| Design | `geo-ai-agents/03-UIUX设计师.md` | flows, visual direction, Figma truth, states and assets | incomplete, inaccessible or non-implementable design |
| Frontend | `geo-ai-agents/04-前端开发工程师.md` | React implementation, interactions, accessibility and browser evidence | unclear design or client contract |
| Backend | `geo-ai-agents/05-后端架构师.md` | FastAPI contracts, providers, data, security and observability | ambiguous or unsafe service contract |
| QA/Data | `geo-ai-agents/06-测试与数据迭代工程师.md` | traceability, defects, E2E, analytics and pilot data | untestable or unobservable behavior |
| Lead | `geo-ai-agents/07-总负责人与简历包装官.md` | owner assignment, arbitration, gates, release and final report | missing evidence, excessive risk or false completion |

Each role follows `Profile -> Goal -> Inputs -> Actions -> Skills Router -> Debate Rules -> Outputs -> Handoff -> Quality Gate -> Constraints -> Definition of Done`.

## Operating Rules

- Read `orchestration/WORKFLOW.md`, `orchestration/COLLABORATION_CONTRACTS.md`, `orchestration/SKILL_ROUTER.md`, the active run manifest and the upstream handoff before acting.
- Exactly one role owns each state. Contributors may review, but the accountable owner accepts the handoff.
- Mutable state lives under `agent-runs/`; this file only defines stable ownership.
- The user alone approves product direction, visual direction/GATE-2 and public release/GATE-3.
- Current stage is `DESIGN`, owned by Design. The Figma quota blocker returns the next action to the user; ownership returns to Design when quota is restored.
