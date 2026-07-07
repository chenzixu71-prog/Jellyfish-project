## 1. Executive Summary

- **Goal:** Add a user knowledge base flow: users can search online, upload files or images, create up to 5 knowledge bases, supplement them later, and start quiz challenges from a selected knowledge base.
- **Finding:** The current app already has the core raw materials: owner resolution for guest/login users, AI quiz generation, Tavily source metadata, asset parsing, report/wrong-question/profile history, and a WeChat-style home UI. What is missing is a first-class "knowledge base" data object and UI flow.
- **Recommended Change:** Build the first version as a small knowledge-base module that reuses existing parsing/search/quiz/report services. Put creation and list entry on the home page; add a detail screen for supplementing and starting challenges.
- **Rationale:** Reusing the existing quiz pipeline keeps the change smaller and makes it immediately testable in WeChat DevTools. A separate knowledge-base entity is still needed because a one-off quiz cannot represent reusable saved learning material.
- **Terms:** knowledge base = a saved learning topic with extracted content and sources; source metadata = titles, URLs, summaries, and warnings from online search; owner id = the guest session or logged-in user id that owns learning data.
- **Change:** Users will first build/select a knowledge base, then generate a quiz from it, instead of every quiz being only a one-time prompt.
- **Risk:** Medium, because the feature touches backend data shape, upload behavior, home UI, and quiz navigation; risk stays manageable if delivered in small batches.
- **Done when:** In WeChat DevTools, a user can create a knowledge base from text/search/upload, see it in a max-5 list, supplement it, start a quiz from it, and get a report that keeps sources visible.
- **Open questions needing input:** Whether first version must persist to MySQL immediately, or whether the current in-memory MVP is acceptable for fast experience before MySQL migration.

## 2. Meta

```text
kind: [F]
slug: knowledge-base-mvp
yyyymm: 202607
repo: Jellyfish-project / 02-Python全栈AI刷题学习小程序
scope: backend/app + frontend/src
one-liner: add reusable knowledge bases
```

## 3. Evidence

```text
backend/app/routes.py:68      owner resolver: auth user -> user.id else session_id
backend/app/routes.py:122     POST /api/generate-quiz creates one-off quiz
backend/app/routes.py:129     POST /api/generate-quiz-from-assets accepts text/files/images
backend/app/routes.py:138     uploaded assets parsed before quiz creation
backend/app/routes.py:150     POST /api/submit-answer consumes quizId/questionId
backend/app/routes.py:162     POST /api/generate-report consumes quizId
backend/app/routes.py:207     GET /api/daily-challenge existing home support endpoint
backend/app/routes.py:213     GET /api/profile existing learning profile endpoint
backend/app/schemas.py:39     SourceMeta already models search tool/source visibility
backend/app/schemas.py:92     Quiz response includes sourceMeta
backend/app/schemas.py:132    Report response includes sourceMeta
backend/app/services/asset_parser.py:8   upload limits already 3 files
backend/app/services/asset_parser.py:9   upload limits already 10 images
backend/app/services/asset_parser.py:22  parse_learning_assets returns content/file_count/image_count/notes
backend/app/services/asset_parser.py:76  image parser supports optional OCR fallback
backend/app/services/quiz_service.py:22  create_quiz builds source_context -> generate_quiz -> save_quiz
backend/app/services/quiz_service.py:38  build_source_meta maps search docs for UI
backend/app/services/quiz_service.py:99  generate_report reads saved quiz + answers
backend/app/storage/memory_store.py:20   quizzes stored globally by quizId
backend/app/storage/memory_store.py:21   answers keyed by owner + quizId
backend/app/storage/memory_store.py:23   reports keyed by owner
backend/app/storage/memory_store.py:97   guest session merge copies answers/wrong/reports/profile
backend/app/storage/memory_store.py:177  save_quiz persists quiz and initializes answers
frontend/src/app.config.ts:2    current pages: create/quiz/report/wrong/profile
frontend/src/app.config.ts:16   current tabBar already has 5 tabs
frontend/src/pages/create/index.tsx:35   chooseMessageFile local file selection
frontend/src/pages/create/index.tsx:51   chooseImage local image selection
frontend/src/pages/create/index.tsx:64   current frontend builds learning content locally
frontend/src/pages/create/index.tsx:77   current image handling only records count
frontend/src/pages/create/index.tsx:83   current generate action creates quiz directly
frontend/src/pages/create/index.tsx:183  existing web search switch
frontend/src/services/quizService.ts:129 request wrapper adds auth header
frontend/src/services/quizService.ts:175 generateQuiz calls POST /api/generate-quiz
```

