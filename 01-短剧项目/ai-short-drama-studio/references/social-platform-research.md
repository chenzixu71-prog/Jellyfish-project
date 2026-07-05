# Douyin and Xiaohongshu Research Method

Use this reference when collecting AI短剧 signals from Douyin, Xiaohongshu, or public search results.

## Access Levels

Public web search:
- Use search-engine snippets, public article pages, public video pages, platform landing pages, and official platform rules.
- Treat coverage as incomplete because Douyin and Xiaohongshu often hide full search results, comments, and feeds behind login or app flows.

Logged-in browser research:
- Ask the user to log in themselves. Do not ask for passwords or verification codes.
- Only search, open results, read visible content, and take screenshots if useful.
- Do not like, follow, comment, save, publish, private-message, edit account settings, buy anything, or export private user data.

## Logged-In Session Handoff

When the user provides logged-in entry URLs, use this sequence:

1. Ask the user to open the pages in the browser/profile controlled by Codex and confirm they are logged in.
2. Verify current tab URLs and page titles before searching.
3. Search one query at a time. Start with `AI短剧`, then branch only when results repeatedly mention a tool or pain point.
4. Capture a small, high-signal sample instead of scrolling endlessly:
   - 5-8 Xiaohongshu notes for tutorial/workflow/prompt signals.
   - 5-8 Douyin videos/search results for production stack, hook format, or tool usage.
5. For each useful sample, record the visible title, author if visible, URL, visible summary, tool chain, and concrete reusable method.
6. Stop immediately if the page asks for password, SMS code, payment, publishing permission, camera/microphone permission, or CAPTCHA confirmation. Ask the user to handle it.

Preferred entry URLs:
- Xiaohongshu: `https://www.xiaohongshu.com/explore`
- Douyin: `https://www.douyin.com/jingxuan`

Do not treat logged-in recommendation feeds as neutral market ranking. Feeds are personalized and should be labeled as account-specific samples.

## Search Queries

Start with:
- AI短剧
- AI短剧教程
- AI短剧 角色一致性
- AI短剧 可灵
- AI短剧 即梦
- AI短剧 剪映
- AI短剧 图生视频
- AI短剧 真人风
- AI短剧 提示词
- 红果短剧 AI

Expand by tool chain:
- 可灵 图生视频 角色一致性
- 即梦 人物一致性
- 海螺 视频生成 AI短剧
- 剪映 AI短剧 配音 字幕
- 数字人 短剧 真人风

## Capture Fields

For each sample, record:
- platform
- URL or screenshot path
- collection date
- author name if visible
- title/hook
- format: tutorial, case study, tool demo, monetization claim, prompt share, platform upload note, critique
- claimed workflow
- tools mentioned
- character consistency method
- expression/acting method
- voice/subtitle/edit method
- platform distribution method
- evidence strength: direct demo, screen recording, personal claim, reposted claim, comment signal
- useful pattern
- risk or counterevidence

Use this compact table during live research:

| platform | query | sample_url | title_or_hook | visible_claim | tools | consistency_method | expression_method | reusable_takeaway | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Pattern Extraction

Look for repeated signals across at least 5-10 samples before calling something a pattern:
- Hook formulas: revenge, identity reveal, betrayal, reversal, family conflict, workplace humiliation, supernatural reset.
- Production stack: script -> character bible -> reference images -> image-to-video -> TTS/dubbing -> subtitles -> editing -> platform QA.
- Pain points: identity drift, face changes, outfit changes, stiff acting, lip-sync mismatch, over-beautified face, slow pacing, compliance risk.
- Monetization claims: treat as low-confidence unless backed by platform dashboards or publisher records.

## Evidence Boundary

Do not write "Douyin users all..." or "Xiaohongshu proves..." from a small sample. Use:
- "Observed in this sample..."
- "Repeated across N sampled posts..."
- "Weak signal..."
- "Needs live validation..."

When research depends on login, include the date, platform account state, and query terms used.
