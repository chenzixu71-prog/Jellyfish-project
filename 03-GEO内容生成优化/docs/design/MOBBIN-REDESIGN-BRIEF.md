# Mobbin Redesign Brief

## Decision

现有 `A / Evidence Editorial`、`B / Signal Grid`、`C / Field Notes` 降级为探索废稿，不再提交用户批准。它们的问题不是局部 polish，而是整体仍像概念板：过粗的黑色导航、荧光强调色、海报式标题和人为切出的三栏，让 GEO 工作流显得生硬、廉价且不够国际化。

新方向只保留一套：`D / Quiet Evidence Workspace`。

## Mobbin Evidence

| 产品 | 可借鉴 | 不复制 |
|---|---|---|
| [WRITER - document review](https://mobbin.com/screens/9ef4cec0-f416-41e5-aaee-7c694805bef8) | 正文占据主视觉，建议贴近对应文本，右侧轨道可折叠，分数退居次要位置 | 品牌紫色、过密的语言规则分类 |
| [OpenAI Platform - evaluation report](https://mobbin.com/screens/ef9c37e1-44e2-400f-9b2e-44f8d1006145) | 报告/数据分层、运行结果表、配置侧栏、克制状态色 | 大面积空白和面向开发者的 schema 细节 |
| [Braintrust - experiment trace](https://mobbin.com/screens/eaa59428-fe41-4366-a344-e5082a6d7b76) | Trace、输入、输出、指标、错误信息在同一详情页形成证据链 | 纯日志工具的工程感和弱视觉层级 |
| [Mixpanel - comparison analysis](https://mobbin.com/screens/41286ad3-47e8-4de6-9370-828e0df60410) | 紧凑筛选、主分析区、右侧配置、表格明细的渐进披露 | 紫色品牌顶栏和复杂分析器配置 |
| [Profound - answer engine insights](https://mobbin.com/screens/4def7e6a-f280-4cf7-bfe8-e0c53429aef5) | GEO 业务导航、时间/模型/主题筛选、趋势与排名组合 | 通用图表仪表盘和弱操作闭环 |
| [Lovable - optimization report](https://mobbin.com/screens/91e4caa2-3908-478a-92e5-50ed9843795d) | 问题分组、影响说明、逐项修复动作、当前/潜力对照 | 暖米色底、AI 对话框主导页面 |

## Visual System

- Base: neutral white `#FFFFFF`, canvas `#F7F8FA`, subtle border `#E6E8EC`.
- Text: primary `#17191C`, secondary `#656B74`, tertiary `#9298A1`.
- Brand accent: restrained cobalt `#3157D5`; only for selection, focus and primary action.
- Semantic colors: success `#16825D`, warning `#B7791F`, danger `#C94242`; use pale backgrounds, never neon blocks.
- Typography: Inter for Latin and numbers; Noto Sans SC for Chinese. No decorative serif, no condensed mono as the primary interface font.
- Radius: 6px controls, 8px overlays; no pill buttons except status filters.
- Shadows: only menus, dialogs and floating inspector; page sections use borders and whitespace.
- Density: 8px spacing system, 14px default body, 12px metadata, 20-28px page heading.

## Shell

- Left navigation: 216px expanded / 64px collapsed, light neutral surface, icon + label. No full-height black bar.
- Top context bar: breadcrumb, project switcher, environment/model status, one primary action.
- Main area: fluid content with `max-width` only where reading width matters; analytics and comparison views use full width.
- Inspector: 320-360px contextual side panel, dismissible and resizable where useful.

## Core Screens

### S01 Projects

- Compact page header and one primary `New evaluation` action.
- Recent projects as a table/list, not a card gallery.
- Columns: project, domain, last run, GEO score change, status, owner.
- Empty state uses one restrained generated brand asset; no dashboard illustration wall.

### S02 Evaluation Setup

- Three-step setup in one page: content source, prompt set, model/provider.
- Progressive disclosure for advanced settings.
- Sticky summary panel shows estimated runs, cost range and validation errors.

### S03 Run Detail

- Header: run status, model, prompt set, timestamp, duration, retry.
- Tabs: Overview / Responses / Evidence / Errors.
- Overview uses a compact metric strip plus result table; errors are inline and filterable.
- No giant circular score. GEO score is one metric among coverage, citation readiness and answer consistency.

### S04 Diagnosis & Revision

- Center: readable source document with inline evidence highlights.
- Right: grouped findings with severity, evidence, minimal fix and apply/reject action.
- Left navigation remains app-level, not a second diagnostic index.
- Applying a suggestion creates a visible change set with undo and stale-conflict handling.

### S05 Comparison Report

- Before/after segmented control, synchronized text diff and metric comparison.
- Direct labels on charts; full evidence table beneath summary.
- Every improvement states test set, model, time and proxy-metric limitation.

## Interaction Quality Bar

- One primary action per view.
- Hover, focus, selected, disabled, loading, empty, partial success, stale, error and permission states must be designed.
- All important metrics expose definition and evaluation context.
- Dense screens remain readable at 1366x768; no horizontal overflow in the core flow.
- Generated bitmap assets are limited to empty states, onboarding and report cover accents. All UI text and data remain native Figma components.

## Figma Rebuild Order

1. Replace the visual-direction page with one shell study and one S04 hero screen.
2. User reviews shell, palette, density and S04 interaction language.
3. After approval of the direction, build tokens/components and S01-S05 states.
4. Run PM, user research and frontend critique before requesting GATE-2.