## 4. Domain & Data

```text
tables:
  none currently: backend uses MemoryStore dictionaries, not DB tables. S:backend/app/storage/memory_store.py:18

current in-memory stores:
  quizzes           dict[str, Quiz]                         S:backend/app/storage/memory_store.py:20
  answers           dict[(owner_id, quiz_id), AnswerResult] S:backend/app/storage/memory_store.py:21
  wrong_questions   dict[owner_id, WrongQuestion[]]         S:backend/app/storage/memory_store.py:22
  reports           dict[owner_id, Report[]]                S:backend/app/storage/memory_store.py:23
  profile_stats     dict[owner_id, stats]                   S:backend/app/storage/memory_store.py:25
  auth_sessions     dict[token_hash, session]               S:backend/app/storage/memory_store.py:27

new in-memory store proposed for MVP:
  knowledge_bases   dict[owner_id, KnowledgeBase[]]         NEW

future MySQL tables recommended:
  knowledge_base:
    id              VARCHAR/CHAR PK
    owner_id        VARCHAR IX
    title           VARCHAR
    summary         TEXT
    content         MEDIUMTEXT
    source_meta     JSON
    item_count      INT
    created_at      DATETIME
    updated_at      DATETIME
    deleted_at      DATETIME NULL
  knowledge_base_material:
    id              VARCHAR/CHAR PK
    kb_id           FK -> knowledge_base.id IX
    type            ENUM(text,file,image,url,search)
    name            VARCHAR
    content         MEDIUMTEXT
    note            TEXT
    created_at      DATETIME
  knowledge_base_quiz:
    kb_id           FK -> knowledge_base.id IX
    quiz_id         FK/logical -> quiz.quizId
    created_at      DATETIME

rels:
  owner_id -> guest session id or user id        S:backend/app/routes.py:68-76
  quizId -> answers/reports/wrong_questions      S:backend/app/services/quiz_service.py:56-128
  knowledge_base.id -> generated quiz content    NEW, reuse create_quiz

cardinality:
  max knowledge bases per owner = 5              PM request
  max files per creation/supplement = 3          S:backend/app/services/asset_parser.py:8
  max images per creation/supplement = 10        S:backend/app/services/asset_parser.py:9

mismatches:
  current frontend upload is local prompt composition, not backend multipart upload. S:frontend/src/pages/create/index.tsx:64-80 vs S:backend/app/routes.py:129-147
```

## 5B. Pattern & Fit

```text
belongs in:
  backend/app/schemas.py        add DTOs near Quiz/Report          analogous: backend/app/schemas.py:92
  backend/app/services          add knowledge_base_service.py      analogous: backend/app/services/quiz_service.py:22
  backend/app/storage           extend MemoryStore                 analogous: backend/app/storage/memory_store.py:177
  backend/app/routes.py         add /api/knowledge-bases endpoints analogous: backend/app/routes.py:122
  frontend/src/services         extend quizService or add kb svc   analogous: frontend/src/services/quizService.ts:129
  frontend/src/pages/create     home creation/list UI              analogous: frontend/src/pages/create/index.tsx:117
  frontend/src/pages/kb-detail  new detail/supplement/start page   new route needed

model after:
  ctrl   backend/app/routes.py:122-147
  svc    backend/app/services/quiz_service.py:22-35
  data   backend/app/storage/memory_store.py:177-182
  dto    backend/app/schemas.py:92-97
  ui     frontend/src/pages/create/index.tsx:169-196

contract:
  POST /api/knowledge-bases
    req: multipart/form-data {sessionId, title?, content, webSearchEnabled, files[], images[]}
    resp: KnowledgeBase
  GET /api/knowledge-bases?sessionId=
    resp: KnowledgeBaseSummary[]
  GET /api/knowledge-bases/{id}?sessionId=
    resp: KnowledgeBase
  POST /api/knowledge-bases/{id}/supplements
    req: multipart/form-data {sessionId, content, webSearchEnabled, files[], images[]}
    resp: KnowledgeBase
  POST /api/knowledge-bases/{id}/quiz
    req: {sessionId}
    resp: Quiz

deviation from analogue:
  - create_quiz returns one quiz; knowledge_base stores reusable content before quiz generation. risk=med
  - current frontend upload does not hit multipart endpoint. risk=med
  - current tabBar already has 5 tabs; avoid adding a 6th tab. risk=low
```

