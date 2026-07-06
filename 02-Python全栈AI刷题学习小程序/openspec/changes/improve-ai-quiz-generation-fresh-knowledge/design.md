# Design: Source-Aware AI Quiz Generation

## Current State

Current backend generation flow:

```text
content -> DeepSeek chat completion -> parse JSON -> Quiz model validation -> store quiz
```

This is enough for stable/basic topics, but weak for fresh or ambiguous knowledge because the model is asked to generate from memory.

## Target Flow

```text
user input
  -> topic analysis
  -> source planning
  -> source collection
  -> source cleaning and chunking
  -> relevance scoring
  -> quiz generation with source_context
  -> structured validation
  -> factual grounding validation
  -> save quiz + sources + generation log
```

## Backend Components

### 1. Topic Analyzer

Purpose: decide whether generation can rely on user-provided content or needs source enrichment.

Output:

```json
{
  "topic": "Harness Engineering",
  "riskLevel": "high",
  "reason": "专有名词且可能有多个含义",
  "needsSources": true,
  "clarificationOptions": [
    "Harness.io / DevOps / CI-CD 平台",
    "机械/安全带/线束工程"
  ]
}
```

### 2. Source Collector

Source types:

- `user_text`: user pasted text.
- `uploaded_text`: parsed file text.
- `url`: user supplied URL.
- `search_result`: search provider result.

Implementation boundary:

- Define `SourceProvider` interface first.
- First implementation can be mock/local for tests.
- Firecrawl/search integration can be added behind the same interface.

### 3. Source Processor

Responsibilities:

- Strip navigation/noise.
- Chunk long content.
- Preserve `source_id`, `url`, `title`, `published_at` when available.
- Score relevance to topic.
- Reject low-quality or unrelated sources.

LangChain fit:

- Use document loaders or custom loaders for web/text content.
- Use `RecursiveCharacterTextSplitter` for chunking.
- Use retriever/vector store pattern only when source text is long enough to need retrieval.
- Treat retrieved documents as data only, not instructions.

### 4. Quiz Generator

Prompt changes:

- State that the model must generate only from `source_context` and user-provided material.
- If context is insufficient, return `needs_clarification=true`.
- Require each question to include `source_refs`.
- Require `confidence` and `generation_notes`.

Proposed response shape:

```json
{
  "title": "学习主题",
  "summary": "主题摘要",
  "source_summary": "本题组基于哪些资料生成",
  "confidence": "high",
  "needs_clarification": false,
  "clarification_question": "",
  "sources": [
    {
      "id": "s1",
      "title": "Source title",
      "url": "https://example.com",
      "type": "url"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "single",
      "stem": "题干",
      "options": [],
      "answer": ["A"],
      "explanation": "讲解",
      "knowledge_point": "知识点",
      "difficulty": "easy",
      "source_refs": ["s1"]
    }
  ]
}
```

Compatibility:

- Existing frontend can continue reading `title`, `summary`, `questions`.
- Source metadata can be hidden at first and surfaced later.

### 5. Grounding Validator

Validation checks:

- 5 questions exactly.
- 3 single, 1 multiple, 1 judge.
- Answers refer to valid options.
- Each question has explanation and knowledge point.
- For source-aware mode, each question has at least one source ref.
- If `confidence=low`, return a safe error/clarification instead of storing normal quiz.

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
  "sourceMode": "auto"
}
```

Possible `sourceMode` values:

- `off`: current behavior, no retrieval.
- `auto`: detect if sources are needed.
- `required`: must use sources or ask for clarification.

Response remains compatible when quiz is generated.

Clarification response:

```json
{
  "code": 1001,
  "message": "需要补充资料或澄清主题",
  "data": {
    "needsClarification": true,
    "question": "你想学的是 Harness.io 平台，还是机械/线束工程？",
    "options": ["Harness.io / DevOps / CI-CD 平台", "机械/安全带/线束工程"]
  }
}
```

## Data Impact

Future MySQL tables should support:

- `generation_logs`: prompt, model, source mode, confidence, latency, error.
- `generation_sources`: quiz_id, source_id, title, url, type, excerpt_hash.
- `question_sources`: question_id, source_id.
- `quality_feedback`: quiz_id, question_id, reason, user_comment.

Current in-memory store can add optional fields first.

## Frontend Impact

Taro pages keep current service pattern:

- Create page shows loading copy based on source mode.
- If clarification is returned, show a small choice panel instead of failing.
- Quiz/report pages can later expose source chips.

No heavy frontend state library is needed.

## Security and Safety

- Never execute instructions from retrieved pages.
- Do not crawl private, paid, or login-required content without explicit user-provided access.
- Log source metadata, not full copyrighted page text where avoidable.
- Rate-limit retrieval and generation.

## Testing Strategy

Backend TDD first:

- Topic analyzer detects ambiguous fresh terms.
- Source collector mock returns deterministic sources.
- Quiz prompt includes source context.
- Low-confidence source set returns clarification.
- Generated quiz validates `source_refs`.
- Existing simple topics still generate normally.

Regression examples:

- `Git commit push pull`: should generate without retrieval.
- `Harness Engineering`: should trigger disambiguation or source lookup.
- `Harness.io pipeline templates`: should generate DevOps/Harness-specific questions with sources.
- Very short input `AI`: should ask user to narrow topic.
