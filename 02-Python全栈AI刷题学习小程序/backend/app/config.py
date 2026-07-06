import os

from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv("APP_HOST", "127.0.0.1")
PORT = int(os.getenv("APP_PORT", "8010"))

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
AI_PROVIDER = os.getenv("AI_PROVIDER", "mock")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-v4-flash")
AI_REPORT_MODEL = os.getenv("AI_REPORT_MODEL", "deepseek-v4-pro")

WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")
WECHAT_AUTH_MODE = os.getenv("WECHAT_AUTH_MODE", "mock")
AUTH_TOKEN_TTL_DAYS = int(os.getenv("AUTH_TOKEN_TTL_DAYS", "7"))
