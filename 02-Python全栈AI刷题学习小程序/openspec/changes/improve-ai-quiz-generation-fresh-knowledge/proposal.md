# Proposal: Improve AI Quiz Generation For Fresh Knowledge

## Summary

优化“AI 生成题目”能力，解决新知识、冷门知识、歧义主题下模型凭训练记忆出题导致的错误题目、错误讲解和错领域理解问题。

典型问题：用户输入 `Harness Engineering` 时，模型可能没有识别为 Harness.io / DevOps / CI/CD 相关上下文，而是生成另一个领域的 “harness engineering” 知识。

## Why

现有方案主要依赖用户输入 + 大模型自身知识。对于训练数据有时限、概念很新、名称有歧义的主题，模型容易：

- 把新概念解释成旧概念。
- 把专有名词理解成普通名词。
- 生成看似完整但来源不可追踪的题目。
- 给初学者建立错误认知。

需求分析文档已记录“AI 自动获取全网知识存在质量风险”和“AI 题目可能出错”。本变更把风险处理前置到生成链路。

## Goals

- 生成前先判断主题是否新、冷门或有歧义。
- 对需要新知识的主题，先检索或解析来源，再基于来源出题。
- 每组题目保留来源摘要、来源列表和置信度。
- 每道题的答案和讲解能追溯到来源片段或用户提供材料。
- 证据不足时不强行生成，返回“需要补充资料/需要澄清主题”的状态。

## Non-Goals

- 本次不实现完整长期知识库。
- 本次不做复杂多轮 Agent 自动浏览所有网页。
- 本次不做视频理解、图片 OCR 或付费内容抓取。
- 本次不改变核心 5 题闯关链路。
- 本次不把 DeepSeek API Key 暴露到前端。

## Proposed Scope

### P0: Generation Quality Gate

- 主题识别：判断输入是普通主题、专有名词、URL、文档摘要还是歧义主题。
- 风险标记：识别“可能需要新资料”的输入。
- Prompt 加强：要求模型不得超出提供来源编造事实。
- JSON 扩展：增加 generation metadata，但保持 questions 主结构兼容。

### P1: Source-Aware Quiz Generation

- 引入来源上下文：
  - 用户输入文本。
  - 用户上传文件解析文本。
  - 用户粘贴 URL 或指定资料 URL 后的网页文本。
  - 后端检索结果摘要。
- 题目生成必须基于 `source_context`。
- 每题增加 `source_refs`，指向来源编号。

### P2: Fresh Knowledge Retrieval

- 后端增加检索服务接口。
- 第一版搜索供应商优先使用 Tavily，通过 `langchain-tavily` 的 `TavilySearch` 工具接入。
- 支持最小检索策略：搜索结果标题、摘要、URL、抓取正文片段。
- 对检索内容做去噪、切分、评分和来源记录。
- 对来源不足或冲突的主题返回澄清状态。

### Tavily Search Decision

用户已确认可以使用 Tavily 做 search。第一版采用：

```python
from langchain_tavily import TavilySearch

tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)
```

后端配置：

- `TAVILY_API_KEY`：Tavily API Key，只放后端环境变量。
- `SEARCH_PROVIDER=tavily`：用于后续保留供应商切换能力。
- `SEARCH_MAX_RESULTS=5`：默认搜索结果数。
- `SEARCH_DEPTH=basic`：默认先用 basic，必要时再升 advanced。

检索结果必须进入来源记录，不允许前端直接调用 Tavily。

## User Experience

用户输入新知识主题后：

1. 系统显示“水母正在查找可靠资料”。
2. 如果找到足够资料，正常生成题目。
3. 答题页/报告页可显示“本题参考资料”入口。
4. 如果资料不足，提示：
   - “这个主题可能较新或有歧义，请补充一段资料或指定官网/文档链接。”
5. 如果主题有多个含义，提示用户选择方向，例如：
   - “你想学的是 Harness.io 工程平台，还是机械/安全带相关的 harness engineering？”

## Risks

- 搜索结果不一定准确，需要来源评分和来源展示。
- 网页抓取有版权和反爬限制，不能抓取付费或未授权内容。
- 引入检索会增加生成耗时和成本。
- 来源内容可能包含 prompt injection，需要把来源作为数据处理，不能执行来源里的指令。

## Open Questions

- 第一版是否只允许用户粘贴 URL，而不做全网搜索？
- Tavily 默认搜索范围是否需要限制官方文档、Wikipedia、GitHub、产品官网等可信域名？
- 是否允许生成“来源不足但可基于用户输入出题”的低置信度题组？
- 前端是否第一版展示来源，还是先只在后端记录？
