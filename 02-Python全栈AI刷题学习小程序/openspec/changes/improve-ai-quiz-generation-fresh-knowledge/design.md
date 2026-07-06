# Design: Tavily Tool-Assisted AI Quiz Generation

## Current State

Current backend generation flow:

```text
content -> DeepSeek chat completion -> parse JSON -> Quiz model validation -> store quiz
```

This is enough for stable/basic topics, but weak for fresh or ambiguous knowledge because the model is asked to generate from memory.

## Target Flow

```text
user input
  -> API receives generate request
  -> check web_search_enabled
      -> false: search_context = empty
      -> true: provide tavily_search and tavily_extract tools to AI
          -> keyword/topic: AI may call tavily_search
          -> URL: AI may call tavily_extract
          -> simple knowledge: AI may use summaries only
          -> complex/fresh knowledge: AI may request deeper/richer context within backend limits
          -> failure/timeout: log warning and use empty or partial context
  -> assemble prompt: system role + user input + tool context + quiz requirements
  -> DeepSeek generates quiz JSON
  -> validate JSON structure
  -> save quiz + generation warning metadata
  -> return quiz to frontend
```

## Backend Components

### 1. Search Toggle And Tool Policy

Purpose: keep the first version controllable while allowing AI to decide whether to use keyword search or URL extraction.

Request policy:

- `webSearchEnabled=false`: do not expose Tavily tools; continue with empty `search_context`.
- `webSearchEnabled=true`: expose `tavily_search` and `tavily_extract` to the AI tool-use step.
- If user input contains URL-like text, AI should prefer `tavily_extract`.
- If user input is a keyword/topic, AI should prefer `tavily_search`.
- If Tavily fails, times out, or returns no useful results, log a warning and continue with empty or partial `search_context`.
- Do not block quiz generation only because a tool failed.

### 2. Tavily Tool Collector

Source types:

- `user_text`: user pasted text.
- `uploaded_text`: parsed file text.
- `url`: user supplied URL.
- `search_result`: Tavily search provider result.
- `extract_result`: Tavily extract provider result.

Implementation boundary:

- Define `SourceProvider` interface first.
- First implementation can be mock/local for tests.
- First real implementation uses Tavily via `langchain-tavily`.
- Other search providers can be added behind the same interface later.

Tavily integration shape:

```python
from langchain_tavily import TavilySearch, TavilyExtract

tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)

tavily_extract_tool = TavilyExtract(
    extract_depth="basic",
)
```

The backend should keep Tavily usage inside a service such as `search_service.py`, not inside route handlers.

Environment variables:

```text
TAVILY_API_KEY=
SEARCH_PROVIDER=tavily
SEARCH_MAX_RESULTS=5
SEARCH_DEPTH=basic
EXTRACT_DEPTH=basic
TAVILY_TIMEOUT_SECONDS=8
```

For narrow source requirements, the backend should support domain filters when the provider supports them, for example “only Wikipedia sources” or “prefer official docs”.

Tool choice rules:

| Input shape | Preferred tool | Parameter guidance |
| --- | --- | --- |
| Plain keyword/topic | `tavily_search` | Start with `max_results=3`, `search_depth=basic`, `include_raw_content=False` |
| New/niche/complex topic | `tavily_search` | Increase `max_results` to 5-8, consider `search_depth=advanced` or `include_raw_content` |
| User-provided URL | `tavily_extract` | Use `urls=[url]`, `query=user_input`, `chunks_per_source=3`, `format=markdown` |
| JS-heavy/table-heavy page | `tavily_extract` | Use `extract_depth=advanced` |
| User asks for specific domains | `tavily_search` | Use `include_domains` / `exclude_domains` where possible |
| Domestic/international context | `tavily_search` | Use `country` when the user implies region; e.g. `china`, `united states`, `united kingdom` |

Operational limits:

- Search timeout: configurable, recommended 5-8 seconds.
- Result limit: configurable, default 5.
- Extract timeout: configurable, recommended 8-12 seconds for URL pages.
- Context length: format only title + summary/snippet/content chunk + URL; truncate each item.
- Failure behavior: warning log + empty or partial search context.