## 6. Reuse Inventory

```text
utils:
  reuse backend/app/services/asset_parser.py:22 parse_learning_assets for creation/supplement upload
  reuse backend/app/services/quiz_service.py:22 create_quiz for start-challenge
  reuse backend/app/services/quiz_service.py:38 build_source_meta for source cards
  reuse backend/app/routes.py:68 resolve_learning_owner for guest/login ownership

dtos:
  extend backend/app/schemas.py:39 SourceMeta for KB source provenance
  new backend/app/schemas.py KnowledgeBase/KnowledgeBaseSummary/KnowledgeBaseSupplementRequest
    searched: Quiz, Report, WrongQuestion, SourceMeta
    no fit: existing Quiz is question set, not reusable knowledge material

svc/repo:
  extend backend/app/storage/memory_store.py with save/list/get/update KB
  new backend/app/services/knowledge_base_service.py
    why not quiz_service-only: quiz_service owns answering/reporting and should not own reusable material lifecycle

clients:
  reuse frontend/src/services/quizService.ts:129 request auth/session pattern
  new upload helper needed for multipart because Taro.request JSON wrapper cannot send files

config/consts:
  reuse asset limits from backend/app/services/asset_parser.py:8-10
  add MAX_KNOWLEDGE_BASES_PER_OWNER = 5 in service/storage layer
```

## 7. Proposed Changes

```text
P0 backend data + API
1 backend/app/schemas.py                         add KnowledgeBase DTOs              reuse SourceMeta
2 backend/app/storage/memory_store.py            add KB store methods                reuse owner keyed pattern
3 backend/app/services/knowledge_base_service.py add create/list/get/supplement/start reuse asset_parser + create_quiz
4 backend/app/routes.py                          add /api/knowledge-bases endpoints  reuse ok + resolve_learning_owner
5 backend/tests/test_api.py                      add KB API tests                    reuse TestClient patterns

P1 frontend experience
6 frontend/src/services/knowledgeBaseService.ts  add JSON + upload functions         reuse auth/session conventions
7 frontend/src/app.config.ts                     add pages/knowledge-base/index route, no new tab
8 frontend/src/pages/create/index.tsx/css        home: create KB + max-5 list        reuse visual style
9 frontend/src/pages/knowledge-base/index.tsx/css detail: source/material/supplement/start challenge
10 frontend/src/pages/quiz/index.tsx             display KB origin if available      optional

P2 WeChat DevTools usability gate
11 build frontend/dist with npm.cmd run build:weapp
12 restart/check backend /health
13 manual check: create KB -> supplement -> start quiz -> answer -> report

P3 persistence hardening
14 add MySQL schema + repository when user confirms DB setup
15 migrate MemoryStore methods behind repository interface
```

## 8. Blast Radius

```text
callers of changed symbols:
  backend/app/routes.py:122       generate_quiz must remain compatible
  backend/app/routes.py:129       generate_quiz_from_assets must remain compatible
  backend/app/services/quiz_service.py:22 create_quiz reused by KB start quiz
  backend/app/storage/memory_store.py:97 guest merge does not yet copy KB unless extended
  frontend/src/pages/create/index.tsx:83 current one-click generate flow will change UX
  frontend/src/services/quizService.ts:175 current generateQuiz should remain for direct quiz fallback
  frontend/src/app.config.ts:16 tabBar should stay at 5 tabs

shared state:
  db tables: none current; future knowledge_base, knowledge_base_material, knowledge_base_quiz
  redis keys: none
  kafka topics: none
  feature flags: optional enableKnowledgeBase default true for local MVP
  cache ns: Taro storage currentQuiz remains

cross-service:
  external search: Tavily via existing source_context path
  external AI: DeepSeek via existing generate_quiz path
  sso/session: auth token fallback to session id via routes.py:68

config/migration:
  new prop optional: MAX_KNOWLEDGE_BASES=5
  ddl: not in P0 unless MySQL-first confirmed
```

