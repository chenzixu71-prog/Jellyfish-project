# Tasks

## 1. Specification Review

- [x] Confirm search provider: Tavily is accepted for search.
- [x] Confirm first-version flow: search toggle exposes Tavily Search/Extract tools; tool failure degrades to empty or partial context.
- [ ] Confirm default value of `webSearchEnabled`: on or off.
- [ ] Confirm Tavily domain policy: unrestricted search, official-docs-first, or allowlist per query.
- [ ] Confirm whether source citations are shown in frontend immediately or only stored in backend.
- [x] Confirm fallback behavior: log warning and continue generation with empty search context.

## 2. Backend TDD

- [ ] Add tests for topic analyzer: normal, fresh, ambiguous, too-short input.
- [ ] Add tests for source provider interface with mock sources.
- [ ] Add tests for source-aware prompt construction.
- [ ] Add tests for `webSearchEnabled=false` not exposing Tavily tools.
- [ ] Add tests for keyword input using Tavily Search.
- [ ] Add tests for URL input using Tavily Extract.
- [ ] Add tests for dynamic Tavily parameters: result count, depth, domain filters, country.
- [ ] Add tests for Tavily Search/Extract timeout/failure warning and empty-context fallback.
- [ ] Add regression tests for current mock/deepseek request shape.

## 3. Backend Implementation

- [ ] Add `TopicAnalysis` schema.
- [ ] Add `SourceDocument` schema.
- [ ] Add `SourceProvider` interface.
- [ ] Add mock source provider for local tests.
- [ ] Add Tavily source provider using `langchain-tavily`.
- [ ] Add `TavilySearch` tool.
- [ ] Add `TavilyExtract` tool.
- [ ] Add backend env vars: `TAVILY_API_KEY`, `SEARCH_PROVIDER`, `SEARCH_MAX_RESULTS`, `SEARCH_DEPTH`.
- [ ] Add `EXTRACT_DEPTH` and `TAVILY_TIMEOUT_SECONDS`.
- [ ] Add search/extract timeout and formatted-context length limits.
- [ ] Add URL detection for tool-routing hints.
- [ ] Add source domain filtering support for trusted-source queries.
- [ ] Add tool-assisted quiz generation prompt.
- [ ] Extend quiz response parsing with optional source metadata.
- [ ] Record Tavily Search/Extract warning/source metadata in existing store/log path.

## 4. Frontend Implementation

- [ ] Extend `generateQuiz` request with `webSearchEnabled`.
- [ ] Add loading copy: “水母正在查找可靠资料”.
- [ ] Add optional联网搜索开关 UI if first version exposes the switch.
- [ ] Add URL input copy so users understand网页也可直接粘贴.
- [ ] Keep existing quiz page compatible with old question shape.
- [ ] Optionally show source chips in report page.

## 5. Documentation

- [ ] Update `docs/product-requirement-analysis.md` with fresh-knowledge generation requirement.
- [ ] Update `docs/solution-design.md` with source-aware generation architecture.
- [ ] Update README environment notes for Tavily Search/Extract setup.
- [ ] Update `backend/.env.example` with Tavily search variables.

## 6. Verification

- [ ] Run backend pytest.
- [ ] Run Taro build.
- [ ] Manually verify `Harness Engineering` no longer silently generates wrong-domain questions.
- [ ] Manually verify URL input extracts page content before quiz generation.
- [ ] Manually verify Tavily domain filtering with a Wikipedia-only query.
