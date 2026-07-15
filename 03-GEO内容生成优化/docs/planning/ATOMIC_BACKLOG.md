# 0-1-N 原子能力 Backlog

## 拆分规则

每项必须能独立演示和验收；若缺少 UI 状态、服务输入输出、事件、测试或回滚方式，则不得进入开发。`0` 建立可运行 Mock 闭环，`1` 接入真实模型并完成 Pilot，`N` 只由真实数据触发。

## Iteration 0：可运行骨架与 Mock 闭环

| ID | 原子能力与用户价值 | 输入 / 处理 / 输出 | UI 与失败路径 | 服务与数据依赖 | 事件 | 验收与测试 | 回滚 |
|---|---|---|---|---|---|---|---|
| A0-01 | 加载 Demo，用户无需准备材料即可理解闭环 | 内置示例 / 创建项目 / Demo 项目 | S01 default、saving、error | Project、Content Version | `project_created` | T-001：一键进入问题页且全程标记 Demo | 关闭 Demo 入口 |
| A0-02 | 创建真实单页项目 | 品牌、受众、正文、竞品 / 校验 / 项目 | S01 validation、success | Project、基线版本 | `project_created` | T-002：边界值与字段错误准确 | 仅保留 Demo |
| A0-03 | 生成并人工确认问题集 | 项目语义 / Mock 生成、分类 / 10 个问题 | S02 generating、editable、empty、error | Prompt Set、版本号 | `prompts_generated` | T-003：可增删改，少于 3 个不可确认 | 退回人工录入 |
| A0-04 | 运行稳定 Mock 基线 | 已确认问题集 / 逐问题执行 / 回答结果 | S03 ready、running、cancelled、partial、failed | Evaluation Run、Answer Evidence | `evaluation_completed` | T-004：相同输入得到稳定演示结果；成功项不因重试丢失 | 禁用运行入口 |
| A0-05 | 查看可见性和证据 | 回答 / 识别品牌竞品 / 指标 | S03 summary、N/A、no_mention | Evidence、指标计算 | `diagnosis_viewed` | T-005：0 提及与 N/A 区分；不可核查引用不生成 URL | 隐藏非可信指标 |
| A0-06 | 查看规则诊断 | 正文与规则 / 打分、定位 / 诊断列表 | S04 loading、success、empty | Rule Diagnosis、规则版本 | `diagnosis_viewed` | T-006：每条有原文证据、影响和最小修复 | 降级为只读清单 |
| A0-07 | 人工处理优化建议 | 诊断 / 采纳拒绝手改 / 候选版本 | S04 editing、disabled、diff | Recommendation、Content Version | `optimization_generated`、`suggestion_adopted` | T-007：未确认不覆盖基线；无改动不创建版本 | 恢复基线版本 |
| A0-08 | Mock 同条件复评与对比 | 候选版本、原运行条件 / 复评 / Comparison | S05 running、invalid、success | 两个 Run、Comparison | `comparison_completed` | T-008：条件不一致时阻止提升计算 | 隐藏提升，仅展示两个独立结果 |
| A0-09 | 提交最小反馈 | 会话结果 / 评分与原因 / 反馈记录 | S05 submit、success、error | Feedback、匿名 session | `feedback_submitted` | T-009：失败可重试且不重复记数 | 暂停反馈入口 |
| A0-10 | 端到端最小埋点 | 核心动作 / 去敏、去重 / 事件流 | 无独立页面 | Event Log | 全部 P0 事件 | T-010：不含正文、Key、完整回答和 PII | 关闭分析写入，不影响业务 |

## Iteration 1：真实模型 GEO 闭环与 Pilot

| ID | 原子能力与用户价值 | 输入 / 处理 / 输出 | UI 与失败路径 | 服务与数据依赖 | 事件 | 验收与测试 | 回滚 |
|---|---|---|---|---|---|---|---|
| A1-01 | 配置并识别一个 Real Provider | 服务配置 / 可用性检查 / Real 可选 | S03 provider_unavailable | Provider Configuration | 无独立产品事件 | T-101：无 Key 时 Real 禁用且 Mock 可用 | 禁用 Real |
| A1-02 | 运行真实基线并支持部分重试 | 问题集 / Provider 执行与校验 / Run | S03 running、partial、timeout、failed | Run、Evidence、模型标识 | `evaluation_completed` | T-102：超时和畸形输出不伪造成成功 | 用户明确选择后新建 Mock Run |
| A1-03 | 固化可复现运行条件 | Provider、模型、问题版本、参数、规则版本、重复次数 / 冻结 / 条件摘要 | S03/S05 条件抽屉 | Run Condition Snapshot | 随运行事件携带非敏感版本字段 | T-103：条件变更产生新 Run，旧 Run 不变 | 禁止不兼容对比 |
| A1-04 | 真实诊断与候选改写 | 正文、Evidence / 结构化生成与校验 / 诊断和建议 | S04 partial、manual takeover | Rule Diagnosis、Recommendation | `optimization_generated` | T-104：无证据结果降级或失败；可手动接管 | 使用确定性规则诊断 |
| A1-05 | 真实同条件复评 | 优化版本、冻结条件 / 重复运行 / Comparison | S05 running、invalid、success | Before/After Run | `comparison_completed` | T-105：同问题集、模型、参数、规则版本和重复策略 | 仅展示独立结果 |
| A1-06 | 数据删除与保留期执行 | 删除请求 / 删除内容对象 / 结果 | 项目删除确认、完成、失败 | 项目内容与关联运行 | 管理事件，不进产品漏斗 | T-106：删除后不可读取；聚合事件无正文 | 暂停新建真实项目 |
| A1-07 | Pilot 追踪与业务验收 | 5-10 位用户 / 会话聚合 / 指标和反馈 | 内部报告，不做用户后台 | 去敏事件与访谈记录 | 核心漏斗事件 | T-107：可重算完成率、采纳率、错误率和 Rule Score 提升 | 不进入 N 期 |

## Iteration N：仅按证据触发

| 触发证据 | 候选能力 | 进入条件 |
|---|---|---|
| 用户需要跨任务复用 | 多项目历史与版本趋势 | 至少 3/5 有效用户明确需要且核心闭环达标 |
| 单 Provider 结论不可信 | 第二 Provider 并列评测 | 真实运行波动成为首要阻碍 |
| Citation N/A 过高 | URL 抓取与来源核验增强 | 合规与成本 ADR 通过 |
| 用户需要外部协作 | CSV/PDF/分享 | 至少 30% 完整会话尝试导出或明确提出 |
| 规则与采纳不一致 | 基于 Pilot 数据调权 | 有足够事件样本且不以小样本自动训练 |

## 开发准入

原子项进入开发前必须具备：对应 PRD Requirement ID、Figma Frame/状态、服务能力名、测试用例 ID、事件或明确 N/A、依赖和回滚。Iteration 1 必须在 Iteration 0 核心 E2E 通过后启动。
