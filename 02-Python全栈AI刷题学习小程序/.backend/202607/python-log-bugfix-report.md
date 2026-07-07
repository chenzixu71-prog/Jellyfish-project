# Python 后端日志排查与修复报告

## 结论

本次排查历史后端验证日志后，确认需要修复的业务问题是：`/api/submit-answer` 在收到单选答案字符串时返回 `422`。已修复为兼容字符串和数组两种格式。

## 日志证据

- `.backend/202607/p0-p6-user-system-verify/runs/run-2.log:632-642`
  - 请求：`POST /api/submit-answer`
  - 结果：`HTTP_STATUS=422`
  - 原因：日志里的请求体传入 `"answer": "B"`，但后端模型只接受 `list[str]`。

- `.backend/202607/p0-p6-user-system-verify/runs/run-1.log:8-9`
  - 现象：`The process cannot access the file ... because it is being used by another process.`
  - 判断：这是验证脚本同时读写同一个日志文件导致的文件占用，不是后端接口业务 bug。

## 修复内容

- `backend/app/schemas.py`
  - 在 `SubmitAnswerRequest.answer` 上增加 Pydantic `field_validator`。
  - 当传入 `"B"` 时自动转换为 `["B"]`。
  - 原本传入 `["A", "B"]` 的多选题答案不受影响。

- `backend/tests/test_api.py`
  - 新增回归测试：`test_submit_answer_accepts_single_answer_string_for_compatibility`。
  - 覆盖日志中的同类问题，确保字符串答案不再返回 `422`。

## 验证结果

```text
28 passed in 1.13s
```

## 后续建议

- 如果后续继续维护 `.backend` 验证脚本，建议每次运行写入新的日志文件，避免同一个进程边写边读导致 Windows 文件占用。
- 前端当前 Taro 服务层已经传 `string[]`，本次修复主要增强后端兼容性，防止手工调试、脚本测试或其他客户端传字符串时失败。
