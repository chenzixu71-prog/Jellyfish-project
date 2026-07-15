# GEO Insight Studio MGX Agent Team

本目录定义 GEO Insight Studio 的多 Agent 协作团队。团队采用角色、Action、共享产物、阶段门禁和可追踪日志推进项目，不允许角色各自生成互不兼容的结论。

## 已锁定基线

- 产品：面向 B2B/SaaS 团队的 AI 搜索可见性诊断与内容优化平台。
- 前端：React + TypeScript + Vite，按 Figma 设计真源实现。
- 后端：FastAPI + Pydantic；本地 SQLite，邀请试用前迁移托管 PostgreSQL。
- AI：稳定 Mock Provider + 可选真实 LLM Provider，二者必须明确区分。
- 上线：前端静态托管、后端独立托管，供应商由上线 ADR 决定。
- 试用：邀请 5-10 位目标用户并采集匿名事件数据。

## 团队角色

1. `geo-ai-agents/01-市场分析与用户研究专家.md`
2. `geo-ai-agents/02-产品经理与PRD负责人.md`
3. `geo-ai-agents/03-UIUX设计师.md`
4. `geo-ai-agents/04-前端开发工程师.md`
5. `geo-ai-agents/05-后端架构师.md`
6. `geo-ai-agents/06-测试与数据迭代工程师.md`
7. `geo-ai-agents/07-总负责人与简历包装官.md`

## 启动顺序

1. 读取 `orchestration/WORKFLOW.md` 和 `orchestration/workflow.yaml`。
2. 创建 `agent-runs/<run-id>/`，复制运行模板并填写 manifest。
3. 当前 Agent 读取自己的角色文件和 `orchestration/SKILL_ROUTER.md`。
4. 只执行当前状态允许的 Action，写入事件和产物路径。
5. 通过门禁后才更新状态并交接给下一角色。

## 三个人工门禁

- `GATE-1 PRODUCT_APPROVAL`：产品方案确认。
- `GATE-2 VISUAL_APPROVAL`：Figma 视觉定稿确认。
- `GATE-3 RELEASE_APPROVAL`：上线前验收确认。

任何 Agent 和总负责人都不得代替用户通过这三个门禁。

## 统一硬规则

- Skill 调用前完整读取其 `SKILL.md`，并在日志记录调用证据。
- Skill 未暴露或不可调用时记录 `unavailable`，不得假装调用成功。
- 辩论最多两轮，返工最多两次；超限升级给总负责人。
- 没有交接单、产物路径和门禁报告，不得进入下一阶段。
- 只记录结论、证据和决策，不记录隐藏推理过程、密钥或个人隐私。
- 不做黑帽 GEO、Prompt 注入、虚假来源、虚假引用或误导性指标。
- 生图只用于视觉方向和位图素材；准确 UI 文本与组件必须在 Figma 和代码中实现。

## 共享协议

- `orchestration/WORKFLOW.md`：协作 SOP 与阶段门禁。
- `orchestration/workflow.yaml`：机器可读状态机。
- `orchestration/SKILL_ROUTER.md`：Skill 发现、选择和记录规则。
- `orchestration/COLLABORATION_CONTRACTS.md`：辩论、否决、交接和裁决契约。
- `orchestration/VALIDATION.md`：模拟需求、门禁、返工和追踪链演练记录。
- `orchestration/templates/`：运行记录、ADR、门禁和实验模板。
