# Backend

这是“水母diy学习助手”的 Python FastAPI 后端。

当前阶段先使用 mock AI 跑通核心闭环：

```text
生成题目 -> 提交答案 -> 生成报告
```

## 目录说明

- `app/main.py`：FastAPI 应用入口。
- `app/routes.py`：接口路由。
- `app/config.py`：端口和 AI 配置。
- `app/schemas.py`：Pydantic 请求/响应模型。
- `app/services/`：业务逻辑和 mock AI。
- `app/storage/`：MVP 内存存储。
- `tests/`：pytest 接口测试。
- `requirements.txt`：Python 依赖清单。

## 本地启动

```powershell
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

核心接口：

```text
POST /api/generate-quiz
POST /api/submit-answer
POST /api/generate-report
```

## 运行测试

```powershell
cd backend
.venv\Scripts\python.exe -m pytest -q
```

当前验收：

```text
5 passed
```
