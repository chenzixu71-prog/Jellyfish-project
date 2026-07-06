# 水母diy学习助手 - 用户系统方案设计

## 0. 文档状态

本文档是“用户系统”扩展功能的方案设计稿，用于人工确认后再进入开发。当前不启动编码。

当前已确认：

- 已有微信小程序 AppID/AppSecret，可支持真实微信登录。
- 用户系统阶段采用 MySQL 作为主数据库，不使用 SQLite 作为正式存储。
- 第一版用户资料只做基础版，不做手机号、密码注册、复杂资料编辑和会员支付。
- 核心学习链路保持不变：用户输入知识 -> AI 生成题目 -> 用户答题闯关 -> AI 生成报告。

## 1. 设计目标

用户系统第一版只解决三件事：

1. 让用户可以通过微信一键登录建立稳定身份。
2. 让游客模式下产生的学习数据在登录后可以绑定到用户账号。
3. 让“我的”页面能够展示长期学习数据，包括学习统计、错题、报告历史和成长值。

不在第一版解决：

- 手机号登录。
- 密码注册。
- 复杂个人资料编辑。
- VIP 支付。
- 好友关系。
- 排行榜。
- 多设备实时同步冲突处理。
- 后台管理系统。

## 2. 用户与场景

### 2.1 未登录用户

未登录用户仍然可以完成一次完整学习：

```text
输入学习内容 -> 生成题目 -> 答题 -> 查看报告
```

系统继续使用本地 `sessionId` 标记游客身份。这样可以避免用户刚进入小程序就被登录打断。

### 2.2 登录用户

登录用户可以获得长期能力：

- 保存学习记录。
- 保存报告历史。
- 保存错题本。
- 累积成长值和等级。
- 统计连续学习天数。
- 后续支持额度、会员、排行榜和跨设备同步。

### 2.3 游客转登录

用户完成学习后，如果点击登录，系统需要把当前游客数据绑定到微信账号：

```text
游客 sessionId 下的数据 -> 登录成功 -> 绑定到 userId
```

如果用户之前已经登录过，则把当前游客数据合并到已有用户数据中。

## 3. 总体架构

```text
Taro 4.x 微信小程序
  -> Python FastAPI 后端
    -> 微信 code2Session
    -> MySQL 主数据库
    -> DeepSeek AI 服务
```

第一版不引入 Redis。登录态先使用后端生成的自定义 token，并保存到 MySQL。后续如果访问量上升，再把 token/session 缓存迁移到 Redis。

## 4. 微信登录方案

### 4.1 登录链路

```text
1. 前端调用 Taro.login 获取临时 code
2. 前端把 code、当前 sessionId 发送给后端
3. 后端调用微信 code2Session
4. 微信返回 openid、session_key
5. 后端根据 openid 创建或读取用户
6. 后端生成自定义 token
7. 前端保存 token 和用户基础信息
8. 后续请求携带 Authorization: Bearer <token>
```

### 4.2 为什么不直接用 openid 当登录态

`openid` 是用户在当前小程序下的稳定身份标识，但不应该直接暴露为业务登录态。后端应生成自己的 token，这样可以：

- 控制过期时间。
- 支持退出登录。
- 支持后续风控和设备管理。
- 避免前端直接依赖微信身份字段。

### 4.3 用户资料策略

第一版只做轻量资料：

- 默认昵称：`水母学员`
- 默认头像：项目水母 Logo 或默认头像
- 如果用户主动授权或后续主动编辑，再保存昵称和头像

不强制获取微信头像昵称，不请求手机号。

## 5. 身份模型

系统同时支持两种身份：

| 身份 | 标识 | 适用场景 |
| --- | --- | --- |
| 游客 | `sessionId` | 未登录也能学习 |
| 登录用户 | `userId` + `token` | 长期保存和跨设备访问 |

接口处理规则：

1. 如果请求带合法 token，优先按 `userId` 读写数据。
2. 如果没有 token，但带 `sessionId`，按游客数据读写。
3. 登录成功后，将该 `sessionId` 下未绑定的数据迁移或关联到 `userId`。
4. 迁移完成后，前端仍可保留 `sessionId`，但后端以 `userId` 为准。

## 6. MySQL 数据设计

### 6.1 核心表

| 表名 | 作用 |
| --- | --- |
| `users` | 用户主表 |
| `user_auth_wechat` | 微信身份绑定表 |
| `auth_sessions` | 后端自定义登录态 |
| `guest_sessions` | 游客 session 记录 |
| `learning_sessions` | 一次学习任务 |
| `quizzes` | AI 生成的一组题 |
| `questions` | 单道题 |
| `question_options` | 题目选项 |
| `answer_records` | 答题记录 |
| `wrong_questions` | 错题记录 |
| `reports` | 学习报告 |
| `user_stats` | 用户累计统计 |
| `user_badges` | 用户勋章 |
| `generation_logs` | AI 调用日志 |

