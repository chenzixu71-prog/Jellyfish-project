# 水母diy学习助手

## 项目目标

做一个用于 AI 辅助学习和刷题的小程序项目。用户可以输入自己想学的知识，系统把它 DIY 成互动闯关题，并在答题后给出即时讲解和复盘报告。

## 技术栈

- 后端：Python 3.11+，FastAPI
- 前端：Taro 4.x + React + TypeScript，第一版只编译微信小程序
- 数据库：MVP 暂不接入，先用内存存储跑通核心链路
- 缓存：MVP 暂不接入 Redis
- AI：默认 mock，本地配置后可切换 DeepSeek API

## 目录结构

```text
backend/       Python 后端
frontend/      Taro 微信小程序前端
docs/          项目文档
screenshots/   截图和接口验证记录
```

## 启动步骤

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m app.main
```

启动后访问：

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/api/generate-quiz
http://127.0.0.1:8000/api/generate-report
```

### 小程序前端

```bash
cd frontend
npm install
npm run build:weapp
```

使用微信开发者工具导入构建产物：

```text
frontend/dist/
```

当前页面：

- `pages/create`：输入学习内容并生成题目
- `pages/quiz`：答题闯关、即时讲解、通关庆祝动效
- `pages/report`：生成并展示学习报告，支持微信分享入口
- `pages/profile`：查看本地学习报告记录

## 部署步骤

后续补充部署平台、环境变量、小程序合法域名、数据库和小程序发布步骤。

## 配置说明

真实密钥只能放在本地 `.env` 或部署平台 Secrets 中，不能提交到 GitHub。

后端默认使用 mock，不会请求真实大模型。如果要切换 DeepSeek，在 `backend/.env` 中配置：

```text
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的本地 key
DEEPSEEK_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-v4-flash
AI_REPORT_MODEL=deepseek-v4-pro
```

注意：`.env` 已被 Git 忽略，不要把真实 key 写入 README、代码或提交记录。

## 当前阶段

当前已完成 MVP 核心功能的第一版开发：

1. 用户输入知识文本。
2. 后端生成 5 道题。
3. 小程序前端完成答题闯关。
4. 答题结束出现彩带庆祝动效。
5. 用户点击查看报告，后端生成学习复盘报告。
6. 报告页提供微信分享入口和 QQ 分享占位入口。

## 产品文档

- [需求分析](docs/product-requirement-analysis.md)
- [竞品与产品决策简报](docs/competitive-decision-brief.md)
- [PRD AI-native 草稿](docs/prd-ai-native-draft.md)
- [方案设计文档](docs/solution-design.md)
