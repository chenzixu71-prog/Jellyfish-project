# 水母diy学习助手 - 方案设计文档

## 0. 文档目标

本文档用于指导“水母diy学习助手”从需求分析进入可执行开发。第一阶段不追求功能完整，而是先跑通核心业务闭环：

```text
用户输入内容 -> AI 生成题目 -> 用户答题 -> AI 生成分析报告
```

当前明确不优先做：

- 用户登录注册。
- 复杂数据库和账号体系。
- 充值 VIP。
- 多人 PK。
- 视频/文档/网页全量解析。
- RAG 知识库。

## 1. 输入资料理解

### 1.1 已确认需求

来自需求分析文档和 PM 输入：

- 产品命名为“水母diy学习助手”。
- 用户可以输入一个想学的知识，可以是一句话、一段话，未来可以扩展到文档、视频、网页。
- AI 自动整理知识并生成互动问答闯关题。
- 用户答题后立即获得正确答案和知识讲解。
- 通关后生成知识总结和复盘报告。
- 后续可扩展 RAG、AI 生图、VIP、多人 PK、排行榜、语音读题等能力。

### 1.2 本方案的关键取舍

第一版只做“最短可运行闭环”，原因是：

- 登录注册会引入微信登录、token、用户表、隐私合规和数据库依赖，会拖慢核心验证。
- 文档/视频/网页解析会引入内容抓取、版权、解析失败、格式兼容和成本问题。
- 排行榜、PK、VIP 是增长和商业化功能，不是用户第一次使用产品的核心价值。

第一版必须优先证明：

```text
用户给一段内容，系统能生成好题，用户答完后觉得讲解和复盘有帮助。
```

## 2. 总体技术方案

### 2.1 推荐架构

```text
Taro 4.x 小程序前端
  -> Python HTTP API 后端
    -> AI 模型服务
    -> 本地 JSON / SQLite 临时存储
```

第一阶段不用复杂中间件。

```text
不引入 Redis
不引入正式 MySQL/PostgreSQL
不引入登录态
不引入对象存储
不引入消息队列
```

### 2.2 分阶段架构演进

| 阶段 | 目标 | 前端 | 后端 | 存储 | AI |
| --- | --- | --- | --- | --- | --- |
| P0 工程骨架 | 能启动、能请求接口 | Taro 4.x + React + TypeScript | Python 标准库/轻量 HTTP | 无持久化或 JSON | mock 数据 |
| P1 核心闭环 | 输入、生成、答题、报告 | Taro 4.x + React + TypeScript | FastAPI | SQLite | 大模型 API |
| P2 可复盘 | 学习记录、错题、报告历史 | Taro 4.x + React + TypeScript | FastAPI | SQLite/MySQL | 题目生成 + 报告生成 |
| P3 增强版 | URL/文档解析、分享、勋章 | Taro 4.x，可扩展 H5/多端 | FastAPI | MySQL/PostgreSQL | AI + 搜索/解析 |
| P4 商业化 | 登录、VIP、额度、排行榜 | 小程序 + 管理后台 | FastAPI/Spring Boot | PostgreSQL/MySQL + Redis | 多模型路由 |

## 3. 小程序技术选型对比

小程序技术栈更新较快，第一版要优先考虑稳定、调试成本和微信生态兼容性。

### 3.1 候选方案

| 方案 | 技术形态 | 优点 | 缺点 | 适合本项目吗 |
| --- | --- | --- | --- | --- |
| Taro 4.x | React + TypeScript，编译到微信小程序等多端 | 开源、工程化好、组件化清晰、后续可扩展 H5/其他小程序；适合把复杂业务拆成页面、组件、service、store | 比原生多一层编译抽象，调试时要区分 Taro 层和微信小程序运行时问题 | 推荐用于 MVP 主线 |
| 原生微信小程序 | WXML + WXSS + JS | 官方能力最直接，调试链路短，微信组件/接口兼容最好，上手路径清晰 | 组件化和工程化弱于现代前端框架，多端复用差；后续页面多了维护成本高 | 仅作为学习占位或兜底方案 |
| uni-app | Vue 语法，多端发布 | Vue 使用门槛较低，多端生态成熟，HBuilderX 支持强 | 平台差异和编译层可能带来额外问题 | 如果目标多端，可以考虑 |
| 微信云开发 | 小程序 + 云函数 + 云数据库 | 少维护服务器，适合轻后端和快速上线 | AI 调用、复杂业务、供应商迁移会受平台约束 | 可做备选，不作为当前主线 |

