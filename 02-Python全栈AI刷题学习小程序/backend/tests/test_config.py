import importlib

import app.config as config_module


def reload_config_with_search_env(monkeypatch, values: dict[str, str]):
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return importlib.reload(config_module)


def test_search_config_reads_tavily_environment_values(monkeypatch):
    config = reload_config_with_search_env(
        monkeypatch,
        {
            "SEARCH_PROVIDER": "tavily",
            "TAVILY_API_KEY": "test-tavily-key",
            "SEARCH_MAX_RESULTS": "7",
            "SEARCH_DEPTH": "advanced",
            "EXTRACT_DEPTH": "advanced",
            "TAVILY_TIMEOUT_SECONDS": "12.5",
        },
    )

    assert config.SEARCH_PROVIDER == "tavily"
    assert config.TAVILY_API_KEY == "test-tavily-key"
    assert config.SEARCH_MAX_RESULTS == 7
    assert config.SEARCH_DEPTH == "advanced"
    assert config.EXTRACT_DEPTH == "advanced"
    assert config.TAVILY_TIMEOUT_SECONDS == 12.5


def test_search_config_supports_mock_provider_without_api_key(monkeypatch):
    config = reload_config_with_search_env(
        monkeypatch,
        {
            "SEARCH_PROVIDER": "mock",
            "TAVILY_API_KEY": "",
            "SEARCH_MAX_RESULTS": "3",
            "SEARCH_DEPTH": "basic",
            "EXTRACT_DEPTH": "basic",
            "TAVILY_TIMEOUT_SECONDS": "5",
        },
    )

    assert config.SEARCH_PROVIDER == "mock"
    assert config.TAVILY_API_KEY == ""
    assert config.SEARCH_MAX_RESULTS == 3
    assert config.SEARCH_DEPTH == "basic"
    assert config.EXTRACT_DEPTH == "basic"
    assert config.TAVILY_TIMEOUT_SECONDS == 5


def test_production_configuration_reports_missing_release_settings(monkeypatch):
    monkeypatch.setattr(config_module, "ENVIRONMENT", "production")
    monkeypatch.setattr(config_module, "HOST", "127.0.0.1")
    monkeypatch.setattr(config_module, "AI_PROVIDER", "mock")
    monkeypatch.setattr(config_module, "DEEPSEEK_API_KEY", "")
    monkeypatch.setattr(config_module, "SEARCH_PROVIDER", "mock")
    monkeypatch.setattr(config_module, "TAVILY_API_KEY", "")
    monkeypatch.setattr(config_module, "WECHAT_AUTH_MODE", "mock")
    monkeypatch.setattr(config_module, "WECHAT_APP_ID", "")
    monkeypatch.setattr(config_module, "WECHAT_APP_SECRET", "")
    monkeypatch.setattr(config_module, "STORAGE_BACKEND", "memory")
    monkeypatch.setattr(config_module, "DATABASE_URL", "")
    monkeypatch.setattr(config_module, "CORS_ORIGINS", ["*"])

    errors = config_module.production_configuration_errors()

    assert len(errors) == 6
    assert any("APP_HOST" in error for error in errors)
    assert any("DEEPSEEK_API_KEY" in error for error in errors)
    assert any("TAVILY_API_KEY" in error for error in errors)
    assert any("WECHAT_APP_ID" in error for error in errors)
    assert any("DATABASE_URL" in error for error in errors)
    assert any("CORS_ORIGINS" in error for error in errors)


def test_production_configuration_accepts_complete_release_settings(monkeypatch):
    monkeypatch.setattr(config_module, "ENVIRONMENT", "production")
    monkeypatch.setattr(config_module, "HOST", "0.0.0.0")
    monkeypatch.setattr(config_module, "AI_PROVIDER", "deepseek")
    monkeypatch.setattr(config_module, "DEEPSEEK_API_KEY", "deepseek-test")
    monkeypatch.setattr(config_module, "SEARCH_PROVIDER", "tavily")
    monkeypatch.setattr(config_module, "TAVILY_API_KEY", "tavily-test")
    monkeypatch.setattr(config_module, "WECHAT_AUTH_MODE", "wechat")
    monkeypatch.setattr(config_module, "WECHAT_APP_ID", "wx-test")
    monkeypatch.setattr(config_module, "WECHAT_APP_SECRET", "wechat-test")
    monkeypatch.setattr(config_module, "STORAGE_BACKEND", "mysql")
    monkeypatch.setattr(config_module, "DATABASE_URL", "mysql+pymysql://test")
    monkeypatch.setattr(config_module, "CORS_ORIGINS", ["https://servicewechat.com"])

    assert config_module.production_configuration_errors() == []
    config_module.validate_runtime_configuration()
