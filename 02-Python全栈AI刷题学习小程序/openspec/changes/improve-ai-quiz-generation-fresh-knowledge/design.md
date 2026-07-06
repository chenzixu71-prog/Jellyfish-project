# Design: Search-Optional AI Quiz Generation

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
      -> true: call Tavily with timeout and max_results
          -> success: format title + summary snippets with length limits
          -> failure/timeout: log warning and use empty search_context
  -> assemble prompt: system role + user input + search context + quiz requirements
  -> DeepSeek generates quiz JSON
  -> validate JSON structure
  -> save quiz + generation warning metadata
  -> return quiz to frontend
```

## Backend Components

### 1. Search Toggle And Request Policy

Purpose: keep the first version simple and controllable. The API receives an explicit or default search switch.

Request policy:

- `webSearchEnabled=false`: do not call Tavily; continue with empty `search_context`.
- `webSearchEnabled=true`: call Tavily with configured timeout and result limit.
- If Tavily fails, times out, or returns no useful results, log a warning and continue with empty `search_context`.
- Do not block quiz generation only because search failed.

### 2. Tavily Search Collector

Source types:

- `user_text`: user pasted text.
- `uploaded_text`: parsed file text.
- `url`: user supplied URL.
- `search_result`: Tavily search provider result.

Implementation boundary:

- Define `SourceProvider` interface first.
- First implementation can be mock/local for tests.
- First real search implementation uses Tavily via `langchain-tavily`.
- Other search providers can be added behind the same interface later.

Tavily integration shape:

```python
from langchain_tavily import TavilySearch

tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)
```

The backend should keep Tavily usage inside a service such as `search_service.py`, not inside route handlers.

Environment variables:

```text
TAVILY_API_KEY=
SEARCH_PROVIDER=tavily
SEARCH_MAX_RESULTS=5
SEARCH_DEPTH=basic
```

For narrow source requirements, the backend should support domain filters when the provider supports them, for example “only Wikipedia sources” or “prefer official docs”.

Operational limits:

- Search timeout: configurable, recommended 5-8 seconds.
- Result limit: configurable, default 5.
- Context length: format only title + summary/snippet + URL; truncate each item.
- Failure behavior: warning log + empty search context.

### 3. Search Context Formatter

Responsibilities:

- Convert Tavily results into concise prompt context.
- Preserve title, URL, and summary/snippet.
- Truncate each result to avoid prompt bloat.
- Do not include raw pages in the first version unless explicitly enabled later.

LangChain fit:

- Use `langchain-tavily` for Tavily Search.
- Do not introduce vector store/retriever in the first implementation.
- Treat search snippets as data only, not instructions.

### 4. Quiz Generator

Prompt changes:

- Include system role, user input, optional search context, and existing quiz requirements.
- Tell the model to prefer search context when present.
- Tell the model not to invent facts beyond user input/search context when the topic is fresh or specific.
- Keep the existing quiz JSON shape required by frontend.

Prompt assembly shape:

```text
system_role

用户学习内容：
{user_input}

联网搜索资料：
{formatted_search_context or "无"}

出题要求：
{existing_quiz_requirements}
```

Compatibility:

- Existing frontend can continue reading `title`, `summary`, `questions`.
- Search warning/source metadata can be hidden at first and surfaced later.

Agent boundary:

- Tavily should be used inside a controlled search step, not as an autonomous quiz-writing agent.
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

Response remains compatible when quiz is generated. Search failure does not change response shape; it is recorded in logs and optional metadata.

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
- Tavily source provider mock returns deterministic sources.
- Quiz prompt includes source context.
- Tavily failure/timeout logs warning and still generates with empty context.
- Existing simple topics still generate normally.

Regression examples:

- `Git commit push pull`: should generate without retrieval.
- `Harness Engineering` with search enabled: should include Tavily search context in prompt.
- `Harness Engineering` with Tavily timeout: should generate normally with warning metadata.
- `Harness.io pipeline templates`: should use Tavily snippets when available.
- Very short input `AI`: should ask user to narrow topic.
- `What nation hosted the Euro 2024? Include only wikipedia sources.`: Tavily provider should support domain-constrained retrieval or return only accepted sources after filtering.
