# OpenSpec Project Notes

## Product

水母diy学习助手：把用户想学的知识转成可闯关、可即时讲解、可复盘报告的微信小程序学习体验。

## Current Stack

- Frontend: Taro 4.x + React + TypeScript, first target is WeChat Mini Program.
- Backend: Python FastAPI-style API modules.
- AI: backend-only model calls, currently DeepSeek-compatible chat completions with mock fallback.
- Storage: current implementation uses in-memory/local structures; formal user data path plans for MySQL.

## Architecture Principles

- 小程序前端不保存真实 AI Key。
- AI 调用、prompt、JSON 校验、重试、来源记录都放在后端。
- 核心链路保持：用户输入知识 -> AI 生成题目 -> 用户答题 -> 生成报告。
- 新能力先通过 OpenSpec 提案确认，再进入开发。

## Quality Rules

- AI 输出必须是可解析、可校验的结构化 JSON。
- 对新知识、冷门知识、歧义词，不能只依赖模型训练记忆。
- 题目、答案、讲解应尽量绑定可追溯来源。
- 证据不足时，应要求用户补充材料或明确主题，而不是硬编题目。