### 3.2 推荐结论

MVP 推荐使用：

```text
Taro 4.x + React + TypeScript + Python FastAPI 后端
```

原因：

- 本项目后续页面会逐步增加：输入页、关卡页、答题页、结果页、报告页、个人中心页，Taro 的组件化和工程化更适合长期维护。
- Taro 4.x 可使用 React + TypeScript，把页面状态、接口请求、AI 生成流程拆得更清楚，利于后续交给 Codex 迭代。
- 现在已经安装 Node.js，具备 Taro 前端工程的基础环境。
- 当前虽然先做微信小程序，但后续如果要扩展 H5、其他小程序或运营页，Taro 比原生小程序迁移成本低。
- 第一版仍然严格收敛业务范围，只用 Taro 做工程框架，不提前做复杂状态管理、登录注册或多端适配。

### 3.3 Taro 4.x 使用边界

第一版 Taro 使用方式：

- 使用 React + TypeScript。
- 使用 Taro 官方 CLI 初始化前端工程。
- 只编译微信小程序端，不同时维护 H5/App。
- 不引入 Redux、MobX 等重状态管理，先用页面 state + service 层。
- 不引入复杂 UI 组件库，先用 Taro 基础组件和少量自定义样式。

建议初始化命令：

```bash
npx.cmd -y @tarojs/cli@latest init frontend
```

初始化时建议选择：

```text
框架：React
语言：TypeScript
CSS：Sass 或普通 CSS 均可，MVP 可先选 CSS
模板：默认模板
```

微信小程序开发命令以实际生成的 `package.json` 为准，通常会是：

```bash
npm.cmd install
npm.cmd run dev:weapp
```

构建产物导入微信开发者工具：

```text
frontend/dist
```

当前仓库里的 `miniprogram/` 是 Day 02 原生小程序学习骨架，后续正式实现核心闭环时应迁移为 `frontend/` Taro 工程。

### 3.4 参考依据

- Taro 官方定位是开放式跨端跨框架解决方案，可以用 React/Vue 等语法编译到多端。
- Taro 官方文档支持通过 `npx @tarojs/cli@latest init <projectName>` 初始化项目。
- Taro React 项目通过 `app.config` 管理页面、窗口和 tabBar 等小程序配置。
- 微信小程序官方提供原生框架、视图层、逻辑层、API 与开发者工具能力，Taro 最终仍需要编译到微信小程序运行时。
- uni-app 官方定位是使用 Vue 语法开发多端应用。
- 微信云开发官方提供云函数、数据库、存储等后端能力，但会带来云开发平台绑定。

参考链接：

- 微信小程序官方文档：https://developers.weixin.qq.com/miniprogram/dev/framework/
- 微信云开发官方文档：https://developers.weixin.qq.com/miniprogram/dev/wxcloud/basis/getting-started.html
- Taro 官方文档：https://docs.taro.zone/docs/
- uni-app 官方文档：https://uniapp.dcloud.net.cn/

## 4. 后端技术选型

### 4.1 候选方案

| 方案 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- |
| Python 标准库 HTTP | 零依赖，最适合 Day 02 骨架 | 不适合长期开发，路由、校验、文档弱 | 仅保留为学习骨架 |
| FastAPI | 类型清晰、接口文档自动生成、适合 AI API 编排 | 需要学习 Pydantic、异步概念 | 推荐 P1 使用 |
| Flask | 简单、资料多 | 接口类型和文档能力弱于 FastAPI | 可选，但不推荐 |
| Node.js/NestJS | 前后端语言统一，工程化强 | 对当前 Python AI 学习路线不匹配 | 暂不采用 |
| Spring Boot | 工程成熟，适合复杂系统 | 对项目 A 学习成本过高，项目 B/C 再用 | 不用于项目 A MVP |

### 4.2 推荐结论

P1 开始使用：

```text
Python 3.12 + FastAPI + Pydantic
```

原因：

- AI 调用、Prompt 编排、JSON 处理在 Python 生态更顺。
- FastAPI 天然适合 HTTP API。
- 后续接 SQLite/MySQL、文件上传、异步任务都比较自然。

## 5. AI 技术方案

### 5.1 AI 在第一版中的职责

AI 只做三件事：

