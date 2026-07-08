# AdGrowth AI｜AI 广告创意增长平台

这是一个面向商业化广告场景的 H5 后台产品 Demo，支持 PC 和移动端自适应。项目暂不接入真实 AI API，重点演示“广告创意增长闭环”本身。

## 当前闭环

```text
广告 Brief -> 多版创意 -> A/B 实验 -> 投放数据看板 -> 复盘建议 -> 下一轮优化
```

## 已实现功能

- 默认载入完整示例数据，打开页面即可看到效果。
- 广告 Brief 表单：产品、行业、人群、卖点、平台、目标、风格。
- 创意工作台：4 个广告版本、广告切图预览、标题、主文案、CTA、短视频脚本、落地页首屏文案。
- 数据看板：曝光、CTR、CPA、ROI，以及创意排行。
- A/B 实验：实验假设、目标指标、胜出版本、实验结论。
- 投放复盘：总结、胜出原因、短板指标、下一轮测试方向。
- 本地持久化：使用浏览器 localStorage 保存数据。
- 响应式 H5：PC 端后台布局，移动端底部导航。

## 如何运行

直接打开：

```text
index.html
```

也可以使用任意静态服务器：

```bash
python -m http.server 8080
```

然后访问：

```text
http://localhost:8080
```

## 文件结构

```text
05-AI广告创意增长平台/
  index.html
  styles.css
  app.js
  README.md
  assets/
    creative-cut-a.svg
    creative-cut-b.svg
    creative-cut-c.svg
    creative-cut-d.svg
  docs/
    PRD.md
    DATA_MODEL.md
```

## 简历描述参考

独立设计并开发 AI 广告创意增长平台 H5 Demo，面向商业化广告投放场景，覆盖广告 Brief、AI 创意生成模拟、A/B 实验管理、投放数据看板和复盘建议。项目通过示例数据展示从创意生产到数据分析再到下一轮优化的完整增长闭环，体现对广告指标、增长实验、素材管理和 AI 产品化流程的理解。

## 后续升级方向

- 接入真实大模型 API。
- 增加后端和数据库。
- 支持 CSV 投放数据导入。
- 接入真实广告平台数据。
- 增加登录、团队协作和权限管理。
