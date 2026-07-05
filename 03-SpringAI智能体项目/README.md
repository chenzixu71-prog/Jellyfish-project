# 03-SpringAI智能体项目

## 项目目标

做一个 Spring AI 智能体项目，覆盖普通对话、RAG、PgVector、Tool Calling、MCP、ReAct Agent、SSE 流式输出和本地模型接入。

## 技术栈

- 后端：Java 17/21，Spring Boot，Spring AI
- 构建：Maven
- 数据库：PostgreSQL + PgVector
- 缓存：Redis（可选）
- AI：大模型 API 或 Ollama

## 启动步骤

后续补充实际命令。

```bash
# mvn clean install
# mvn spring-boot:run
```

## 部署步骤

后续补充 Docker、数据库、环境变量和部署平台说明。

## 配置说明

真实密钥只能放在本地 `.env`、`application-local.yml` 或部署平台 Secrets 中，不能提交到 GitHub。

需要准备的配置：

- `spring.datasource.url`
- `spring.datasource.username`
- `spring.datasource.password`
- `spring.ai.openai.api-key`
- `spring.ai.openai.base-url`
- `spring.ai.openai.chat.options.model`

## 当前阶段

Day 01 目标：建立项目目录、README、`.gitignore`、`docs/` 和 `screenshots/`，完成第一次提交。

