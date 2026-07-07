# Backend

这是“水母diy学习助手”的 Python FastAPI 后端。

当前阶段先使用 mock AI 跑通核心闭环：

```text
生成题目 -> 提交答案 -> 生成报告
```

默认配置是 `AI_PROVIDER=mock`，不会请求真实大模型。

## 目录说明

- `app/main.py`：FastAPI 应用入口。
- `app/routes.py`：接口路由。
- `app/config.py`：端口和 AI 配置。
- `app/schemas.py`：Pydantic 请求/响应模型。
- `app/services/`：业务逻辑和 mock AI。
- `app/storage/`：MVP 内存存储。
- `tests/`：pytest 接口测试。
- `requirements.txt`：Python 依赖清单。

## 本地启动

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m app.main
```

启动后访问：

```text
http://127.0.0.1:8010/health
http://127.0.0.1:8010/api/levels
http://127.0.0.1:8010/api/questions?levelId=level-1
```

核心接口：

```text
POST /api/generate-quiz
POST /api/generate-quiz-from-assets
POST /api/submit-answer
POST /api/generate-report
```

## 上传素材出题

`POST /api/generate-quiz-from-assets` 使用 `multipart/form-data`：

- `sessionId`：必填，会话 ID。
- `content`：可选，用户补充的文字说明。
- `files`：最多 3 个，当前支持 `.txt`、`.md`、`.csv`、`.json`，单个文件不超过 2MB。
- `images`：最多 10 张，当前会完成接收和数量校验。

当前 DeepSeek 官方 API 模型列表为 `deepseek-v4-flash` / `deepseek-v4-pro`，官方文档列出的能力是文本 Chat Completions、JSON Output、Tool Calls 等，没有图片输入能力。因此第一版使用 `deepseek-v4-flash` 处理解析出的文本内容；图片会作为素材清单记录。若要识别图片里的文字，需要后续接入 OCR 或视觉模型。

## DeepSeek 配置

复制 `.env.example` 为 `.env`，并填入本地密钥：

```text
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的本地 key
DEEPSEEK_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-v4-flash
AI_REPORT_MODEL=deepseek-v4-pro
```

注意：

- `.env` 已被 Git 忽略，不能提交。
- 小程序前端不能直接调用 DeepSeek，必须通过后端接口。
- 没有 `.env` 时，后端会继续使用 mock AI，方便开发和测试。

## Tavily 搜索配置

如果要启用联网搜索和网页抽取，只把真实 Tavily Key 写入本地 `backend/.env` 或部署平台 Secrets，不要写入代码、README 或 `.env.example`：

```text
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=你的本地 Tavily key
SEARCH_MAX_RESULTS=5
SEARCH_DEPTH=basic
EXTRACT_DEPTH=basic
TAVILY_TIMEOUT_SECONDS=8
```

`.env.example` 只保留空值模板，用于提示需要哪些环境变量。

## 运行测试

```powershell
cd backend
.venv\Scripts\python.exe -m pytest -q
```

当前验收：

```text
5 passed
```

## Source-aware quiz generation

Current backend supports source-aware generation behind `webSearchEnabled`:

- `POST /api/generate-quiz` accepts JSON field `webSearchEnabled`.
- `POST /api/generate-quiz-from-assets` accepts form field `webSearchEnabled`.
- When `webSearchEnabled=false`, the backend keeps the existing mock/DeepSeek flow.
- When `webSearchEnabled=true` and `SEARCH_PROVIDER=tavily`, the backend uses Tavily search/extract context before calling DeepSeek.
- If Tavily is missing, times out, or fails, quiz generation degrades to empty source context and continues.

Uploaded assets:

- Text files: `.txt`, `.md`, `.csv`, `.json`, up to 3 files and 2MB each.
- Images: up to 10 images and 2MB each.
- Image OCR is optional. If `Pillow`, `pytesseract`, and the local Tesseract binary are available, image text is extracted. Otherwise the backend records image metadata and continues.
