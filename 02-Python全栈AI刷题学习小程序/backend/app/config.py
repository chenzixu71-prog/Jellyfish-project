import os

from dotenv import load_dotenv


load_dotenv()

ENVIRONMENT = os.getenv("APP_ENV", "development").lower()
HOST = os.getenv("APP_HOST", "127.0.0.1")
PORT = int(os.getenv("APP_PORT", "8010"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

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


def production_configuration_errors() -> list[str]:
    if ENVIRONMENT != "production":
        return []

    errors: list[str] = []
    if HOST in {"127.0.0.1", "localhost"}:
        errors.append("APP_HOST must listen on 0.0.0.0 in production")
    if AI_PROVIDER != "deepseek" or not DEEPSEEK_API_KEY:
        errors.append("AI_PROVIDER=deepseek and DEEPSEEK_API_KEY are required")
    if SEARCH_PROVIDER != "tavily" or not TAVILY_API_KEY:
        errors.append("SEARCH_PROVIDER=tavily and TAVILY_API_KEY are required")
    if WECHAT_AUTH_MODE != "wechat" or not WECHAT_APP_ID or not WECHAT_APP_SECRET:
        errors.append(
            "WECHAT_AUTH_MODE=wechat, WECHAT_APP_ID and WECHAT_APP_SECRET are required"
        )
    if STORAGE_BACKEND != "mysql" or not DATABASE_URL:
        errors.append("STORAGE_BACKEND=mysql and DATABASE_URL are required")
    if not CORS_ORIGINS or "*" in CORS_ORIGINS:
        errors.append("CORS_ORIGINS must contain explicit HTTPS origins")
    return errors


def validate_runtime_configuration() -> None:
    supported_values = {
        "AI_PROVIDER": (AI_PROVIDER, {"mock", "deepseek"}),
        "SEARCH_PROVIDER": (SEARCH_PROVIDER, {"mock", "tavily"}),
        "WECHAT_AUTH_MODE": (WECHAT_AUTH_MODE, {"mock", "wechat"}),
        "STORAGE_BACKEND": (STORAGE_BACKEND, {"memory", "mysql"}),
    }
    errors = [
        f"{name}={value} is unsupported"
        for name, (value, allowed) in supported_values.items()
        if value not in allowed
    ]
    errors.extend(production_configuration_errors())
    if errors:
        raise RuntimeError("Invalid runtime configuration: " + "; ".join(errors))
