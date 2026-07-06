# 水母diy学习助手 - P0 用户登录方案设计

## 0. 文档状态

本文档只覆盖第一批需求：用户登录。确认后再进入开发。

## 1. 本批目标

让用户可以在小程序中完成微信一键登录，并获得后端自定义登录态。

本批不做：

- 获取完整用户信息。
- 闯关历史列表。
- 报告历史。
- 错题本。
- 手机号登录。
- 密码注册。
- 用户资料编辑。

## 2. 官方依据

- Taro 官方：`Taro.login` 支持微信小程序端，用于获取登录凭证 `code`。
- 微信官方：`wx.login` 返回的 `code` 有效期为 5 分钟。
- 微信官方：后端调用 `code2Session`，用 `appid + secret + code` 换取 `openid`、`session_key`，可能返回 `unionid`。
- 微信官方：开发者服务器应生成自己的登录态，用于后续业务请求识别用户。

参考：

- https://docs.taro.zone/docs/apis/open-api/login/login
- https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html
- https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html

## 3. 登录流程

```text
1. 用户在“我的”页面点击“微信一键登录”
2. 前端调用 Taro.login 获取 code
3. 前端把 code 和本地 sessionId 发给后端
4. 后端调用微信 code2Session
5. 后端根据 openid 创建或读取用户
6. 后端生成自定义 token
7. 前端保存 token
8. 前端进入已登录状态
```

## 4. 前端范围

页面：`我的`

未登录状态：

- 显示默认水母身份。
- 显示按钮：`微信一键登录`
- 保留游客模式提示。

登录中状态：

- 按钮 loading。
- 禁止重复点击。

登录成功状态：

- 保存 token。
- 展示已登录状态。
- 不强制获取微信昵称和头像。

登录失败状态：

- 显示失败提示。
- 用户仍可继续游客模式。

## 5. 后端范围

新增能力：

- 接收前端传来的 `code` 和 `sessionId`。
- 调用微信 `code2Session`。
- 根据 `openid` 创建或读取用户。
- 生成后端自定义 token。
- 返回 token 和最小用户信息。

第一版最小用户信息：

```json
{
  "id": "user_id",
  "displayName": "水母学员",
  "avatarUrl": "",
  "loginType": "wechat"
}
```

## 6. API 草案

```text
POST /api/auth/wechat-login
```

请求：

```json
{
  "code": "wx-login-code",
  "sessionId": "guest-session-id"
}
```

成功响应：

```json
{
  "code": 0,
  "data": {
    "token": "server-token",
    "user": {
      "id": "user_id",
      "displayName": "水母学员",
      "avatarUrl": "",
      "loginType": "wechat"
    }
  }
}
```

失败响应：

```json
{
  "code": 1001,
  "message": "登录失败，请稍后重试"
}
```

## 7. 数据保存

本批只需要保存登录相关最小数据：

- 用户。
- 微信 `openid` 绑定。
- token 登录态。

`session_key` 不返回前端。

## 8. 安全规则

- `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET` 只能放后端环境变量。
- 前端不能保存 `openid`、`session_key`、`AppSecret`。
- 后端数据库不保存明文 token，只保存 token 哈希。
- token 第一版有效期建议 7 天。
- 退出登录不在本批实现，可放到后续用户信息批次。

## 9. 测试验收

后端 TDD：

- 首次微信登录会创建用户。
- 同一 `openid` 再次登录返回同一用户。
- 微信 `code2Session` 失败时返回登录失败。
- 成功登录后返回 token。

前端验收：

- 点击登录按钮后能进入登录中状态。
- 登录成功后能展示已登录状态。
- 登录失败后仍可游客模式学习。
- 不弹出强制获取头像昵称授权。

## 10. 确认后开发步骤

1. 后端先写 P0 登录测试。
2. 实现微信登录服务。
3. 实现 `/api/auth/wechat-login`。
4. 前端新增 `authService`。
5. “我的”页面接入登录按钮和登录状态。
6. 运行测试和构建。
7. Git 提交本批功能。
