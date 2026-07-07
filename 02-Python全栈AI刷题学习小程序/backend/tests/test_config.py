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
