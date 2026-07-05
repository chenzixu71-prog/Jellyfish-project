# 水母diy学习助手

## 项目目标

做一个用于 AI 辅助学习和刷题的小程序项目。用户可以输入自己想学的知识，系统把它 DIY 成互动闯关题，并在答题后给出即时讲解和复盘报告。

## 技术栈

- 后端：Python 3.11+，FastAPI 或 Flask
- 前端：微信小程序
- 数据库：MySQL 或 PostgreSQL
- 缓存：Redis（可选）
- AI：大模型 API，用于生成题目、解释答案和优化错题

## 目录结构

```text
backend/       Python 后端
miniprogram/   微信小程序前端
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
http://127.0.0.1:8000/api/levels
http://127.0.0.1:8000/api/questions?levelId=level-1
```

### 小程序前端

使用微信开发者工具导入：

```text
miniprogram/
```

当前页面：

- `pages/levels`：关卡页
- `pages/quiz`：答题页
- `pages/result`：结果页
- `pages/profile`：个人中心页

## 部署步骤

后续补充部署平台、环境变量、数据库和小程序发布步骤。

## 配置说明

真实密钥只能放在本地 `.env` 或部署平台 Secrets 中，不能提交到 GitHub。

需要准备的配置：

- `DATABASE_URL`
- `REDIS_URL`
- `AI_API_KEY`
- `AI_BASE_URL`
- `AI_MODEL`

## 当前阶段

Day 02 目标：跑通 Python 后端和微信小程序前端骨架，确认接口请求链路，并沉淀“水母diy学习助手”的需求分析。

## 产品文档

- [需求分析](docs/product-requirement-analysis.md)
- [竞品与产品决策简报](docs/competitive-decision-brief.md)
- [PRD AI-native 草稿](docs/prd-ai-native-draft.md)
- [方案设计文档](docs/solution-design.md)
