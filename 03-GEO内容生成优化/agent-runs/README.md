# Agent Run Logs

每次真实运行在此目录创建独立 `<run-id>/`，并从 `../AGENTS_self/orchestration/templates/` 复制模板。

运行日志只保存决策、证据、产物索引和门禁状态。不得保存 API Key、Token、Cookie、真实身份信息、未经脱敏的用户内容或模型隐藏推理过程。

```text
<run-id>/
  manifest.yaml
  events.jsonl
  debates.md
  decisions.md
  handoffs.md
  gate-report.md
  artifacts.md
```