### 6.2 关键字段草案

#### `users`

| 字段 | 说明 |
| --- | --- |
| `id` | 用户 ID |
| `display_name` | 展示昵称 |
| `avatar_url` | 头像 |
| `status` | 用户状态 |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

#### `user_auth_wechat`

| 字段 | 说明 |
| --- | --- |
| `id` | 记录 ID |
| `user_id` | 关联用户 |
| `openid` | 微信 openid |
| `unionid` | 微信 unionid，可为空 |
| `session_key_encrypted` | 加密后的 session_key |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

`openid` 需要唯一索引。

#### `auth_sessions`

| 字段 | 说明 |
| --- | --- |
| `id` | 记录 ID |
| `user_id` | 用户 ID |
| `token_hash` | token 哈希，不存明文 token |
| `expires_at` | 过期时间 |
| `revoked_at` | 退出登录时间 |
| `created_at` | 创建时间 |

#### `learning_sessions`

| 字段 | 说明 |
| --- | --- |
| `id` | 学习会话 ID |
| `user_id` | 登录用户 ID，可为空 |
| `guest_session_id` | 游客 sessionId，可为空 |
| `topic` | 学习主题 |
| `input_type` | 输入类型 |
| `input_content` | 输入内容摘要或正文 |
| `status` | 状态 |
| `created_at` | 创建时间 |

#### `answer_records`

| 字段 | 说明 |
| --- | --- |
| `id` | 答题记录 ID |
| `user_id` | 用户 ID，可为空 |
| `guest_session_id` | 游客 sessionId，可为空 |
| `quiz_id` | 题组 ID |
| `question_id` | 题目 ID |
| `selected_answer` | 用户选择 |
| `is_correct` | 是否正确 |
| `created_at` | 创建时间 |

#### `reports`

| 字段 | 说明 |
| --- | --- |
| `id` | 报告 ID |
| `user_id` | 用户 ID，可为空 |
| `guest_session_id` | 游客 sessionId，可为空 |
| `quiz_id` | 题组 ID |
| `score` | 得分 |
| `total` | 题目总数 |
| `mastery` | 掌握度 |
| `summary` | 总结 |
| `weak_points_json` | 薄弱点 |
| `next_steps_json` | 下一步建议 |
| `created_at` | 创建时间 |

### 6.3 索引建议

- `user_auth_wechat.openid` 唯一索引。
- `auth_sessions.token_hash` 唯一索引。
- `learning_sessions.user_id + created_at` 普通索引。
- `answer_records.user_id + created_at` 普通索引。
- `wrong_questions.user_id + created_at` 普通索引。
- `reports.user_id + created_at` 普通索引。
- `generation_logs.user_id + created_at` 普通索引。

## 7. API 设计

### 7.1 微信登录

```text
POST /api/auth/wechat-login
```

请求：

```json
{
  "code": "wx-login-code",
  "sessionId": "local-guest-session-id"
}
```

响应：

```json
{
  "code": 0,
  "data": {
    "token": "server-issued-token",
    "expiresAt": "2026-07-13T00:00:00+08:00",
    "user": {
      "id": "user_001",
      "displayName": "水母学员",
      "avatarUrl": "",
      "level": 1,
      "exp": 0
    },
    "merged": {
      "learningSessions": 1,
      "reports": 1,
      "wrongQuestions": 0
    }
  }
}
```

### 7.2 获取当前用户

```text
GET /api/me
Authorization: Bearer <token>
```

响应：

```json
{
  "code": 0,
  "data": {
    "id": "user_001",
    "displayName": "水母学员",
    "avatarUrl": "",
    "level": 1,
    "exp": 0,
    "streakDays": 1,
    "totalAnswered": 5,
    "totalCorrect": 4,
    "badges": []
  }
}
```

### 7.3 退出登录

```text
POST /api/auth/logout
Authorization: Bearer <token>
```

处理：

- 后端将当前 token 标记为 revoked。
- 前端清除本地 token 和用户资料。
- 游客 `sessionId` 保留，用户仍可继续游客模式学习。

### 7.4 现有学习接口的身份兼容

现有接口保持路径不变：

- `POST /api/generate-quiz`
- `POST /api/submit-answer`
- `POST /api/generate-report`
- `GET /api/wrong-questions`
- `GET /api/report-history`
- `GET /api/daily-challenge`
- `GET /api/profile`

兼容策略：