1. 根据用户输入生成题目。
2. 根据用户答案生成即时讲解。
3. 根据答题结果生成复盘报告。

不要让 AI 直接决定：

- 用户身份。
- 支付权限。
- 排行榜结果。
- 数据库写入是否合法。

### 5.2 DeepSeek 模型策略

第一版确认使用 DeepSeek API，但小程序前端不能直接请求 DeepSeek。调用链必须是：

```text
Taro 微信小程序 -> Python FastAPI 后端 -> DeepSeek API
```

原因：

- DeepSeek API Key 属于真实密钥，不能放在小程序包里，否则用户可以反编译拿到。
- 后端可以统一做 prompt、JSON 校验、失败重试、额度控制和日志记录。
- 未来如果切换模型供应商，只需要改后端 `ai_service.py`，前端接口不变。

MVP 模型配置：

| 用途 | 默认模型 | 说明 |
| --- | --- | --- |
| 生成单选题 | `deepseek-v4-flash` | 默认使用，速度和成本更适合 MVP |
| 生成即时讲解 | `deepseek-v4-flash` | 单题讲解不需要复杂推理 |
| 生成复盘报告 | `deepseek-v4-flash` | 第一版报告先控制复杂度 |
| 高质量报告备选 | `deepseek-v4-pro` | 后台配置保留切换能力，不作为默认 |

配置原则：

- 默认模型写入环境变量 `AI_MODEL=deepseek-v4-flash`。
- 不在代码里写死模型名，统一从 `app/config.py` 读取。
- 预留 `AI_REPORT_MODEL=deepseek-v4-pro`，后续需要更高质量报告时再启用。
- `deepseek-chat`、`deepseek-reasoner` 作为旧模型名，不作为新项目绑定目标。

### 5.3 Prompt 输出格式

AI 生成题目时必须输出结构化 JSON：

```json
{
  "topic": "用户输入主题",
  "summary": "知识点摘要",
  "questions": [
    {
      "id": "q1",
      "type": "single_choice",
      "stem": "题干",
      "options": ["A", "B", "C", "D"],
      "answerIndex": 1,
      "explanation": "讲解",
      "knowledgePoint": "对应知识点"
    }
  ]
}
```

后端必须校验：

- `questions` 是否存在。
- 每题是否有 4 个选项。
- `answerIndex` 是否在合法范围。
- `explanation` 是否为空。

校验失败时不能直接保存，要提示用户重新生成。

### 5.4 AI 失败处理

| 场景 | 处理 |
| --- | --- |
| 模型超时 | 显示“生成超时，请重试” |
| JSON 解析失败 | 后端自动重试 1 次 |
| 内容明显不相关 | 用户可点“题目不准”反馈 |
| 额度不足 | 显示“今日生成次数已用完” |
| 用户输入过短 | 前端提示补充内容，不请求 AI |

## 6. 核心业务流程设计

### 6.1 MVP 主流程

```text
1. 用户进入小程序
2. 用户在输入页填写学习内容
3. 点击“生成练习”
4. 后端调用 AI 生成题目
5. 前端展示题目
6. 用户逐题答题
7. 后端判分并返回讲解
8. 用户完成所有题
9. 后端调用 AI 生成复盘报告
10. 前端展示复盘报告
```

### 6.2 首版不登录的会话方案

不做微信登录时，需要一个临时会话 ID：

```text
sessionId = 小程序本地生成的随机 ID
```

用途：

- 标记本次学习。
- 保存本地答题过程。
- 生成报告时关联题目和答案。

限制：

- 换手机或清缓存后记录可能丢失。
- 无法跨设备同步。
- 不能做长期排行榜和会员。

这是 MVP 可以接受的取舍。

## 7. 页面与模块设计

### 7.1 页面规划

| 页面 | 路径 | MVP 状态 | 作用 |
| --- | --- | --- | --- |
| 输入页 | `pages/create` | 新增 | 输入想学内容，触发 AI 生成 |
| 关卡页 | `pages/levels` | 已有骨架 | 展示生成后的学习关卡 |
| 答题页 | `pages/quiz` | 已有骨架 | 展示题目、选项、提交答案 |
| 结果页 | `pages/result` | 已有骨架 | 展示得分和答题概览 |
| 报告页 | `pages/report` | 新增 | 展示 AI 复盘报告 |
| 个人中心 | `pages/profile` | 已有骨架 | 暂时展示本地学习记录 |

