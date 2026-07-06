# 水母 DIY 学习助手小程序 UI 10 轮设计优化记录

## Visual Constraints

- Product surface: 微信小程序，核心链路是输入知识、生成题目、答题、查看报告。
- Local UI stack: Taro 4 React，微信小程序 `View/Text/Button/Textarea/ScrollView`，`designWidth: 375`。
- Layout shell: 自定义导航栏，保留微信胶囊按钮；底部使用微信原生 tabBar。
- Tokens / palette: `#6246f2` 紫色主背景，`#fffdf7` 纸白，`#f7de61` 黄色重点，`#21e6da` 青色强调，`#f28abd` 水母粉，`#dfeeff/#bcefff` 蓝色信息区。
- Typography: 手写体优先，中文必须清晰可读，标题保持手写感，正文控制在 14-16px。
- Components to reuse: 现有水母 CSS 组件、泡泡、输入卡片、答题选项、半屏知识详情、报告卡。
- Required states: 空输入、素材已选、生成 loading、答题选中、答对、答错、知识详情弹层、通关、报告 loading、无报告、历史记录。
- Gaps / assumptions: 不引入新 UI 组件库；微信小程序不支持完整浏览器 hover，转为点击反馈和持续轻动效。

## Screen Inventory

- 首页：品牌区、今日挑战区、水母舞台、输入区、上传区、生成按钮、生成 loading。
- 答题页：题目信息、进度、选项、提交、答题反馈、知识详情半屏。
- 通关页：庆祝泡泡、水母、报告入口。
- 报告页：loading、REPORT CENTER、得分/掌握度、结构化报告、分享入口。
- 记录页：空状态、历史报告列表、新练习入口。

## 10 Rounds

1. 文案与编码：修复小程序源码里的中文乱码，保证微信端展示不是 mojibake。
2. 首页信息层：补“今日挑战”卡片，让首屏不只是装饰，用户能知道 5 题目标和即时讲解。
3. 首页视觉重心：水母舞台保持在标题和输入卡之间，避免压住微信胶囊和输入区。
4. 动效体系：统一水母浮动、身体轻压缩、眨眼、触手浮动、泡泡上升。
5. 生成状态：生成题目时增加水母解析素材的 loading 层，而不是只依赖按钮 loading。
6. 答题反馈：答对用黄色，答错用弱红；选项添加轻脉冲，但不影响可读性。
7. 知识详情：半屏上滑，外部点击关闭，内容结构化为解释、答案、标签、下一步。
8. 报告质感：保留 REPORT CENTER 封面，得分卡呼吸，报告区保持可扫读。
9. 记录页统一：历史卡片使用同样柔光白卡和轻浮动，空状态给明确下一步。
10. 小程序渲染校准：保持 `375` 设计宽度，使用自定义导航和底部留白，避免被微信系统 UI 挤压。

## Frontend Handoff

- 首页新增状态组件：`.challenge-card`, `.challenge-stats`, `.loading-overlay`, `.loading-panel`。
- 答题页保留现有结构，重点修复文案和已有动效。
- 报告页修复文案，保留微信分享 `openType='share'` 和 QQ 预留 toast。
- 记录页修复文案，保留本地 storage 历史记录。
- 验收路径：微信开发者工具清缓存编译后，依次检查首页、生成 loading、答题反馈、知识详情、通关页、报告页、记录页。