- 前端已登录时附带 `Authorization`。
- 前端仍传 `sessionId`，用于游客数据迁移和兜底。
- 后端统一通过 identity resolver 决定本次请求属于 `userId` 还是 `guest_session_id`。

## 8. 前端页面设计

### 8.1 “我的”页面

未登录状态：

- 展示水母头像或默认头像。
- 文案：`登录后保存你的水母学习记录`
- 主按钮：`微信一键登录`
- 次按钮或弱提示：`继续游客模式`
- 展示游客本地最近学习记录。

已登录状态：

- 展示头像、昵称、等级、经验。
- 展示累计答题数、正确率、连续学习天数。
- 展示勋章区域。
- 展示报告历史入口。
- 展示错题本入口。
- 展示退出登录入口。

### 8.2 首页与核心学习链路

首页、闯关、报告、错题页面不强制登录。登录只增强数据保存能力，不阻断学习链路。

### 8.3 登录触发点

建议放在三个位置：

1. “我的”页面主入口。
2. 用户完成一轮学习并生成报告后，提示“登录后长期保存报告”。
3. 用户进入错题本或报告历史时，如果未登录，提示“登录后可跨设备查看”。

## 9. 安全与合规

### 9.1 密钥管理

以下内容只能放在后端环境变量，不进入 Git：

```text
WECHAT_APP_ID=
WECHAT_APP_SECRET=
AUTH_TOKEN_SECRET=
MYSQL_HOST=
MYSQL_PORT=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
```

### 9.2 token 存储

- 前端只保存后端签发的 token。
- 后端数据库只保存 token 哈希。
- token 设置过期时间。
- 退出登录后 token 立即失效。

### 9.3 隐私边界

第一版不采集手机号，不读取通讯录，不读取地理位置。

需要在小程序隐私说明中明确：

- 会保存用户学习主题。
- 会保存答题记录。
- 会保存错题和报告。
- 学习内容会发送到后端和 AI 服务用于生成题目与报告。

## 10. 测试方案

后端必须 TDD：

1. `test_wechat_login_creates_user`
   - mock 微信 code2Session 返回 openid。
   - 首次登录创建用户。

2. `test_wechat_login_reuses_existing_user`
   - 同一个 openid 再次登录返回同一个用户。

3. `test_login_merges_guest_learning_data`
   - 给游客 sessionId 创建报告和错题。
   - 登录后数据绑定到 userId。

4. `test_me_requires_valid_token`
   - 无 token 访问 `/api/me` 失败。
   - 有效 token 访问成功。

5. `test_logout_revokes_token`
   - 退出登录后 token 失效。

6. `test_guest_flow_still_works_without_login`
   - 不登录也能生成题目、答题、生成报告。

前端验证：

- 未登录可完整学习。
- 点击微信一键登录后能展示用户信息。
- 登录后报告历史和错题本能读取用户数据。
- 退出登录后回到游客状态。
- 接口失败时有明确提示，不出现空白页。

## 11. 开发步骤

人工确认后，按以下顺序开发：

### 阶段 1：数据库与后端 TDD

- 增加 MySQL 连接配置。
- 增加数据库迁移脚本。
- 先写用户系统测试。
- 实现用户表、微信身份表、登录态表。
- 实现微信登录、退出登录、获取当前用户。
- 实现游客数据绑定到用户。

### 阶段 2：现有接口身份改造

- 增加 identity resolver。
- 现有学习接口支持 token + sessionId 双模式。
- 报告、错题、学习统计改为可按 userId 查询。
- 保持游客模式兼容。

### 阶段 3：Taro 前端接入

- 新增 `authService.ts`。
- 统一请求层自动附带 token。
- “我的”页面增加登录态、用户资料、退出登录。
- 报告历史、错题、成长值读取后端用户数据。
- 登录成功后刷新用户数据。

### 阶段 4：验证与提交

- 运行后端 pytest。
- 运行 Taro 微信小程序构建。
- 微信开发者工具人工验证登录和游客模式。
- 文档补充启动说明、环境变量说明和 MySQL 初始化说明。
- 完成 Git 提交。

## 12. 待人工确认

进入开发前还需要确认：

1. MySQL 使用方式：本地 Docker、云数据库，还是云服务器自建 MySQL。
2. 微信 AppID/AppSecret 是否由你提供后写入本地 `.env`，还是你自己手动配置。
3. token 有效期第一版建议 7 天，是否接受。

我的建议：

- 本地开发用 Docker MySQL。
- AppID/AppSecret 放 `.env`，只提交 `.env.example`。
- token 有效期先用 7 天。
- 第一版不做 Redis，等登录用户量和接口压力上来后再加。
