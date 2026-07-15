# Product Decision Brief：GEO MVP 差异化

## 1. Decision Question

- 决策问题：首版应复制品牌 AI 可见性监测，还是聚焦单页内容的可解释诊断、改写与重评？
- 产品背景：简历优先、可在数周内完成、随后升级 SaaS。
- 目标用户：B2B/SaaS 内容运营、SEO/GEO 与增长营销人员。
- 调研对象：Profound、Peec AI、OtterlyAI、Semrush AI Visibility、Ahrefs Brand Radar、Scrunch。
- 不在范围：登录态深度走查、付费购买和私有客户数据。

## 2. Executive Recommendation

- Recommendation：选择“单页可解释 GEO 优化闭环”，不把首版定位成多平台长期监控工具。
- Confidence：Medium。
- 原因：监测、提示词追踪、提及/引用和竞品对比已成为竞品共同能力；本项目更适合用 AutoGEO 规则建立透明诊断和 Before/After 证据。
- 推翻条件：若首轮访谈显示目标用户只愿意为长期趋势监控付费，而不使用内容诊断，则重新评估定位。

## 3. Evidence Base

| Evidence | Source | Level | Decision implication |
|---|---|---|---|
| Profound 同时覆盖 Answer Engine Insights、Prompt Volumes、内容 Agents、Agent Analytics 和任务优先级 | [Profound](https://www.tryprofound.com/) | L1 | 企业全栈能力过重，不适合首版正面复制 |
| Peec AI 以 Visibility、Position、Sentiment 为核心，并提供 Prompts、Sources、Models 工作区 | [Peec AI](https://peec.ai/) | L1 | 监测仪表盘已形成明确产品范式 |
| Peec 定价与提示词、模型数量和项目规模绑定 | [Peec Pricing](https://peec.ai/pricing) | L1 | 多模型持续运行是主要成本驱动，应推迟 |
| Otterly 提供每日提示词追踪、引用分析、GEO URL Audit、推荐、API/MCP | [Otterly Pricing](https://otterly.ai/pricing) | L1 | 单纯增加 URL audit 不足以差异化，需要解释性和重评闭环 |
| Semrush 提供品牌表现、竞品、提示词追踪和站点 AI readiness，基础 AI Visibility 为每域每月 99 美元 | [Semrush Features](https://www.semrush.com/kb/1626-ai-visibility-features)、[Pricing](https://www.semrush.com/pricing/ai/) | L1 | SEO 套件优势难复制；可服务预算有限的小团队试用场景 |
| Ahrefs 用搜索支持的问题库做大规模发现，指标含 mentions、citations、impressions 和 share of voice | [Brand Radar](https://ahrefs.com/brand-radar)、[Metrics](https://help.ahrefs.com/en/articles/15501968-ai-visibility-metrics) | L1 | 数据库规模不是本项目可竞争方向，应强调小样本可复现评测 |
| Scrunch 将能力扩展到 AI agent 检测和为机器访问提供优化内容 | [Scrunch](https://scrunch.com/) | L1 | 边缘服务和 crawler experience 属于后续企业能力 |
| AutoGEO 显示规则组合与领域适配能提升受控 GEO 指标 | 用户提供论文 | L1 primary research | 规则诊断和同条件重评是本项目最强技术叙事 |

访问日期：2026-07-14。竞品功能和价格会变化，PRD 前应保留日期标签。

## 4. Competitor Pattern Map

| Pattern | Maturity | Relevance |
|---|---|---|
| Prompt tracking 与多模型覆盖 | Table stakes | 首版只保留固定问题集和一个真实 Provider |
| Mentions、citations、position、sentiment | Table stakes | 采用可计算子集，无法验证时显示 N/A |
| 竞品 benchmark 与 topic gaps | Common | 保留最多 3 个竞品的轻量对比 |
| GEO/AI readiness audit | Common | 必须升级为证据片段 + 规则原因 + 可执行修改 |
| 内容生成/Agent | Emerging to common | 只生成有变更解释的改写，不做通用写作 |
| AI crawler/agent analytics | Enterprise differentiator | N 阶段，不进入首版 |
| 大规模提示词数据库 | Incumbent advantage | 避免竞争，使用用户场景生成的小问题集 |

## 5. Internal Translation

| External observation | Action | Why |
|---|---|---|
| 竞品普遍先展示可见性总览 | Adapt | 首屏展示基线，但必须带样本范围和运行元数据 |
| 竞品以提示词数量和模型数量定价 | Avoid in P0 | 会快速扩大成本、调度和数据解释复杂度 |
| URL audit 和推荐已存在 | Adapt | 增加 AutoGEO 规则、证据定位、采纳/拒绝和同条件重评 |
| Ahrefs 强调搜索支持的超大问题库 | Avoid copying | 我们没有同类数据资产，不能用合成数量制造权威感 |
| Profound/Scrunch 扩展到 crawler 与 autonomous agents | Monitor | 证明长期空间存在，但不支撑简历 MVP |

## 6. Product Implications

- Positioning：Explainable GEO Page Optimizer，不是“全网 AI 排名监控平台”。
- Activation：加载 Demo 或粘贴一页内容后，尽快得到第一份基线诊断。
- P0：项目输入、问题集、单 Provider 基线、规则诊断、改写、重评、反馈与报告。
- Trust：展示证据、运行条件、N/A 和代理指标限制；禁止虚构来源。
- Technical：Provider 抽象、可复现 run metadata、稳定 mock 和真实评测分离。

## 7. Copy / Adapt / Avoid / Validate

| Action | Item | Validation |
|---|---|---|
| Copy | 清晰的 prompts/sources/models 信息结构 | 原型可用性走查 |
| Adapt | visibility 与 competitor overview | 限定小问题集并展示置信边界 |
| Adapt | GEO audit 与 recommendations | 增加 AutoGEO 规则和 Before/After 重评 |
| Avoid | 企业级 crawler analytics、多地区日更和大数据库叙事 | 保持在 N 阶段 |
| Validate | 用户是否愿意采纳系统改写 | 记录 suggestion adoption 和访谈原因 |

## 8. Risks And Unknowns

- 缺少真实用户访谈与登录态产品走查。
- 不同 LLM Provider 的浏览、引用和可复现能力不同。
- 小问题集不能代表全网可见性，报告必须明确样本边界。

## 9. Next validation

| Validation | Owner | Cost | Success signal |
|---|---|---|---|
| 5 位目标用户问题访谈 | User Research | Low | 至少 3 位认可“诊断 + 改写 + 重评”为高频任务 |
| 3 篇真实 B2B/SaaS 页面离线评测 | Product + Backend | Low | 可稳定生成规则证据和可解释差异 |
| 单 Provider 重复运行 3 次 | Backend + QA | Low | 能量化输出波动并确定报告口径 |

## 10. Handoff

- 推荐下一步：通过 `GATE-1` 后使用 `prd-architect` 起草正式 PRD，再由 `prd-review` 联合评审。
- 本文是决策输入，不代表已获得真实用户验证。
