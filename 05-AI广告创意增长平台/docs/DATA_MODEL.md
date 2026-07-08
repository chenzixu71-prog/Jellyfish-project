# 数据模型设计

当前版本为前端 localStorage 原型。后续接后端时可按以下表结构设计。

## ad_briefs

| 字段 | 说明 |
| --- | --- |
| id | Brief ID |
| productName | 产品名称 |
| industry | 行业 |
| audience | 目标人群 |
| sellingPoints | 核心卖点 |
| platform | 投放平台 |
| goal | 转化目标 |
| tone | 文案风格 |
| createdAt | 创建时间 |

## ad_creatives

| 字段 | 说明 |
| --- | --- |
| id | 创意 ID |
| briefId | 所属 Brief |
| version | 版本，如 A/B/C |
| headline | 广告标题 |
| body | 主文案 |
| cta | 行动召唤 |
| videoScript | 短视频脚本 |
| landingHero | 落地页首屏文案 |
| angle | 主卖点角度 |
| status | active / archived / favorite |

## experiments

| 字段 | 说明 |
| --- | --- |
| id | 实验 ID |
| name | 实验名称 |
| hypothesis | 实验假设 |
| goalMetric | 目标指标 |
| controlCreativeId | 对照组 |
| variantCreativeIds | 实验组 |
| status | running / completed |
| winnerCreativeId | 胜出版本 |

## campaign_metrics

| 字段 | 说明 |
| --- | --- |
| id | 数据 ID |
| creativeId | 创意 ID |
| impressions | 曝光 |
| clicks | 点击 |
| spend | 花费 |
| conversions | 转化 |
| revenue | 收入 |
| date | 日期 |

## ai_reports

| 字段 | 说明 |
| --- | --- |
| id | 报告 ID |
| experimentId | 关联实验 |
| summary | 总结 |
| winningReason | 胜出原因 |
| weakMetric | 短板指标 |
| nextTests | 下一轮测试建议 |
| createdAt | 创建时间 |
