from app.services.search_service import (
    TavilySourceProvider,
    SourceDocument,
    SourceContext,
    build_source_context,
    choose_max_results,
    extract_urls,
    format_source_context,
    normalize_extract_response,
    normalize_search_response,
)
from app.services.quiz_service import build_source_meta


class FakeProvider:
    def collect(self, query: str) -> SourceContext:
        return SourceContext(
            documents=[
                SourceDocument(
                    title="Harness Engineering",
                    url="https://example.com/harness-engineering",
                    content="Harness Engineering is a modern software delivery topic.",
                    source_type="search",
                )
            ],
            tool_calls=["tavily_search"],
        )


class FakeTavilyClient:
    def __init__(self) -> None:
        self.search_calls = []
        self.extract_calls = []

    def search(self, **kwargs):
        self.search_calls.append(kwargs)
        return {
            "results": [
                {
                    "title": "Harness docs",
                    "url": "https://developer.harness.io/docs",
                    "content": "Harness platform documentation content.",
                    "score": 0.9,
                }
            ]
        }

    def extract(self, **kwargs):
        self.extract_calls.append(kwargs)
        return {
            "results": [
                {
                    "url": "https://developer.harness.io/docs",
                    "raw_content": "Extracted Harness page content.",
                }
            ],
            "failed_results": [],
        }


def test_extract_urls_finds_http_urls():
    assert extract_urls("Read https://example.com/a and http://b.test/x.") == [
        "https://example.com/a",
        "http://b.test/x",
    ]


def test_build_source_context_uses_injected_provider():
    context = build_source_context(
        "Harness Engineering",
        web_search_enabled=True,
        provider=FakeProvider(),
    )

    assert context.has_sources is True
    assert context.tool_calls == ["tavily_search"]
    assert context.documents[0].title == "Harness Engineering"


def test_build_source_context_disabled_returns_empty_context():
    class ProviderThatMustNotRun:
        def __init__(self):
            self.calls = 0

        def collect(self, query: str) -> SourceContext:
            self.calls += 1
            raise AssertionError("search provider must not run while disabled")

    provider = ProviderThatMustNotRun()
    context = build_source_context(
        "Harness Engineering",
        web_search_enabled=False,
        provider=provider,
    )

    assert context.has_sources is False
    assert context.tool_calls == []
    assert provider.calls == 0


def test_tavily_provider_extracts_url_and_searches_long_query():
    client = FakeTavilyClient()
    provider = TavilySourceProvider(client=client)

    context = provider.collect(
        "Please learn this new topic in detail: https://developer.harness.io/docs "
        "and compare it with current software delivery concepts."
    )

    assert "tavily_extract" in context.tool_calls
    assert "tavily_search" in context.tool_calls
    assert client.extract_calls[0]["urls"] == ["https://developer.harness.io/docs"]
    assert len(context.documents) == 2


def test_normalize_tavily_responses():
    search_docs = normalize_search_response(
        {
            "results": [
                {
                    "title": "A",
                    "url": "https://a.test",
                    "raw_content": "Search content",
                    "score": 0.8,
                }
            ]
        }
    )
    extract_docs = normalize_extract_response(
        {
            "results": [
                {
                    "url": "https://b.test",
                    "raw_content": "Extract content",
                }
            ]
        }
    )

    assert search_docs[0].source_type == "search"
    assert extract_docs[0].source_type == "extract"


def test_format_source_context_limits_and_labels_sources():
    context = SourceContext(
        documents=[
            SourceDocument(
                title="Doc",
                url="https://example.com",
                content="Fresh source text",
                source_type="search",
            )
        ]
    )

    formatted = format_source_context(context)

    assert "[Source 1]" in formatted
    assert "Fresh source text" in formatted


def test_build_source_meta_exposes_visible_source_summary():
    context = SourceContext(
        documents=[
            SourceDocument(
                title="Harness Docs",
                url="https://developer.harness.io/docs",
                content="Harness Engineering is a software delivery topic for modern teams.",
                source_type="search",
            )
        ],
        tool_calls=["tavily_search"],
    )

    meta = build_source_meta(True, context)

    assert meta.enabled is True
    assert meta.sourceCount == 1
    assert meta.toolCalls == ["tavily_search"]
    assert meta.sources[0].title == "Harness Docs"
    assert "software delivery" in meta.sources[0].summary


def test_complex_topic_uses_at_least_five_results():
    assert choose_max_results("latest Harness Engineering updates in 2026") >= 5
