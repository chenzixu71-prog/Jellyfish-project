import os


HOST = os.getenv("APP_HOST", "127.0.0.1")
PORT = int(os.getenv("APP_PORT", "8000"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
AI_MODEL = os.getenv("AI_MODEL", "not-configured")

