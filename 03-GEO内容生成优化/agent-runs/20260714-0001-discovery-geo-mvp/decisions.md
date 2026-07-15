# Product Decision Record PDR-001

## Decision

首版产品定为：`GEO Insight Studio - Explainable GEO Page Optimizer`。

一句话定位：面向 B2B/SaaS 内容与增长人员，对单页内容生成受控 AI 问题集，诊断其被提及或引用的阻碍，给出基于 AutoGEO 规则的可解释改写，并在同一评测条件下展示 Before/After。

## Target User

- 第一用户：B2B/SaaS 内容运营或 SEO/GEO 负责人。
- 第二用户：小团队增长负责人、内容营销代理人员。
- 首轮试用对象：5-10 位拥有真实产品页或文章优化任务的人。

## Core Journey

```text
加载 Demo 或创建单页项目
-> 填写品牌、目标用户、页面内容、最多 3 个竞品
-> 生成并确认 10-20 个问题
-> 运行 Mock 或一个真实 LLM Provider 基线
-> 查看品牌/竞品出现情况和 AutoGEO 规则诊断
-> 采纳、拒绝或修改优化建议
-> 在同一问题集和运行条件下重评
-> 查看 Before/After、证据和限制
-> 提交反馈
```

## P0

1. Demo 数据和单页项目配置。
2. 问题集生成、编辑和分类。
3. 稳定 Mock 与一个真实 Provider，界面明确显示模式。
4. 基线答案、品牌提及、相对位置和轻量竞品对比。
5. Citation 仅在可核查时计算，否则显示 N/A。
6. AutoGEO 规则维度、原文证据、影响等级和修复建议。
7. 可选择的内容改写，并记录采纳、拒绝和手动修改。
8. 同条件重评、Before/After 和 run metadata。
9. 反馈事件和一页结果报告。

## P1

- 单用户多项目历史和版本对比。
- 两个 Provider 的并列评测。
- URL 抓取与引用来源增强。
- CSV/PDF 报告和分享链接。
- 基于试用数据的规则权重调整。

## N / Not Now

- 多地区、多语言、每日提示词趋势。
- 全站爬虫、AI crawler analytics 和自动 CMS 发布。
- 团队权限、订阅支付、复杂队列和企业集成。
- AutoGEOMini 强化学习训练。

## Metrics

- 至少 5 次完整有效试用会话。
- 核心闭环完成率 >= 70%。
- 建议采纳率 >= 30%。
- 系统错误率 < 5%。
- 真实模型 GEO Rule Score 平均提升 >= 15%。
- Brand Mention/Position 变化作为探索结果，不设硬承诺。

## Trust And Measurement Rules

- 报告必须区分 Mock、真实模型输出和代理指标。
- Before/After 记录 Provider、模型、问题集版本、参数、时间和重复次数。
- 不把小问题集结果称为全网排名、真实流量或收入增长。
- 不生成虚假引用；无法验证的来源标记为待补充。

## Tradeoffs

- 选择深度：单页闭环与解释性。
- 放弃广度：多平台趋势、全站规模和企业功能。
- 选择可复现：固定问题集和运行元数据。
- 接受限制：首轮用户与价值仍需真实试用验证。

## What Would Reverse This Decision

- 5 位以上目标用户中少于 2 位认可单页诊断任务。
- 真实 Provider 输出波动使 Before/After 无法形成可解释结果。
- 用户只愿为持续监测付费，且不采纳内容修复建议。

## Verdict

- Owner: Agent 7
- Status: approved by user at 2026-07-14T12:59:40+08:00
- Confidence: Medium
- Next action: 使用 `prd-architect` 生成 PRD，再由五角色评审。
