# handoffs


## Frontend -> QA

- 目标：验证新版首页、答题反馈、讲解抽屉、通关和报告交互。
- 版本：当前工作树，等待 Git 提交。
- 已验证：微信/H5 构建通过；手机首屏、输入、联网开关、加载层通过。
- 排除：公开发布、DeepSeek/Tavily 服务质量、Figma。
- 风险：图片体积告警、真机差异、未部署 E2E。
- 接收：QA 条件接收；发布 Gate 保持关闭。

## Product/AI/Engineering -> User

- 目标：确认个人知识库学习闭环的 P0 范围。
- 输入：现有需求文档、前后端代码、存储和测试。
- 输出：`docs/personal-knowledge-loop-review.md`、`.backend/202607/personal-knowledge-loop/explore.md`。
- 建议：真实素材上传、解析状态、手工补题、点击即闯关、恢复上次知识库、统一账号归属。
- 排除：本轮不实现业务代码，不批准公开发布。
- 状态：等待用户接受、调整或拒绝 P0-A 至 P0-F。
