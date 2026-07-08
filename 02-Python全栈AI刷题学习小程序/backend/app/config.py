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

SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "mock")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
SEARCH_MAX_RESULTS = int(os.getenv("SEARCH_MAX_RESULTS", "5"))
SEARCH_DEPTH = os.getenv("SEARCH_DEPTH", "basic")
EXTRACT_DEPTH = os.getenv("EXTRACT_DEPTH", "basic")
TAVILY_TIMEOUT_SECONDS = float(os.getenv("TAVILY_TIMEOUT_SECONDS", "8"))

WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")
WECHAT_AUTH_MODE = os.getenv("WECHAT_AUTH_MODE", "mock")
AUTH_TOKEN_TTL_DAYS = int(os.getenv("AUTH_TOKEN_TTL_DAYS", "7"))

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "memory").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "")
