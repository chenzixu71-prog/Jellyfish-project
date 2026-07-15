# Generated Asset Pack Spec

## 候选阶段资产

| ID | 资产 | 用途 | 生成要求 | 导出 |
|---|---|---|---|---|
| VA-01 | 三方向视觉情绪板 | GATE-2 选型 | 统一构图展示 A/B/C，不承担精确 UI 文案 | JPG/PNG 2x |
| VA-02 | 证据信号主视觉 | 空状态与报告封面 | 抽象检索束、证据页片、引用括号；无文字、无 Logo | PNG 透明底 1x/2x |
| VA-03 | 诊断空状态插图 | 无诊断或等待运行 | 低复杂度、可裁切、中心留白 | PNG 透明底 1x/2x |
| VA-04 | Partial Success 插图 | 部分成功提示 | 不用警报三角堆叠，表现断裂后可续接 | PNG 透明底 1x/2x |
| VA-05 | Report Cover Texture | 分享/报告封面 | 可平铺、低对比、不影响文字 | WEBP/PNG 2x |
| VA-06 | Brand Motif Sheet | 品牌边角与小型图形 | 6 个独立元素，纯色轮廓，避免渐变球 | PNG 透明底 + Figma trace reference |

## 抠底流程

1. 生图时使用与主体明显分离的纯色 chroma-key 背景。
2. 使用 imagegen Skill 自带 `remove_chroma_key.py` 去底，不用 Python 对 UI 截图补字或放大。
3. 检查 alpha 边缘、半透明毛边、孤立像素和 1x/2x 尺寸一致性。
4. 源图保存在 `assets/source/`；透明底导出到 `assets/export/1x/` 和 `assets/export/2x/`。
5. 资产清单记录 prompt、生成日期、用途、尺寸、背景移除状态和 Figma node id。

## Gate Rule

候选阶段只生成 VA-01 和每个方向一张 VA-02 样例。用户确定方向后，才批量生成 VA-03 至 VA-06，避免为被淘汰风格制作无用素材。
