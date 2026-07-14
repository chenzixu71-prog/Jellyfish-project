# Personal Knowledge Loop Exploration

## 1. Executive Summary

- **Goal:** 将用户自己的资料可靠地沉淀为知识库，并形成可补充、可闯关、可继续的个人学习闭环。
- **Finding:** 后端已有知识库和素材上传骨架，但前端没有真正上传图片，长中文分块、来源追踪、手工补题和上次知识库恢复仍缺失。
- **Recommended Change:** 先接通真实素材上传与解析状态，再增加手工题和当前知识库状态，最后把首页知识库点击改成直接进入闯关。
- **Rationale:** 现有页面数量已经足够；继续加页面不会修复“题目通用”和“下次无法继续”的根因。
- **Terms:** multipart = 同时传文字和文件的上传方式；知识块 = 从文档中切出的可检索小段；溯源 = 能知道题目依据哪份资料。
- **Change:** 用户上传的真实内容会成为题目依据，补充后可重新闯关，重新登录仍能继续上次知识库。
- **Risk:** 高，因为涉及资料解析、账号归属和持久化，错误会造成错误题目或数据丢失。
- **Done when:** 真实资料、手工题、点击即闯关和跨登录恢复都有自动化及微信开发者工具证据。
- **Open questions needing input:** 本轮 P0 是否接受先用进程内存验证、手机号短信供应商何时接入。

## Symbol Legend

`->` depends-on; `+` add; `~` extend; `=` reuse; `[F]` feature; `[BLOCK]` required decision; `[GAP]` unverified gap.

## 2. Meta

```text
kind: [F]
slug: personal-knowledge-loop
yyyymm: 202607
repo: Jellyfish-project
scope: frontend + FastAPI + storage + AI pipeline
one-liner: Make personal knowledge bases reliable and resumable
```

## 3. Evidence

- `frontend/src/pages/create/index.tsx:61-73` - files read locally; images become count text only.
- `frontend/src/pages/create/index.tsx:86-89` - creation uses JSON service then opens detail.
- `frontend/src/pages/create/index.tsx:146-149` - knowledge-base click opens detail, not quiz.
- `frontend/src/pages/knowledge-base/index.tsx:81-97` - supplements repeat local text/count behavior.
- `frontend/src/pages/knowledge-base/index.tsx:124-130` - detail page starts quiz and stores currentQuiz.
- `backend/app/routes.py:172-196` - reusable multipart create endpoint exists.
- `backend/app/routes.py:231-255` - reusable multipart supplement endpoint exists.
- `backend/app/services/asset_parser.py:8-11` - 3 files/10 images; text-only extensions.
- `backend/app/services/asset_parser.py:76-110` - OCR failures silently become placeholder content.
- `backend/app/services/knowledge_base_service.py:19-23` - 12k content cap and retrieval constants.
- `backend/app/services/knowledge_base_service.py:128-157` - knowledge chunks generate quiz and link quizId.
- `backend/app/services/knowledge_base_service.py:225-266` - whitespace word chunker; poor fit for long Chinese.
- `backend/app/schemas.py:21-29` - question model has no evidence/source field.
- `backend/app/schemas.py:118-154` - knowledge base has material/chunk/quiz IDs, no manual questions.
- `backend/app/storage/memory_store.py:146-154` - guest knowledge bases merge up to five.
- `backend/app/config.py:29-30` - default storage is memory; MySQL optional.
- `frontend/src/pages/quiz/index.tsx:36-46` - new quiz always resets to question one.
- `backend/app/routes.py:78-86` - invalid auth silently falls back to sessionId.
- `backend/app/routes.py:258-266` - full Quiz response exposes Question answers.

## 4. Domain & Data

```text
static source only; no live database connected.
existing KnowledgeBase: id/title/summary/content/materials/chunks/sourceMeta/quizIds
  S: backend/app/schemas.py:144-154
existing StoreRecord: namespace/owner_id/item_id/payload/created_at/updated_at
  S: backend/app/storage/sql_store.py:41-49
proposed: KnowledgeBase.manualQuestions[], Material.parseStatus/source metadata,
  UserLearningState.activeKnowledgeBaseId
relations: owner_id -> KnowledgeBase[]; KnowledgeBase.id -> Quiz[] via quizIds
[GAP] MySQL uses generic JSON records, not normalized relational tables.
```