### 3. Tool Context Formatter

Responsibilities:

- Convert Tavily Search and Extract results into concise prompt context.
- Preserve title, URL, and summary/snippet/content chunks.
- Truncate each result to avoid prompt bloat.
- For simple topics, prefer summaries/snippets.
- For fresh/complex topics, allow richer content chunks while staying under prompt budget.

LangChain fit:

- Use `langchain-tavily` for Tavily Search and Tavily Extract.
- Do not introduce vector store/retriever in the first implementation.
- Treat tool results as data only, not instructions.

### 4. Quiz Generator

Prompt changes:

- Include system role, user input, optional search context, and existing quiz requirements.
- Tell the model to decide whether to call `tavily_search`, `tavily_extract`, both, or neither.
- Tell the model to prefer tool context when present.
- Tell the model not to invent facts beyond user input/tool context when the topic is fresh or specific.
- Keep the existing quiz JSON shape required by frontend.

Prompt assembly shape:

```text
system_role

用户学习内容：
{user_input}

联网工具资料：
{formatted_tool_context or "无"}

出题要求：
{existing_quiz_requirements}
```

Compatibility:

- Existing frontend can continue reading `title`, `summary`, `questions`.
- Search warning/source metadata can be hidden at first and surfaced later.

Agent boundary:

- Tavily tools should be provided to AI for context gathering, not for final quiz validation.
- DeepSeek remains the final quiz generator.
- Final quiz JSON still goes through the same schema validator.

### 5. Grounding Validator

Validation checks:

- 5 questions exactly.
- 3 single, 1 multiple, 1 judge.
- Answers refer to valid options.
- Each question has explanation and knowledge point.
- In web-search mode, generation log records whether search succeeded, failed, timed out, or returned no results.

## API Impact

Existing endpoint remains:

```text
POST /api/generate-quiz
```

Request can be extended:

```json
{
  "sessionId": "local-session-id",
  "inputType": "text",
  "content": "Harness Engineering",
  "questionCount": 5,
  "webSearchEnabled": true
}
```

If `content` contains one or more URLs, the tool-use step should attempt Tavily Extract for those URLs. Response remains compatible when quiz is generated. Tool failure does not change response shape; it is recorded in logs and optional metadata.

## Data Impact

Future MySQL tables should support:

- `generation_logs`: prompt, model, source mode, confidence, latency, error.
- `generation_sources`: quiz_id, source_id, title, url, type, excerpt_hash.
- `question_sources`: question_id, source_id.
- `quality_feedback`: quiz_id, question_id, reason, user_comment.

Current in-memory store can add optional generation warning/source fields first.

## Frontend Impact

Taro pages keep current service pattern:

- Create page shows loading copy based on source mode.
- Search switch can be added later; first version may use backend default.
- Quiz/report pages can later expose source chips.

No heavy frontend state library is needed.

## Security and Safety

- Never execute instructions from retrieved pages.
- Do not crawl private, paid, or login-required content without explicit user-provided access.
- Log source metadata and short snippets, not full copyrighted page text where avoidable.
- Rate-limit retrieval and generation.

## Testing Strategy

Backend TDD first:

- Topic analyzer detects ambiguous fresh terms.
- Tavily Search provider mock returns deterministic keyword search results.
- Tavily Extract provider mock returns deterministic URL page content.
- Quiz prompt includes formatted tool context.
- Tavily Search/Extract failure or timeout logs warning and still generates with empty/partial context.
- Existing simple topics still generate normally.

Regression examples:

- `Git commit push pull`: should generate without retrieval.
- `Harness Engineering` with search enabled: AI should call Tavily Search and include context in prompt.
- `https://docs.langchain.com/.../tavily_extract` with search enabled: AI should call Tavily Extract and include page content.
- `Harness Engineering` with Tavily timeout: should generate normally with warning metadata.
- `Harness.io pipeline templates`: should use Tavily snippets when available.
- Very short input `AI`: should ask user to narrow topic.
- `What nation hosted the Euro 2024? Include only wikipedia sources.`: Tavily provider should support domain-constrained retrieval or return only accepted sources after filtering.
