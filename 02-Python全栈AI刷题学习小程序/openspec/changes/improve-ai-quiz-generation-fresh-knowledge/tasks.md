# Tasks

## 1. Specification Review

- [ ] Confirm whether first version supports search, user-provided URL only, or both.
- [ ] Confirm whether source citations are shown in frontend immediately or only stored in backend.
- [ ] Confirm fallback behavior when sources are insufficient.

## 2. Backend TDD

- [ ] Add tests for topic analyzer: normal, fresh, ambiguous, too-short input.
- [ ] Add tests for source provider interface with mock sources.
- [ ] Add tests for source-aware prompt construction.
- [ ] Add tests for quiz validation requiring `source_refs` in source-aware mode.
- [ ] Add tests for clarification response when evidence is insufficient.
- [ ] Add regression tests for current mock/deepseek request shape.

## 3. Backend Implementation

- [ ] Add `TopicAnalysis` schema.
- [ ] Add `SourceDocument` schema.
- [ ] Add `SourceProvider` interface.
- [ ] Add mock source provider for local tests.
- [ ] Add source-aware quiz generation prompt.
- [ ] Extend quiz response parsing with optional source metadata.
- [ ] Add grounding validation.
- [ ] Record generation source metadata in existing store/log path.

## 4. Frontend Implementation

- [ ] Extend `generateQuiz` request with `sourceMode`.
- [ ] Add loading copy: “水母正在查找可靠资料”.
- [ ] Add clarification UI state on create page.
- [ ] Keep existing quiz page compatible with old question shape.
- [ ] Optionally show source chips in report page.

## 5. Documentation

- [ ] Update `docs/product-requirement-analysis.md` with fresh-knowledge generation requirement.
- [ ] Update `docs/solution-design.md` with source-aware generation architecture.
- [ ] Update README environment notes if external search provider is introduced.

## 6. Verification

- [ ] Run backend pytest.
- [ ] Run Taro build.
- [ ] Manually verify `Harness Engineering` no longer silently generates wrong-domain questions.