## 5B. Pattern & Fit

```text
belongs in: routes -> knowledge_base_service -> current store
analogous: backend/app/routes.py:160-266
contracts:
  POST /api/knowledge-bases/from-assets = extend existing
  POST /api/knowledge-bases/{id}/supplements/from-assets = extend existing
  POST /api/knowledge-bases/{id}/manual-questions = new
  PUT /api/me/active-knowledge-base = new
  GET /api/me/learning-state = new
deviation: upload response returns per-asset parse status, not only counts.
```

## 6. Reuse Inventory

```text
= backend/app/services/asset_parser.py:22 parse_learning_assets
~ backend/app/services/knowledge_base_service.py:26 create_knowledge_base
~ backend/app/services/knowledge_base_service.py:80 supplement_knowledge_base
= backend/app/services/knowledge_base_service.py:128 start_quiz_from_knowledge_base
= backend/app/storage/memory_store.py:99 merge_guest_session_into_user
= frontend/src/services/quizService.ts:132 request envelope/auth header
+ manual-question DTO: searched schemas/question/knowledge; no matching ownership semantics
+ learning-state methods: searched active/last/current knowledge; no implementation
```

## 7. Proposed Changes

```text
1 frontend knowledge service/pages  ~ use multipart endpoints and upload binaries
2 asset_parser + schemas            ~ explicit parse results; PDF/DOCX/image validation
3 knowledge_base_service            ~ Chinese-aware chunks; no silent truncation/fake OCR text
4 schemas/store/routes              + manual questions and learning state
5 create page                       ~ card main click starts quiz; management opens detail
6 auth merge                        ~ migrate active knowledge selection and report conflicts
7 public quiz contract              + hide answers until submission
8 store writes                      ~ version checks for concurrent supplements/quizzes
9 tests                             + unit/API/frontend interaction coverage
```

## 8. Blast Radius

```text
callers: create page, knowledge-base page, knowledge service, routes, KB service, both stores
shared state: memory dictionaries; jelly_store_records JSON payloads; Taro storage
config: OCR/PDF/DOCX dependencies; SMS provider remains separate auth capability
risk: old KnowledgeBase JSON must validate with defaults after schema extension.
```

## 9. Test Plan

```text
add backend/tests/test_asset_parser.py: format/size/bad image/OCR/Chinese parsing
edit backend/tests/test_knowledge_base_service.py: chunks/dedupe/manual question inclusion
edit backend/tests/test_api.py: multipart create/supplement/active selection/guest merge
add frontend interaction tests: direct quiz/manage/restore selection
manual: WeChat DevTools upload -> parse -> add question -> quiz -> reopen/login -> continue
regression: text create, web search, guest migration, report, wrong book
```

## 10. Open Questions

```text
[BLOCK] confirm P0-A..P0-F before source edits
[BLOCK] real phone verification requires SMS provider and approved template
[INFO] memory can prove interaction but cannot satisfy restart persistence
[GAP] no live MySQL schema evidence; static generic StoreRecord only
```

## 11. Rollback

```text
code: atomic commits per capability
db: additive JSON fields with defaults; no destructive migration in first slice
data: keep original uploads out of destructive transforms
flag: direct-start behavior and manual-question mix default off until verified
```

## 12. Exploration Steps & Reasoning

```text
agents:
  product scope=user loop/priorities conclusion=P0 reliable resumable loop
  ai scope=parse/retrieve/generate conclusion=source/evidence quality blocks trust
  dev scope=contracts/storage/tests conclusion=reuse upload/quiz skeleton
reasoning:
  R1 "knowledge base complete" rejected: image count only (create/index.tsx:72)
  R2 "new upload API needed" rejected: routes.py:172-255 already exists
  R3 "direct quiz is UI-only" rejected: active selection and ownership must persist
  final: source reliability first, then manual questions and resume state
search: rg knowledge/upload/quiz/auth; line reads routes/schemas/parser/KB/pages/stores
live DB skipped: no confirmed non-production connection
```

## 13. Repro Header

```text
kind=F slug=personal-knowledge-loop yyyymm=202607
scope=frontend+FastAPI+storage+AI touches=knowledge-base,user-learning-state risk=high
next=awaiting-user-approval
```
