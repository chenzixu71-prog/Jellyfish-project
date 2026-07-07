import logging
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from app import config


logger = logging.getLogger(__name__)

URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
MAX_CONTEXT_CHARS = 6000
MAX_SOURCE_CHARS = 1200


@dataclass
class SourceDocument:
    title: str
    url: str
    content: str
    source_type: str
    score: float | None = None


@dataclass
class SourceContext:
    documents: list[SourceDocument] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)

    @property
    def has_sources(self) -> bool:
        return bool(self.documents)


class SourceProvider(Protocol):
    def collect(self, query: str) -> SourceContext:
        ...


def extract_urls(text: str) -> list[str]:
    return [item.rstrip(").,;]}>") for item in URL_RE.findall(text)]


def build_source_context(
    content: str,
    web_search_enabled: bool,
    provider: SourceProvider | None = None,
) -> SourceContext:
    if not web_search_enabled:
        return SourceContext()
    try:
        selected_provider = provider or get_source_provider()
        return selected_provider.collect(content)
    except Exception as exc:
        warning = f"source context failed: {exc.__class__.__name__}"
        logger.warning(warning)
        return SourceContext(warnings=[warning])


def get_source_provider() -> SourceProvider:
    if config.SEARCH_PROVIDER != "tavily":
        return EmptySourceProvider("search provider is not tavily")
    if not config.TAVILY_API_KEY:
        return EmptySourceProvider("TAVILY_API_KEY is not configured")
    return TavilySourceProvider()


class EmptySourceProvider:
    def __init__(self, warning: str) -> None:
        self.warning = warning

    def collect(self, query: str) -> SourceContext:
        logger.warning(self.warning)
        return SourceContext(warnings=[self.warning])


class TavilySourceProvider:
    def __init__(self, client: Any | None = None) -> None:
        self.client = client or self._create_client()

    def _create_client(self) -> Any:
        try:
            from tavily import TavilyClient
        except ImportError as exc:
            raise RuntimeError(
                "tavily-python is required when SEARCH_PROVIDER=tavily"
            ) from exc
        return TavilyClient(api_key=config.TAVILY_API_KEY)

    def collect(self, query: str) -> SourceContext:
        context = SourceContext()
        urls = extract_urls(query)

        if urls:
            context.tool_calls.append("tavily_extract")
            context.documents.extend(self._safe_extract(urls))

        if should_search(query, urls):
            context.tool_calls.append("tavily_search")
            context.documents.extend(self._safe_search(query))

        if not context.documents and not context.warnings:
            context.warnings.append("Tavily returned no usable sources")
        return context

    def _safe_search(self, query: str) -> list[SourceDocument]:
        try:
            response = self.client.search(
                query=query,
                search_depth=choose_search_depth(query),
                max_results=choose_max_results(query),
                include_raw_content=should_include_raw_content(query),
            )
            return normalize_search_response(response)
        except Exception as exc:
            logger.warning("Tavily search failed: %s", exc.__class__.__name__)
            return []

    def _safe_extract(self, urls: list[str]) -> list[SourceDocument]:
        try:
            response = self.client.extract(
                urls=urls[:3],
                format="markdown",
                extract_depth=choose_extract_depth(urls),
            )
            return normalize_extract_response(response)
        except Exception as exc:
            logger.warning("Tavily extract failed: %s", exc.__class__.__name__)
            return []


def should_search(query: str, urls: list[str]) -> bool:
    text = query.strip()
    if not text:
        return False
    return not urls or len(text) > 120


def choose_max_results(query: str) -> int:
    configured = max(1, config.SEARCH_MAX_RESULTS)
    if is_complex_topic(query):
        return min(max(configured, 5), 8)
    return min(configured, 5)


def choose_search_depth(query: str) -> str:
    if is_complex_topic(query):
        return "advanced"
    return config.SEARCH_DEPTH


def choose_extract_depth(urls: list[str]) -> str:
    if len(urls) > 1:
        return "advanced"
    return config.EXTRACT_DEPTH


def should_include_raw_content(query: str) -> bool | str:
    if is_complex_topic(query):
        return "markdown"
    return False


def is_complex_topic(query: str) -> bool:
    lowered = query.lower()
    markers = (
        "latest",
        "new",
        "2025",
        "2026",
        "harness engineering",
        "官方",
        "最新",
        "文档",
        "论文",
    )
    return len(query) > 80 or any(marker in lowered for marker in markers)


def normalize_search_response(response: dict[str, Any]) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for item in response.get("results", []):
        content = item.get("raw_content") or item.get("content") or item.get("first_paragraph") or ""
        if not content:
            continue
        documents.append(
            SourceDocument(
                title=item.get("title") or "Untitled source",
                url=item.get("url") or "",
                content=trim_text(str(content), MAX_SOURCE_CHARS),
                source_type="search",
                score=item.get("score"),
            )
        )
    return documents


def normalize_extract_response(response: dict[str, Any]) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for item in response.get("results", []):
        content = item.get("raw_content") or item.get("content") or ""
        if not content:
            continue
        documents.append(
            SourceDocument(
                title=item.get("title") or item.get("url") or "Extracted page",
                url=item.get("url") or "",
                content=trim_text(str(content), MAX_SOURCE_CHARS),
                source_type="extract",
            )
        )
    return documents


def format_source_context(context: SourceContext) -> str:
    if not context.documents:
        return ""
    blocks: list[str] = []
    for index, document in enumerate(context.documents, start=1):
        blocks.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    f"type: {document.source_type}",
                    f"title: {document.title}",
                    f"url: {document.url}",
                    f"content: {trim_text(document.content, MAX_SOURCE_CHARS)}",
                ]
            )
        )
    return trim_text("\n\n".join(blocks), MAX_CONTEXT_CHARS)


def trim_text(text: str, limit: int) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."
