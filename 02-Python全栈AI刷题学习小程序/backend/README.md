# Backend

这是“水母diy学习助手”的 Python 后端最小可运行骨架。

## 目录说明

- `app/main.py`：后端入口文件，负责启动 HTTP 服务。
- `app/routes.py`：路由文件，负责定义接口路径和返回数据。
- `app/config.py`：配置文件，负责集中管理端口、数据库地址和 AI 配置占位。
- `requirements.txt`：Python 依赖清单。当前 Day 02 使用标准库，暂时没有外部依赖。

## 本地启动

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m app.main
```

启动后访问：

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/api/levels
http://127.0.0.1:8000/api/questions?levelId=level-1
```
