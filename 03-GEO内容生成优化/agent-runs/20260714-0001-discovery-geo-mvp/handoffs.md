# Agent Handoffs

## Research to Product

- From: Agent 1
- To: Agent 2
- Stage: DISCOVERY_DEBATE
- Accepted facts: 竞品监测能力已较成熟；AutoGEO 支持规则发现和受控改写评测。
- Hypotheses: B2B/SaaS 内容运营愿意为可解释的单页诊断投入时间；需用访谈和试用验证。
- Non-goals: 首版不做多平台日更监控、全站爬虫或 RL 训练。
- Evidence: `evidence/` 下三份材料。
- Status: accepted-with-conditions；真实用户证据将在试用前补齐。

## Lead to User

- From: Agent 7
- To: User
- Stage: PRODUCT_APPROVAL
- Requested outcome: 确认或拒绝 `decisions.md` 中的产品基线。
- Allowed next action after approval: 进入 PRD_REVIEW，调用 PRD Skill 起草正式 PRD。
- Current blocker: none.
- Status: accepted；用户已于 2026-07-14 批准 `GATE-1`。

## User Gate to Product

- From: User
- To: Agent 2
- Stage: PRD_REVIEW
- Approved baseline: `decisions.md` 中的目标用户、单页闭环、P0/P1/Not Now 和成功指标。
- Required output: AI-native PRD、0-1-N 原子能力、事件字典、需求追踪矩阵和跨角色评审报告。
- Constraints: 不扩大已批准范围；产品主文档不提前写具体 API 或 schema。
- Status: accepted.

## Product to Design

- From: Agent 2
- To: Agent 3
- Stage: DESIGN
- Approved product source: `../../../docs/PRD.md` v1.0.
- Supporting inputs: `../../../docs/planning/ATOMIC_BACKLOG.md`、`EVENT_DICTIONARY.md`、`TRACEABILITY_MATRIX.md`。
- Required design output: Screen Inventory、状态模型、2-3 个生图视觉方向、Figma 变量与组件、五屏全状态原型、压力样本检查。
- Mandatory constraints: S03-S05 固定运行上下文条；Mock/Real 和代理指标不可弱化；精确文字和表格必须是 Figma 真实组件；不得用整张生成图冒充 UI。
- Gate: 完成内部闭环走查后请求 `GATE-2 VISUAL_APPROVAL`。
- User lock: 用户必须亲自敲定视觉方案；在收到明确“批准 GATE-2”前，禁止进入 TECH_PLANNING、BUILD 或实现生产 UI。
- Status: ready.

## Design Quota Blocker To User

- From: Agent 3
- To: User
- Stage: DESIGN
- Completed in Figma: Foundations, six reusable component groups, S01 default, S02 editable, S03 ready/running/partial success, approved S04 success, and S05 success.
- Pending: remaining failure/empty/stale states, five overlays, Prototype reactions, flow start point, responsive verification and asset pack.
- Evidence: `../../../docs/design/PROTOTYPE-INTERACTION-MAP.md` and Figma page `31:4`.
- Blocker: Codex/Figma usage limit reached; service reported retry availability at 2026-07-20 03:56 Asia/Shanghai unless credits are restored earlier.
- Gate impact: GATE-2 remains pending and cannot be requested.
- Resume owner: Agent 3 after quota restoration; user retains visual approval authority.
