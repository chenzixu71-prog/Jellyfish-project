# 水母diy学习助手 - P1 获取用户信息方案设计

## 0. 文档状态

本文档只覆盖第二批需求：获取用户信息。确认后再进入开发。

## 1. 本批目标

登录后，“我的”页面可以从后端获取当前用户基础资料和学习概览。

本批不做：

- 游客数据绑定。
- 闯关历史列表。
- 报告历史列表。
- 错题本。
- 退出登录。
- 昵称头像授权或编辑。

## 2. 依据

- P0 已完成微信登录，并在前端保存后端 token。
- Taro 官方支持 `Taro.getStorageSync` / `Taro.setStorageSync` 存取本地登录态。
- Taro 官方 `Taro.request` 支持请求 header，可携带 `Authorization`。
- 已确认第一版默认使用水母身份，不强制获取微信头像昵称。

## 3. 用户体验

未登录：

- “我的”页面显示默认水母身份。
- 显示“微信一键登录”。
- 不展示后端用户统计。

已登录：

- 页面打开时请求当前用户信息。
- 展示默认昵称：`水母学员`。
- 展示默认头像或水母身份标识。
- 展示学习概览：累计答题数、正确率、学习次数、等级、经验值、连续学习天数。
- 接口失败时保留本地登录状态，但显示轻提示。

## 4. API 草案

```text
GET /api/me
Authorization: Bearer <token>
```

成功响应：

```json
{
  "code": 0,
  "data": {
    "id": "user_id",
    "displayName": "水母学员",
    "avatarUrl": "",
    "loginType": "wechat",
    "level": 1,
    "exp": 0,
    "streakDays": 1,
    "totalAnswered": 0,
    "totalCorrect": 0,
    "totalSessions": 0,
    "accuracy": 0
  }
}
```

未登录或 token 无效：

```json
{
  "code": 1002,
  "message": "登录已失效，请重新登录",
  "data": null
}
```

## 5. 后端范围

新增能力：

- 从 `Authorization` header 读取 Bearer token。
- 校验 token 是否存在、未过期。
- 根据 token 找到用户。
- 返回最小用户资料和学习概览。

学习概览第一版可以先使用现有统计数据：

- `level`
- `exp`
- `streakDays`
- `totalAnswered`
- `totalCorrect`
- `accuracy`
- `totalSessions`

说明：

- 因 P2 才做游客数据绑定，本批登录用户的统计可从用户自身统计读取。
- 如果用户暂无统计，返回 0 值，不报错。

## 6. 前端范围

新增或调整：

- `authService` 增加 `getCurrentUser()`。
- 通用请求层支持可选 `Authorization` header。
- “我的”页面在已登录时请求 `/api/me`。
- “我的”页面展示统计卡片。

页面状态：

```text
未登录 -> 显示登录卡片
已登录且加载中 -> 显示用户卡片 loading
已登录且加载成功 -> 显示用户资料和学习概览
已登录但加载失败 -> 显示本地水母身份 + 错误提示
```

## 7. 测试验收

后端 TDD：

- 有效 token 可以获取用户信息。
- 无 token 返回 `1002`。
- 无效 token 返回 `1002`。
- 新登录用户没有学习数据时，统计返回 0 值。

前端验收：

- 未登录时不请求 `/api/me`。
- 登录后进入“我的”页面会请求 `/api/me`。
- 成功后展示昵称和统计。
- 失败时不影响继续游客学习。

## 8. 确认后开发步骤

1. 后端先写 `/api/me` 测试。
2. 后端补 token 校验方法。
3. 实现 `GET /api/me`。
4. 前端请求层支持 auth header。
5. `authService` 增加获取当前用户信息。
6. “我的”页面展示学习概览。
7. 跑后端测试、Taro 构建、HTTP 验证。
8. Git 提交并推送本批功能。
