# Design Brief

## Output Mode

`visual-handoff`。当前尚无生产前端项目，Figma 是设计真源；不会先写 standalone HTML 冒充产品，也不会在 GATE-2 前进入生产开发。

## 设计目标

让用户始终回答三个问题：现在运行的是什么条件、系统为什么给出这个判断、我能安全地改什么并如何恢复。

## Discovered UI Constraints

- 五屏结构与所有异常状态已经由 PRD 锁定。
- S03-S05 必须固定显示内容来源、Mock/Real、Provider、模型、问题集、样本数和置信状态。
- Rule Score 必须标注“代理指标”，不能成为页面唯一视觉焦点。
- Citation Availability 不等于语义真实性，N/A 原因必须直接可见。
- 工作副本必须支持逐条采纳、撤销、重置、stale 和显式确认。
- 桌面基准 1366px；窄屏单列/标签页，页面不得整体横向溢出。
- 不用嵌套卡片、营销 Hero、紫蓝渐变、玻璃拟态或整图式 UI。
- 主产品文字使用支持中文的无衬线字体；显示与数据可组合 IBM Plex Sans SC / Inter 类字体，最终以 Figma 可用字体为准。

## 视觉原则

1. Evidence first：证据片段和限制先于分数。
2. Context persistent：运行条件不藏进弹窗。
3. Quiet density：高密度但不让所有元素争抢注意力。
4. Recovery visible：失败、取消、部分成功和 stale 都在受影响区域恢复。
5. Human authority：AI 建议永远停在工作副本，用户确认才建立优化版本。

## GATE-2 Lock

需要用户确认：视觉方向、主色体系、字体气质、核心五屏、关键异常状态和切图素材风格。未收到明确“批准 GATE-2”前，设计师只能继续打磨设计，不得交接生产开发。
