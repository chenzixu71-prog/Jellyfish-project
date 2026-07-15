# Skill Router

## 1. 选择流程

每个 Agent 在 Action 开始前执行：

1. 读取当前任务、角色边界和阶段允许的 Action。
2. 查看当前会话实际暴露的 Skills，不把历史安装记录当作当前可用性证明。
3. 根据 Skill description 判断是否触发。
4. 选中后完整读取对应 `SKILL.md`，包括其明确要求的直接引用文件。
5. 按 Skill 的流程执行，并保存输出或证据路径。
6. 在 `events.jsonl` 记录 `invoked`、`skipped`、`unavailable` 或 `failed`。

不得为满足“每个角色都用了 Skill”而调用无关 Skill。角色至少要完成一次真实、符合触发条件的 Skill 调用；若当前阶段确实没有匹配 Skill，记录 `no_matching_skill` 并由总负责人确认，不得虚构。

## 2. 角色路由

| 角色 | 优先 Skill | 使用条件 |
|---|---|---|
| 用户研究 | `competitive-analysis` | 竞品结论要影响产品决策时 |
| 用户研究 | `requirement-analysis-assistant` | 用户信号混乱、冲突或缺口较多时 |
| 用户研究 | `research-industry` | 需要系统行业研究和证据库时 |
| 用户研究 | `pdf` / `ocr-and-documents` / `paper-lookup` | 阅读论文、扫描文档或补充学术证据时 |
| 产品经理 | `brainstorming` | 方案尚未定案，需要比较路径时 |
| 产品经理 | `prd-architect` / `prd-development` | 已确认方案要形成 PRD 时 |
| 产品经理 | `prd-review` | 已有 PRD 要做交付评审时 |
| 设计师 | `ui-mockup-desktop-workbench` | PRD 要转成 UI 结构和状态时 |
| 设计师 | `imagegen` | 生成视觉方向或位图素材时 |
| 设计师 | `figma:figma-use` | 任何 Figma 操作前，强制前置 |
| 设计师 | `figma:figma-generate-design` | 页面或多区块布局进入 Figma 时 |
| 设计师 | `figma:figma-generate-library` | 建立变量、组件和设计系统时 |
| 前端 | `figma:figma-use` | 读取设计真源和组件属性时 |
| 前端 | `sites:sites-building` | 仅项目使用 Sites 或存在 `.openai/hosting.json` 时 |
| 前端 | `playwright` / `playwright-interactive` | 浏览器流程、截图、UI 调试时 |
| 后端 | `explore` | 陌生/遗留后端或影响范围不清时 |
| 后端 | `verify` | Endpoint 改动后验证运行中服务时 |
| 后端 | `openai-docs` | 接入或选择 OpenAI 产品/API 时 |
| 测试 | `prd-review` | 检查需求是否可测试时 |
| 测试 | `verify` | 本地 HTTP 接口验证时 |
| 测试 | `playwright` | 本地浏览器流程和截图时 |
| 测试 | `qa-engineer` | 仅已部署 URL 的 E2E 门禁 |
| 总负责人 | `prd-review` | 独立复核 PRD 交付性时 |
| 总负责人 | `qa-engineer` | 复核部署后证据时 |
| 总负责人 | `tailored-resume-generator` | 有真实结果且目标岗位明确时 |

## 3. 失败与回退

- `unavailable`：Skill 未暴露、路径不可读或所需连接器不可用。
- `failed`：Skill 已执行但未产出有效结果。
- `skipped`：已检查但触发条件不成立。
- `no_matching_skill`：当前 Action 没有适用 Skill。

处理规则：

- 若 Skill 是质量门禁的必要能力，如 Figma 真源或部署后 QA，转 `BLOCKED`。
- 若有不降低质量的本地替代，可继续，但必须记录替代方式和局限。
- 不允许把普通图片冒充 Figma，不允许把手工点击冒充可重复 E2E。
- 不允许因为 Skill 失败而隐去失败记录或改写门禁标准。

## 4. 日志字段

每次 Skill 决策至少记录：

```json
{
  "skill": "playwright",
  "trigger": "验证本地核心浏览器流程",
  "status": "invoked",
  "input_refs": ["docs/PRD.md#REQ-001"],
  "output_refs": ["artifacts/playwright/core-flow.png"],
  "limitations": []
}
```

总负责人只根据日志和输出证据确认 Skill 已使用。
