# 04-AI零代码应用生成平台

## 项目目标

做一个 AI 零代码应用生成平台，覆盖用户输入需求、AI 规划、文件生成、预览、构建日志、自动修复和模型配置等核心流程。

## 技术栈

- 后端：Java 17/21，Spring Boot，LangChain4j
- 前端：Vue，Ant Design
- 数据库：MySQL 或 PostgreSQL
- 构建与预览：Node.js LTS，npm
- AI：大模型 API，用于应用规划、代码生成和错误修复

## 启动步骤

后续补充实际命令。

```bash
# backend
# mvn clean install
# mvn spring-boot:run

# frontend
# npm install
# npm run dev
# npm run build
```

## 部署步骤

后续补充前端、后端、数据库、生成文件目录和环境变量说明。

## 配置说明

真实密钥只能放在本地 `.env`、`application-local.yml` 或部署平台 Secrets 中，不能提交到 GitHub。

需要准备的配置：

- `DATABASE_URL`
- `AI_API_KEY`
- `AI_BASE_URL`
- `AI_MODEL`
- `GENERATED_WORKSPACE_DIR`

## 当前阶段

Day 01 目标：建立项目目录、README、`.gitignore`、`docs/` 和 `screenshots/`，完成第一次提交。