## 9. Test Plan

```text
add:
  backend/tests/test_api.py
    - create KB from text with webSearchEnabled false
    - create KB with webSearchEnabled true returns sourceMeta shape
    - reject 6th KB for same owner
    - supplement KB updates content/source/material count
    - start quiz from KB returns 5 questions and stores current quiz
    - auth owner and guest owner separated
    - login merge copies KB if implemented in P0

manual:
  1 open backend /health
  2 run frontend build:weapp
  3 WeChat DevTools compile from frontend project
  4 home create KB from text + search switch
  5 home list shows KB card
  6 KB detail supplement text/file/image
  7 start challenge -> quiz page
  8 finish quiz -> report includes source

regression focus:
  generate_quiz, generate_quiz_from_assets, submit_answer, generate_report, profile, report-history
```

## 10. Open Questions

```text
[BLOCK] Should P0 persist knowledge bases in MySQL immediately, or is in-memory MVP acceptable for first playable WeChat DevTools version? need from: P:PM
[INFO] Should one knowledge base generate exactly one active quiz at a time or unlimited quizzes? assumption: unlimited quiz sessions, reports keep quizId.
[INFO] Should supplement overwrite summary/title automatically? assumption: append content, recompute summary lightly, preserve user title.
[GAP] Frontend true multi-file upload needs a helper beyond current Taro.request JSON wrapper. see frontend/src/services/quizService.ts:129
```

## 11. Rollback

```text
code: revert feature commit
db: none for in-memory P0; if MySQL added, down migration needed
data: in-memory KB lost on backend restart unless MySQL implemented
flag: recommended y; name=enableKnowledgeBase; default=true in local MVP, false if MySQL required
```

## 12. Exploration Steps & Reasoning

```text
agents:
  main scope=classification+synthesis
    steps=read PM request, read requirement/UI/explore skills, grep backend routes/schemas/storage/services, grep frontend pages/services/app config
    evidence=backend/app/routes.py:122, backend/app/routes.py:129, backend/app/services/asset_parser.py:22, frontend/src/pages/create/index.tsx:64
    conclusion=feature fits as KB module reusing existing quiz/search/upload services
  subagent status=not spawned
    reason=current tool policy requires explicit subagent/delegation authorization; no user request for subagents

reasoning:
  R1 "directly extend Quiz as KB" rejected because Quiz is question set. evidence=backend/app/schemas.py:92-97
  R2 "reuse create_quiz for KB challenge" kept because create_quiz already handles source_context, AI generation, store.save_quiz. evidence=backend/app/services/quiz_service.py:22-35
  R3 "reuse asset parser" kept because limits and OCR/text parsing already exist. evidence=backend/app/services/asset_parser.py:22-53
  R4 "add new tab" rejected because tabBar already has 5 pages and user wants home entry. evidence=frontend/src/app.config.ts:16-53
  R5 "backend multipart already enough for frontend" rejected because current frontend only uses JSON generateQuiz and local text composition. evidence=frontend/src/pages/create/index.tsx:64-101, frontend/src/services/quizService.ts:175-183
  final feature-fit conclusion=add KnowledgeBase lifecycle + reuse existing quiz/search/upload path

terms:
  owner id = stable id used to save data under guest session or logged-in user
  multipart = request format used to upload files/images plus normal text fields
  source metadata = visible record of online search/extract sources used by AI

search trail:
  rg "generate-quiz|generate-quiz-from-assets|profile|sourceMeta" backend/app backend/tests
  rg "chooseFiles|chooseImages|webSearch|generateQuiz|tabBar" frontend/src
  rg "save_quiz|get_quiz|reports|profile_stats|merge" backend/app/storage/memory_store.py
```

## 13. Repro Header for Follow-up Sessions

```text
kind=F slug=knowledge-base-mvp yyyymm=202607
scope=backend/app + frontend/src touches=MemoryStore knowledge_bases risk=med
next=awaiting-user-approval
```