### 7.2 前端模块

```text
frontend/
  package.json
  config/
  src/
    app.config.ts
    app.tsx
    app.scss
    utils/request.ts
    services/quizService.ts
    pages/create/index.tsx
    pages/levels/index.tsx
    pages/quiz/index.tsx
    pages/result/index.tsx
    pages/report/index.tsx
    pages/profile/index.tsx
    components/
```

说明：

- `frontend/` 是后续正式 Taro 4.x 前端工程目录。
- `src/app.config.ts` 负责配置小程序页面、窗口标题和 tabBar。
- `src/services/quizService.ts` 只封装业务接口，不在页面里直接拼请求。
- `src/utils/request.ts` 统一处理 baseUrl、错误提示和 loading。
- 当前 `miniprogram/` 目录保留为 Day 02 原生小程序学习骨架，不作为 P1 主线继续扩展。

### 7.3 后端模块

```text
backend/
  app/main.py
  app/config.py
  app/routes.py
  app/services/ai_service.py
  app/services/quiz_service.py
  app/services/report_service.py
  app/storage/session_store.py
  app/schemas.py
```

## 8. API 设计草案

### 8.1 健康检查

```text
GET /health
```

用途：确认后端是否启动。

### 8.2 生成题目

```text
POST /api/generate-quiz
```

请求：

```json
{
  "sessionId": "local-session-id",
  "inputType": "text",
  "content": "我想学习 Git 的 pull、commit、push",
  "questionCount": 5
}
```

响应：

```json
{
  "code": 0,
  "data": {
    "quizId": "quiz-001",
    "topic": "Git 基础命令",
    "questions": []
  }
}
```

### 8.3 提交答案

```text
POST /api/submit-answer
```

请求：

```json
{
  "sessionId": "local-session-id",
  "quizId": "quiz-001",
  "questionId": "q1",
  "selectedIndex": 1
}
```

响应：

```json
{
  "code": 0,
  "data": {
    "isCorrect": true,
    "correctIndex": 1,
    "explanation": "讲解内容",
    "knowledgePoint": "知识点"
  }
}
```

### 8.4 生成复盘报告

```text
POST /api/generate-report
```

请求：

```json
{
  "sessionId": "local-session-id",
  "quizId": "quiz-001"
}
```

响应：

```json
{
  "code": 0,
  "data": {
    "score": 4,
    "total": 5,
    "summary": "本次学习总结",
    "weakPoints": ["易错点"],
    "nextSteps": ["复习建议"]
  }
}
```

## 9. 数据设计

### 9.1 MVP 临时存储

第一版可以用 JSON 文件或 SQLite。

推荐：

```text
P1 demo: JSON 文件
P2 可复盘: SQLite
P3 多用户: MySQL/PostgreSQL
```

### 9.2 核心业务对象

| 对象 | 说明 |
| --- | --- |
| LearningSession | 一次学习会话 |
| Quiz | 一组 AI 生成题 |
| Question | 单道题 |
| AnswerRecord | 用户答题记录 |
| Report | 复盘报告 |
| GenerationLog | AI 调用日志 |

### 9.3 为什么暂不设计 User 表

因为当前最核心的问题不是“用户是谁”，而是：

```text
用户能不能从输入内容完成一轮高质量学习。
```

等核心闭环跑通后，再加微信登录和用户表。

## 10. 开发流程与实现顺序

### 10.1 第一步：后端核心 API

目标：不用真实 AI，先用 mock 数据跑通接口。

任务：

- `POST /api/generate-quiz`
- `POST /api/submit-answer`
- `POST /api/generate-report`
- 本地 JSON 存储
- API 自测文档

验收：

- 浏览器或 Postman 能完成完整流程。

### 10.2 第二步：Taro 4.x 前端核心页面

目标：小程序页面能走完整链路。

任务：

- 初始化 Taro 4.x 工程到 `frontend/`。
- 使用 React + TypeScript。
- 新增输入页。
- 答题页支持选择答案。
- 结果页展示得分。
- 报告页展示复盘。
- 把接口请求集中到 `services/quizService.ts`。

验收：

- 用户不用登录，也能完整完成一轮学习。
- `npm.cmd run dev:weapp` 能生成微信小程序开发者工具可导入的 `dist/`。

### 10.3 第三步：接入真实 AI

目标：把 mock 生成换成 DeepSeek API 调用。

任务：

