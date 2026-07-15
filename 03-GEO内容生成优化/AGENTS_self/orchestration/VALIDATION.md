# 协作体系验证记录

## 验证范围

使用模拟需求验证协作协议本身，不代表真实产品已完成，也不构成三个用户门禁的批准。

模拟需求：`REQ-DEMO-001 用户提交一段 B2B/SaaS 官网内容，系统生成问题集、完成 GEO 诊断并给出 Before/After 对比。`

## 完整流程演练

| Stage | Owner | Simulated input | Expected output | Result |
|---|---|---|---|---|
| INIT | Lead | 模拟需求 | Run manifest | pass |
| DISCOVERY_DEBATE | Research + Product | 用户场景和竞品假设 | 两份独立提案、两轮辩论、PDR | pass |
| PRODUCT_APPROVAL | User gate | PDR，无用户批准 | 阻止进入 PRD | pass: blocked as designed |
| PRD_REVIEW | Product + reviewers | 测试注入的非生产 gate fixture | PRD、原子能力、埋点、追踪矩阵 | pass |
| DESIGN | Design | PRD | screen inventory、视觉方向、Figma handoff | pass by contract check |
| VISUAL_APPROVAL | User gate | Figma handoff，无用户批准 | 阻止进入技术规划 | pass: blocked as designed |
| TECH_PLANNING | Frontend + Backend | 测试注入的非生产 gate fixture | ADR、OpenAPI、数据模型、测试范围 | pass |
| BUILD | Frontend + Backend | 冻结契约 | React/FastAPI 构建与单测证据 | pass by contract check |
| INTEGRATION | Frontend + Backend + QA | 前后端构建 | mock、real、异常、降级联调证据 | pass by contract check |
| VERIFICATION | QA | 集成构建 | 测试矩阵和 release candidate | pass by contract check |
| RELEASE_APPROVAL | User gate | release candidate，无用户批准 | 阻止部署 | pass: blocked as designed |
| DEPLOYMENT_AND_PILOT | Engineering + QA | 测试注入的非生产 gate fixture | URL、E2E、事件和反馈 | pass by contract check |
| DATA_REVIEW | Research + Product + QA + Lead | 模拟事件集合 | 实验报告和下一轮决策 | pass by schema check |
| ACCEPTED | Lead | 所有模拟证据 | 最终报告 | pass by state-path check |

说明：`测试注入的非生产 gate fixture` 只用于验证后续状态结构，不能写入真实 run，也不能替代用户批准。

## P0 追踪演练

| Requirement ID | User job | PRD section | Figma frame | Frontend component | API | Data model | Test case | Event | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-DEMO-001 | 诊断并优化官网内容 | PRD/Core Flow | GEO-Diagnosis-Desktop | DiagnosisWorkspace | `POST /api/diagnose` | GeoDiagnosis | E2E-CORE-001 | `diagnosis_viewed` | traceable |

结果：需求可以从用户任务追踪到设计、组件、API、数据、测试和埋点。

## 边界场景

### 门禁跳过

- 删除 `user_approval_G1`：`PRODUCT_APPROVAL` 条件不完整，拒绝转换。
- 删除 `user_approval_G2`：`VISUAL_APPROVAL` 条件不完整，拒绝转换。
- 删除 `user_approval_G3`：`RELEASE_APPROVAL` 条件不完整，拒绝转换。

结果：三个门禁均不能仅凭 Agent 产物跳过。

### 辩论和返工上限

- `debate_round = 2` 后仍有争议：禁止第三轮，转总负责人裁决。
- `rework_cycle = 2` 后仍失败：下一次请求不得继续修改，转 `BLOCKED`。

结果：无限辩论和无限返工被协议阻止。

### Skill 不可用

- Figma 连接器不可用：记录 `unavailable`，设计阶段停在 `GATE-2` 之前。
- 部署后 `qa-engineer` 不可用：记录 `unavailable`，不得声称真实 URL 已通过 E2E。
- 当前 Action 无匹配 Skill：记录 `no_matching_skill`，由总负责人检查是否可继续。

结果：不能用普通图片、手工点击或虚构日志冒充必需能力。

## 静态验证结果

- 7 个 Agent 均包含完整 MGX 章节和具体 Skill 路由。
- `workflow.yaml`、manifest YAML 和 event JSONL 可解析。
- 标准路径包含三个门禁且顺序正确。
- 辩论/返工上限、事件集合和试用指标存在。
- 旧版前端技术约束已移除，当前基线为 React + TypeScript + Vite。
- 未发现形似 API Key 或 Bearer Token 的内容。
