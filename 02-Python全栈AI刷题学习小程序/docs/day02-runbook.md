# Day 02 跑通 Python 小程序项目的后端和前端

## 今天目标

先把项目 A 拆成两个明确部分：

- `backend/`：Python 后端，负责接口、配置、后续数据库和 AI 调用。
- `miniprogram/`：微信小程序前端，负责页面展示和用户操作。

## 后端入口

入口文件：

```text
backend/app/main.py
```

启动命令：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m app.main
```

## 路由文件

路由文件：

```text
backend/app/routes.py
```

当前接口：

```text
GET /health
GET /api/levels
GET /api/questions?levelId=level-1
```

## 数据库配置位置

配置文件：

```text
backend/app/config.py
```

当前只是占位：

```text
DATABASE_URL=sqlite:///dev.db
```

后续接 MySQL 或 PostgreSQL 时，优先改这里或 `.env`。

## 小程序页面目录

```text
miniprogram/pages/levels    关卡页
miniprogram/pages/quiz      答题页
miniprogram/pages/result    结果页
miniprogram/pages/profile   个人中心页
```

## Day 02 验收

- 后端能启动。
- 浏览器能访问 `/health`。
- 小程序目录能被微信开发者工具导入。
- README 写清启动命令。