- AI service 封装，统一从后端调用 DeepSeek。
- `.env` 配置 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`AI_MODEL`。
- 默认使用 `deepseek-v4-flash`，保留切换到 `deepseek-v4-pro` 的配置位。
- JSON 输出校验。
- 失败重试 1 次。

验收：

- 输入任意短文本，能生成合理题目。

### 10.4 第四步：质量与体验

目标：让 demo 可展示。

任务：

- loading/empty/error 状态。
- 题目不准反馈入口。
- 复盘报告优化。
- README 更新启动流程。
- 截图保存到 `screenshots/`。

验收：

- 可以录制一条完整演示视频或截图链路。

## 11. 工程规范

### 11.1 环境变量

真实密钥只放 `.env`：

```text
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-v4-flash
AI_REPORT_MODEL=deepseek-v4-pro
APP_PORT=8000
```

GitHub 只提交：

```text
.env.example
```

### 11.2 Git 提交节奏

每完成一个小闭环提交一次：

```bash
git status
git add .
git commit -m "feat: add quiz generation api"
git push
```

### 11.3 文档同步

每完成一个功能，至少更新：

- README 启动说明。
- docs 当前阶段说明。
- screenshots 接口或页面验证记录。

## 12. 测试方案

### 12.1 后端测试

先做手工 HTTP 验证：

- `/health`
- `/api/generate-quiz`
- `/api/submit-answer`
- `/api/generate-report`

后续补 pytest。

### 12.2 前端测试

用 Taro + 微信开发者工具验证：

- 输入为空时不能生成。
- 生成中按钮不可重复点击。
- 接口失败时有错误提示。
- 答题后能看到讲解。
- 完成后能进入报告页。
- `frontend/dist/` 能被微信开发者工具打开。

### 12.3 AI 输出测试

重点检查：

- 是否是合法 JSON。
- 是否围绕用户输入。
- 是否存在明显错误答案。
- 讲解是否有帮助。
- 报告是否能指出错题和下一步。

## 13. 部署方案

### 13.1 MVP 本地演示

```text
Taro 4.x dev:weapp + 微信开发者工具 + 本地 Python 后端
```

适合 Day 02-Day 10。

### 13.2 线上演示

后端可选：

- Render
- Railway
- 云服务器

要求：

- HTTPS。
- 环境变量配置。
- AI Key 不入库、不进 Git。

### 13.3 小程序发布

发布前需要：

- 小程序 AppID。
- 后端 HTTPS 域名。
- 微信后台配置 request 合法域名。
- 隐私协议和用户数据说明。

## 14. 主要风险与应对

| 风险 | 表现 | 应对 |
| --- | --- | --- |
| AI 题目质量不稳定 | 题目不相关、答案错 | 结构化 prompt + JSON 校验 + 用户反馈 |
| 范围膨胀 | 一开始做登录、RAG、PK | 严格按 P1 核心闭环推进 |
| 小程序请求限制 | 本地接口或域名无法请求 | 开发阶段用本地调试，发布前配置合法域名 |
| 模型成本不可控 | 每次生成消耗额度 | 限制题数、记录 GenerationLog |
| 用户输入质量差 | 输入太短无法出题 | 前端提示补充材料 |
| 版权和内容来源风险 | 抓取网页/视频内容 | 第一版只处理用户输入文本 |

## 15. 待人工确认

以下问题不阻塞方案设计，但会影响后续实现：

1. 复盘报告第一版只做文本，还是必须做图片海报？
2. 是否已经有微信小程序 AppID？
3. 后端线上部署优先用 Render/Railway，还是国内云服务器？

已确认决策：

- 第一版只做微信小程序。
- 第一版输入只支持文本，不做 URL/文档/视频解析。
- 第一版不做登录注册。
- 第一版题型只做单选题。
- 第一版 AI 供应商使用 DeepSeek，默认模型为 `deepseek-v4-flash`，保留 `deepseek-v4-pro` 切换能力。

## 16. 推荐下一步

下一步不要继续写登录注册，也不要扩展数据库。

建议直接进入 P1：

```text
实现 POST /api/generate-quiz
实现 POST /api/submit-answer
实现 POST /api/generate-report
初始化 Taro 4.x frontend 工程
新增 Taro 页面 pages/create 和 pages/report
用 mock AI 跑通完整闭环
```

当 mock 闭环跑通后，再接真实大模型。
