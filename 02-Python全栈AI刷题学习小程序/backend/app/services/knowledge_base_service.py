import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from app.schemas import (
    KnowledgeBase,
    KnowledgeBaseMaterial,
    KnowledgeBaseSummary,
)
from app.services.quiz_service import build_source_meta, create_quiz
from app.services.search_service import SourceContext, SourceProvider, build_source_context
from app.storage.memory_store import store


MAX_KNOWLEDGE_BASES_PER_OWNER = 5
MAX_KNOWLEDGE_CONTENT_CHARS = 12000


def create_knowledge_base(
    owner_id: str,
    content: str,
    title: str = "",
    web_search_enabled: bool = False,
    source_provider: SourceProvider | None = None,
) -> KnowledgeBase:
    normalized_content = normalize_content(content)
    if store.count_knowledge_bases(owner_id) >= MAX_KNOWLEDGE_BASES_PER_OWNER:
        raise HTTPException(status_code=400, detail="每个人最多只能创建 5 个知识库")

    source_context = build_source_context(
        normalized_content,
        web_search_enabled,
        source_provider,
    )
    now = now_iso()
    knowledge_base = KnowledgeBase(
        id=f"kb-{uuid.uuid4().hex[:12]}",
        title=build_title(title, normalized_content),
        summary=build_summary(normalized_content, source_context),
        content=build_content_with_sources(normalized_content, source_context),
        materials=[
            KnowledgeBaseMaterial(
                id=f"mat-{uuid.uuid4().hex[:10]}",
                type="text",
                name="初始知识",
                summary=trim_for_summary(normalized_content, 90),
                createdAt=now,
            )
        ],
        sourceMeta=build_source_meta(web_search_enabled, source_context),
        createdAt=now,
        updatedAt=now,
    )
    store.save_knowledge_base(owner_id, knowledge_base)
    return knowledge_base


def list_knowledge_bases(owner_id: str) -> list[KnowledgeBaseSummary]:
    return [to_summary(item) for item in store.get_knowledge_bases(owner_id)]


def get_knowledge_base(owner_id: str, knowledge_base_id: str) -> KnowledgeBase:
    knowledge_base = store.get_knowledge_base(owner_id, knowledge_base_id)
    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return knowledge_base


def supplement_knowledge_base(
    owner_id: str,
    knowledge_base_id: str,
    content: str,
    web_search_enabled: bool = False,
    source_provider: SourceProvider | None = None,
) -> KnowledgeBase:
    knowledge_base = get_knowledge_base(owner_id, knowledge_base_id)
    normalized_content = normalize_content(content)
    source_context = build_source_context(
        normalized_content,
        web_search_enabled,
        source_provider,
    )
    now = now_iso()
    supplement = build_content_with_sources(normalized_content, source_context)
    knowledge_base.content = trim_for_storage(
        f"{knowledge_base.content}\n\n[补充资料]\n{supplement}"
    )
    knowledge_base.summary = build_summary(knowledge_base.content, source_context)
    knowledge_base.updatedAt = now
    knowledge_base.materials.insert(
        0,
        KnowledgeBaseMaterial(
            id=f"mat-{uuid.uuid4().hex[:10]}",
            type="text",
            name="补充资料",
            summary=trim_for_summary(normalized_content, 90),
            createdAt=now,
        ),
    )
    if web_search_enabled:
        knowledge_base.sourceMeta = build_source_meta(True, source_context)
    store.save_knowledge_base(owner_id, knowledge_base)
    return knowledge_base


def start_quiz_from_knowledge_base(owner_id: str, knowledge_base_id: str):
    knowledge_base = get_knowledge_base(owner_id, knowledge_base_id)
    quiz_content = (
        f"请基于以下知识库生成闯关题。\n"
        f"知识库标题：{knowledge_base.title}\n"
        f"知识库摘要：{knowledge_base.summary}\n"
        f"知识库内容：\n{knowledge_base.content}"
    )
    quiz = create_quiz(owner_id, quiz_content, web_search_enabled=False)
    quiz.title = knowledge_base.title
    quiz.summary = f"基于知识库“{knowledge_base.title}”生成的 5 题闯关练习。"
    quiz.sourceMeta = knowledge_base.sourceMeta
    store.save_quiz(owner_id, quiz)
    knowledge_base.quizIds.insert(0, quiz.quizId)
    knowledge_base.updatedAt = now_iso()
    store.save_knowledge_base(owner_id, knowledge_base)
    return quiz


def to_summary(knowledge_base: KnowledgeBase) -> KnowledgeBaseSummary:
    return KnowledgeBaseSummary(
        id=knowledge_base.id,
        title=knowledge_base.title,
        summary=knowledge_base.summary,
        materialCount=len(knowledge_base.materials),
        sourceCount=knowledge_base.sourceMeta.sourceCount if knowledge_base.sourceMeta else 0,
        quizCount=len(knowledge_base.quizIds),
        updatedAt=knowledge_base.updatedAt,
    )


def build_content_with_sources(content: str, source_context: SourceContext) -> str:
    if not source_context.documents:
        return trim_for_storage(content)
    source_lines = [
        f"- {document.title}: {document.content[:500]}"
        for document in source_context.documents[:5]
    ]
    return trim_for_storage(
        f"{content}\n\n[联网资料摘要]\n" + "\n".join(source_lines)
    )


def build_title(title: str, content: str) -> str:
    cleaned_title = title.strip()
    if cleaned_title:
        return cleaned_title[:30]
    first_line = content.strip().splitlines()[0] if content.strip() else "水母知识库"
    return trim_for_summary(first_line, 18) or "水母知识库"


def build_summary(content: str, source_context: SourceContext) -> str:
    suffix = ""
    if source_context.documents:
        suffix = f" 已参考 {len(source_context.documents)} 条联网资料。"
    return f"{trim_for_summary(content, 80)}{suffix}"


def normalize_content(content: str) -> str:
    cleaned = content.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail="请至少输入知识内容")
    return trim_for_storage(cleaned)


def trim_for_storage(content: str) -> str:
    return content[:MAX_KNOWLEDGE_CONTENT_CHARS].strip()


def trim_for_summary(content: str, limit: int) -> str:
    compact = " ".join(content.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
