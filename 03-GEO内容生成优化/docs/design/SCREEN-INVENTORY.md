# Screen Inventory And Contract

## Persistent Shell

- 左侧导航 72px：项目、运行记录、反馈；MVP 只激活项目，其他入口不扩展功能。
- 顶部 56px：项目名、保存状态、步骤进度、项目操作。
- S03-S05 固定运行上下文条 44px：内容来源、Mock/Real、Provider、模型、问题集版本、有效样本与置信状态。
- 主内容：最大可读宽度按任务变化；诊断与编辑使用全宽高密度工作区。
- 右侧检查器 360-420px：仅在证据、建议或运行详情需要时出现，不与卡片嵌套。

## Screens

| Screen | Purpose | Key regions | Required states | PRD |
|---|---|---|---|---|
| S01 Project Setup | 创建 Demo 或真实单页项目 | 输入源切换、品牌/受众、正文、竞品、删除确认 | default、validation、saving、delete_confirm、deleting、error | REQ-001、010 |
| S02 Prompt Set | 让用户掌控评测问题 | 意图筛选、问题列表、批量生成、人工新增、确认栏 | generating、editable、empty、error、dirty_confirmed | REQ-002 |
| S03 Baseline Run | 选择模式并观察真实执行 | 运行上下文、模式选择、逐问题进度、结果摘要、失败项 | ready、provider_unavailable、running、cancel_requested、cancelled、partial_success、failed、success | REQ-003-005 |
| S04 Diagnose & Optimize | 从证据到可控改稿 | 诊断摘要、证据列表、建议处理、正文工作副本、Diff、确认栏 | loading、N/A、no_mention、empty_suggestion、editing、waiting_confirmation、confirmed、stale、disabled | REQ-006-007 |
| S05 Compare & Feedback | 判断改动是否值得保留 | 条件一致性、Before/After、问题明细、限制、反馈 | running、partial_success、invalid_comparison、success、feedback_submitting、feedback_success、error | REQ-008-009 |

## Supporting Overlays

| Overlay | Trigger | Required behavior |
|---|---|---|
| Run Condition Drawer | 点击运行上下文条 | 展示条件快照；只读；关闭后焦点回到触发器 |
| Exit Feedback Dialog | S02-S05 中止或退出 | 原因可选，不阻止退出；失败可重试 |
| Delete Project Dialog | S01 项目操作 | 显示删除范围；删除中禁用重复操作 |
| Suggestion Evidence Inspector | 选择一条诊断/建议 | 原文、规则解释、影响和限制同屏，不单独跳页 |

## State Rules

- `partial_success` 至少有一条有效回答时允许预览诊断，但确认优化版本和正式比较保持禁用。
- `stale` 建议必须显示冲突片段和“重新诊断/放弃建议”，不得自动覆盖手动编辑。
- Mock/Real、内容来源和代理指标不能只用颜色表达。
- 错误必须贴近受影响区域；Toast 只负责确认，不承担恢复操作。
- `invalid_comparison` 必须列出不一致字段，不只显示一句“条件不同”。

## Responsive Contract

- Desktop 1366-1600：S04 使用主工作区 + 检查器；S05 使用顶部摘要 + 下方对比明细。
- Narrow 1024-1365：检查器改抽屉；Before/After 使用标签页；上下文条可横向滚动但不折叠关键模式。
- 小于 1024：允许查看和轻量编辑，不承诺完整高密度桌面体验；主操作不得被固定栏遮挡。
