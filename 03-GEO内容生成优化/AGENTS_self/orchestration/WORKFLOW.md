# GEO Insight Studio 协作工作流

## 1. 运行原则

每次项目运行使用唯一 `run-id`：`YYYYMMDD-HHMM-<stage>-<slug>`。总负责人先创建 `agent-runs/<run-id>/`，再按 `workflow.yaml` 推进状态。

状态推进必须同时满足：

1. 当前负责人完成允许的 Actions。
2. 必需产物存在且能被下一角色读取。
3. handoff 和 gate report 已填写。
4. blocker 为空，或有总负责人书面裁决。
5. 人工门禁已由用户明确确认，不得由 Agent 代签。

## 2. 初始化运行

从 `templates/run-manifest.yaml` 创建 `manifest.yaml`，并创建：

```text
agent-runs/<run-id>/
  manifest.yaml
  events.jsonl
  debates.md
  decisions.md
  handoffs.md
  gate-report.md
  artifacts.md
```

每个 Agent 开工前读取 README、自己的角色文件、当前 manifest、上游 handoff、Skill Router 和协作契约。

## 3. 阶段 SOP

### S0 INIT

- 负责人：总负责人。
- 动作：确定目标、范围、约束、运行模式和必须产物。
- 出口：manifest 完整，进入 `DISCOVERY_DEBATE`。

### S1 DISCOVERY_DEBATE

- 负责人：用户研究、产品经理。
- 轮次 1：双方独立提交用户、问题、价值、MVP、指标和风险。
- 轮次 2：交叉质询并针对有效挑战修订。
- 出口：总负责人形成 Product Decision Record。
- 超限：不开始第三轮，升级总负责人裁决。

### S2 PRODUCT_APPROVAL

- 必需：研究证据、竞品矩阵、两份独立提案、辩论记录、Product Decision Record。
- 人工门禁：`GATE-1 PRODUCT_APPROVAL`。
- 只有用户明确批准后才能进入 `PRD_REVIEW`。

### S3 PRD_REVIEW

- 负责人：产品经理。
- 动作：输出 PRD、需求追踪矩阵、埋点字典和 0-1-N backlog。
- 评审人：用户研究、设计、前端、后端、测试。
- 每轮：评审意见 -> 产品修订 -> 阻断项复核。
- 超限：两轮后仍有 blocker，提交总负责人裁决。

### S4 DESIGN

- 负责人：UI/UX 设计师。
- 顺序：screen inventory -> 用户流/状态 -> 低保真 -> 2-3 套生图视觉方向 -> 方向选择 -> Figma library -> 全状态页面 -> 可点击闭环。
- 评审人：产品、用户研究、前端。
- 生图只作为视觉参考和位图素材；精确文字与组件进入 Figma。

### S5 VISUAL_APPROVAL

- 必需：Figma 链接、组件库、全状态页面、素材清单、走查报告和无阻断证明。
- 人工门禁：`GATE-2 VISUAL_APPROVAL`。
- Figma 不可用或用户未批准时不得进入技术规划。

### S6 TECH_PLANNING

- 负责人：前端、后端；设计和测试参与。
- 固定基线：React + TypeScript + Vite；FastAPI + Pydantic；SQLite -> PostgreSQL；OpenAPI 真源。
- 动作：冻结 API 草案、数据模型、组件映射、测试边界和部署 ADR。
- 变更：冻结后字段变化必须新增 ADR 并通知产品、前端、后端和测试。

### S7 BUILD

- 前端先按 mock contract 建立 UI、状态和交互骨架。
- 后端并行实现冻结契约、Mock/Real Provider、指标和事件。
- 每个原子能力完成后立即执行类型检查、单元测试和局部验证。
- 不允许把全部测试推迟到集成结束。

### S8 INTEGRATION

- 顺序：mock contract -> real API -> 错误/超时 -> 部分成功 -> Demo 降级 -> 事件验证。
- 失败按协作契约生成 rework delta，返工最多两次。

### S9 VERIFICATION

- 测试建立并核对端到端追踪矩阵。
- 执行单元、API、迁移、本地浏览器、视觉回归和安全检查。
- P0/P1 缺陷必须清零，flake 和未覆盖范围必须披露。

### S10 RELEASE_APPROVAL

- 必需：本地验证报告、部署计划、回滚方案、数据合规说明和已知风险。
- 人工门禁：`GATE-3 RELEASE_APPROVAL`。
- 只有用户明确批准后才允许公网发布和邀请真实用户。

### S11 DEPLOYMENT_AND_PILOT

- 前端静态托管、FastAPI 独立托管，具体供应商写入 ADR。
- 数据迁移到托管 PostgreSQL，并验证回滚和备份。
- 使用 `qa-engineer` 对真实 URL 执行部署后 E2E。
- 经用户授权后邀请 5-10 位目标用户并采集匿名事件。

### S12 DATA_REVIEW

- 最低数据：5 次完整有效会话。
- 目标：核心流程完成率 >= 70%，建议采纳率 >= 30%，系统错误率 < 5%，真实模型 GEO Rule Score 平均提升 >= 15%。
- 同时收集定性反馈，说明样本偏差、异常数据和代理指标限制。
- 未达标不伪装完成；输出原因、证据和下一轮实验。

### S13 ACCEPTED

- 总负责人实际走通线上闭环并检查 E2E、埋点和试用数据。
- 最终报告包含已完成、未完成、真实数据、风险、下一轮和简历表达。

## 4. 返工和阻断

- 辩论最多两轮，开发/设计/测试返工最多两次。
- 每次返工必须有 `rework delta`：预期、实际、证据、责任人、允许修改范围和复验方式。
- 两次后无 meaningful progress，状态改为 `BLOCKED`，由总负责人裁决。
- 需要新权限、付费、发布、真实用户数据或外部账号时必须请求用户授权。

## 5. 事件与隐私

每次 Action 在 `events.jsonl` 写一行 JSON，字段遵循 `templates/event.example.jsonl`。记录可审计结论，不记录隐藏推理。

禁止写入：API Key、Cookie、Token、真实身份信息、未经脱敏的用户内容和模型隐藏思考过程。

## 6. 试用埋点

最低事件集合：

- `project_created`
- `prompts_generated`
- `evaluation_completed`
- `diagnosis_viewed`
- `optimization_generated`
- `suggestion_adopted`
- `comparison_completed`
- `feedback_submitted`

事件至少包含匿名 `session_id`、时间、模式、结果状态、耗时和错误类别；不得默认采集正文或个人信息。
