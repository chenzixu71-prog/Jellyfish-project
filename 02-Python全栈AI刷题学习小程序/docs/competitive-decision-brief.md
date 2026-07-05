# 水母diy学习助手 - 竞品与产品决策简报

## 1. Decision Question

- 决策问题：水母diy学习助手的 MVP 应该优先做哪些学习闭环和游戏化能力，哪些竞品能力应该后置？
- 我方产品上下文：微信小程序 + Python 后端的 AI 互动学习项目，当前处于 Day 02 工程骨架阶段。
- 目标用户：想把自定义知识快速转成可练习内容的个人学习者。
- 时间范围：第一版 MVP 到项目 A 前 2 周。
- 参考对象：Duolingo、Quizlet、PM 提供的游戏化学习分析截图。
- 不在范围：完整企业培训平台、复杂会员计费、真实多人实时对战。

## 2. Executive Recommendation

- Recommendation：Adapt。
- Confidence：Medium。
- 结论：MVP 应复制“即时反馈 + 关卡进度 + 复盘报告”的学习闭环，谨慎适配“排行榜/勋章/连续签到”，暂时避免复制复杂社交竞争和重会员商业化。
- 如果后续用户更偏考试备考或企业培训，推荐会转向“知识库/RAG + 复习计划 + 管理后台”；如果用户更偏娱乐化学习，才提高 PK、排行榜、勋章优先级。

## 3. Evidence Base

| Evidence | Source | Level | Supports | Contradicts | Decision implication |
| --- | --- | --- | --- | --- | --- |
| Duolingo Max 把生成式 AI 用于互动对话、角色扮演和反馈，并保留人工课程设计与审核 | Duolingo 官方博客，2023-03-14，访问于 2026-07-06：https://blog.duolingo.com/duolingo-max/ | L1 | AI 学习产品要做互动反馈，不只是生成内容 | Duolingo 是语言学习，不是通用知识 DIY | 我们要把 AI 输出落到“题目 + 讲解 + 复盘”，而不是只做聊天 |
| Duolingo Leaderboards 用每周联赛和相似学习习惯匹配促进参与，也允许用户关闭排行榜 | Duolingo 官方博客，2023-05-03，访问于 2026-07-06：https://blog.duolingo.com/duolingo-leagues-leaderboards/ | L1 | 竞争机制能提高动力，但需要可退出 | 全局榜可能制造压力 | 我们先做轻量好友分享，不急着做全网排行 |
| Quizlet 是成熟学习工具，包含 flashcards、practice quizzes、collaborative games，并采用 freemium/subscription | Wikipedia 汇总，访问于 2026-07-06：https://en.wikipedia.org/wiki/Quizlet | L3 | 题卡、测试、协作游戏是成熟学习产品常见路径 | Wikipedia 不是一手产品证据 | 我们可借鉴“学习材料 -> 练习题”路径，但不把商业模式作为第一版目标 |
| PM 截图中把 MVP 定义为自由输入、AI 获取/解析知识、AI 生成题目、即时讲解、复盘报告、后台分析 | PM 提供截图，2026-07-06 | L1 | 明确我方核心闭环 | 输入范围过大 | MVP 需要收敛输入类型，先完成闭环 |
| PM 截图中列出 streak、leaderboard、badges、instant feedback 等游戏化要素 | PM 提供截图，2026-07-06 | L1 | 游戏化是产品方向 | 不是每个要素都适合 MVP | 即时反馈和关卡优先，排行榜/勋章后置 |

## 4. Competitor Pattern Map

| Pattern | Where observed | Product job it serves | Maturity | Relevance to us |
| --- | --- | --- | --- | --- |
| 即时反馈 | Duolingo Max、Quizlet Learn、PM 截图 | 让用户知道为什么对/错，形成认知闭环 | Table stakes | MVP 必做 |
| 关卡/路径 | Duolingo 学习路径、PM 闯关设想 | 把学习拆成可完成的小目标 | Common | MVP 必做 |
| 排行榜/联赛 | Duolingo Leaderboards | 增强竞争和留存 | Common | 后置，先不要做全网榜 |
| AI 互动角色 | Duolingo Max Roleplay/Video Call | 提高沉浸感和口语练习 | Differentiating | 只借鉴“场景化反馈”，不复制角色扮演 |
| AI 从材料生成学习内容 | Quizlet AI 工具方向、PM 截图 | 降低用户整理知识的成本 | Emerging/Common | MVP 核心方向，但先做文本输入 |
| 会员/VIP | Duolingo Max/Super、Quizlet Plus | 覆盖 AI 成本、提升收入 | Table stakes for mature products | 后置，先记录成本指标 |

