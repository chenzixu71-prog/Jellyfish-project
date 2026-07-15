# 微信小程序上线清单

当前代码已经具备生产构建和容器部署入口，但只有完成以下人工配置并通过真机验收后，才能提交正式审核。

## 1. 云端后端

1. 准备已备案域名，例如 `api.example.com`，并配置有效 HTTPS 证书。
2. 将 `deploy/production.env.example` 复制为不提交 Git 的 `.env.production.local`，填入 DeepSeek、Tavily、微信和 MySQL 密钥；`DATABASE_URL` 中的数据库密码必须进行 URL 编码。
3. 在 `deploy` 目录执行：

```bash
docker compose --env-file .env.production.local -f docker-compose.production.yml up -d --build
```

4. 由 Nginx、Caddy 或云负载均衡把 `https://api.example.com` 反向代理到 `127.0.0.1:8010`。
5. 验证 `GET /health` 返回运行状态，`GET /ready` 返回 `status=ready`。
6. 配置 MySQL 自动备份、容器日志轮转、API 余额告警和服务异常告警。

## 2. 微信后台

1. 在小程序后台填写服务类目、主体信息并完成小程序备案。
2. 在“开发管理 → 开发设置 → 服务器域名”中配置：
   - `request` 合法域名：生产 API HTTPS 域名；
   - `uploadFile` 合法域名：同一生产 API HTTPS 域名。
3. 后端只保存 `AppSecret`；不得把 AppSecret、DeepSeek Key 或 Tavily Key 放进小程序代码。
4. 在“用户隐私保护指引”声明微信登录标识、用户上传的文本/文件/图片、学习记录以及调用第三方 AI/搜索服务的用途。
5. 根据实际接口配置隐私授权弹窗，并提供数据删除和账号注销联系渠道。

## 3. 生产构建

在 `frontend` 目录设置仅本地保存的 `.env.production.local`：

```text
TARO_APP_ID=wx真实AppID
TARO_APP_API_BASE_URL=https://api.example.com
```

然后执行：

```bash
npm ci
npm run build:weapp:prod
```

导入目录为 `frontend/dist`。生产构建会拒绝 HTTP、localhost、空 API 地址和无效 AppID。

## 4. 提审前验收

- 真机完成微信登录，退出后再次登录仍能读取知识库、积分、报告和错题。
- 分别验证文字、网页 URL、1 个文件、3 个文件、1 张图片和 10 张图片。
- 联网搜索页面显示加载状态、来源数量和失败降级提示。
- DeepSeek/Tavily 余额不足、超时和不可用时，前端显示可理解的错误信息。
- 完成知识库创建、进入闯关、答题、报告、错题复习和再次进入知识库全链路。
- 检查用户协议、隐私指引、第三方数据处理说明和内容安全策略。
- 上传体验版，至少完成一轮不同网络和不同尺寸手机测试，再提交审核。

## 5. 已知依赖风险

- 当前 Taro 最新正式版为 `4.2.0`，项目已使用该版本。
- `npm audit --omit=dev` 仍会报告 Taro 传递依赖中的 `swiper`、`lodash-es` 等告警，当前没有不破坏 Taro 兼容性的自动修复方案。
- Taro 4.2.0 将 Webpack peer dependency 精确锁定为 `5.91.0`，暂时无法单独升级；禁止执行会破坏依赖树的 `npm audit fix --force`。
- 正式发布前应重新运行依赖审计，并在 Taro 发布兼容修复后统一升级全部 `@tarojs/*` 包。

## 尚未自动完成的人工门槛

- 云服务器、备案域名和 HTTPS 证书；
- 微信后台合法域名、隐私指引、服务类目和版本提审；
- 短信验证码登录需要另选短信服务商并完成模板/签名审核，当前版本只有微信登录；
- 正式发布必须由小程序管理员在微信后台确认。