## 5. Internal Translation

| External observation | Internal taxonomy | Copy / Adapt / Avoid / Validate | Why |
| --- | --- | --- | --- |
| Duolingo 用 AI 做互动反馈，不只生成题目 | AI capability | Adapt | 我们做通用知识学习，不做语言角色扮演，但要保留“讲解和改进建议” |
| Leaderboard 有激励，也可能带来压力 | Growth / Social | Adapt | 先做好友分享和个人进度，不做全网竞争 |
| Quizlet 从学习材料到练习题 | User task | Copy | 与“用户输入一个想学知识”高度一致 |
| VIP 订阅承载 AI 能力 | Pricing | Validate | AI 成本真实存在，但没有用户验证前不急着付费 |
| 多模态输入看起来强，但实现成本高 | Workflow / Ops | Avoid for MVP | 文档/视频/网页解析会拖慢第一版 |

## 6. Product Implications

- 定位：从“AI 刷题小程序”升级为“把任何想学知识 DIY 成闯关练习的学习助手”。
- 路线图：第一阶段完成文本输入、AI 出题、答题反馈、复盘报告；第二阶段再做 URL/文档解析；第三阶段再做知识库、排行榜和 VIP。
- 功能优先级：即时反馈 > 关卡进度 > 复盘报告 > 分享 > 勋章 > 排行榜 > PK。
- 定价/包装：先不做付费墙，保留模型调用次数记录，为后续 VIP 设计准备。
- 激活：首次进入要让用户 1 分钟内生成第一组题，而不是先注册和配置复杂资料。
- 信任与安全：AI 题目必须允许反馈错误；外部网页和文档解析要标注来源。
- 技术约束：后端要保存生成日志，方便追踪 AI 题目质量和成本。

## 7. What To Copy, Adapt, Avoid

| Action | Item | Reason | Validation |
| --- | --- | --- | --- |
| Copy | 即时反馈、正确答案、知识讲解 | 直接提升学习效果 | 用户答错后是否愿意继续下一题 |
| Copy | 关卡进度 | 让学习变成短闭环 | 用户是否完成一整组题 |
| Adapt | 分享复盘 | 适合微信小程序传播 | 先做文本分享，验证分享率 |
| Adapt | 勋章/连续学习 | 能增强留存，但不是第一天必须 | 观察 3 天留存后再做 |
| Avoid | 全网排行榜 | 容易制造压力，也需要反作弊 | 先做个人进度和好友分享 |
| Avoid | 视频/网页/文档全解析 | 成本和稳定性都高 | 先验证文本输入闭环 |
| Validate | VIP 盈利模式 | AI 成本需要覆盖，但太早收费会影响验证 | 记录生成次数和成本估算 |

## 8. Risks And Unknowns

- 弱证据：Quizlet 当前具体功能和价格没有完整一手网页证据，现阶段只作为方向参考。
- 缺少用户数据：还没有真实用户测试“输入知识 -> 生成题 -> 完成答题”的转化。
- 可能误读：游戏化不等于越多玩法越好，过度竞争可能降低学习体验。
- 合规/版权风险：解析网页、文档、视频时要确认用户有使用权。
- 反转信号：如果测试用户更需要“整理笔记”而不是“答题闯关”，产品重心要调整。

## 9. Next Validation

| Validation | Owner | Cost | Deadline | Success signal |
| --- | --- | --- | --- | --- |
| 文本输入生成 5 道题的端到端 demo | 产品/开发 | Low | Day 08 前 | 用户能从输入到结果页完成一轮 |
| 3 名目标用户试用 | PM | Low | MVP demo 后 | 至少 2 人认为“比自己整理题目省事” |
| 记录 AI 生成质量问题 | 产品/开发 | Low | 接入 AI 后 | 能收集错误题目和用户反馈 |
| 分享复盘文案测试 | PM | Low | 复盘页完成后 | 用户愿意复制或转发报告 |

## 10. Handoff

- Recommended next Skill：prd-architect。
- Suggested next prompt：把这份需求分析整理成水母diy学习助手的 AI-native PRD 初稿。
- Artifacts produced：
  - `docs/product-requirement-analysis.md`
  - `docs/competitive-decision-brief.md`
  - `docs/prd-ai-native-draft.md`

