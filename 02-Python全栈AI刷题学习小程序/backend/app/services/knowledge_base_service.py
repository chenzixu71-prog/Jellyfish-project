import hashlib
import re
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from app.schemas import (
    KnowledgeBase,
    KnowledgeBaseChunk,
    KnowledgeBaseMaterial,
    KnowledgeBaseSummary,
    Question,
    Quiz,
)
from app.services.ai_service import generate_quiz
from app.services.quiz_service import build_source_meta
from app.services.search_service import (
    SourceContext,
    SourceProvider,
    build_source_context,
    is_url_only_content,
)
from app.storage.memory_store import store


MAX_KNOWLEDGE_BASES_PER_OWNER = 5
MAX_QUESTIONS_PER_KNOWLEDGE_BASE = 200
MAX_KNOWLEDGE_CONTENT_CHARS = 12000
CHUNK_WORD_SIZE = 180
CHUNK_WORD_OVERLAP = 35
MAX_RETRIEVED_CHUNKS = 5
QUESTION_BATCH_SIZE = 20
CHALLENGE_QUESTION_COUNT = 10


def create_knowledge_base(
    owner_id: str,
    content: str,
    title: str = "",
    web_search_enabled: bool = False,
    source_provider: SourceProvider | None = None,
) -> KnowledgeBase:
    normalized_content = normalize_content(content)
    require_search_for_url_only_content(normalized_content, web_search_enabled)
    if store.count_knowledge_bases(owner_id) >= MAX_KNOWLEDGE_BASES_PER_OWNER:
        raise HTTPException(status_code=400, detail="Each user can create at most 5 knowledge bases.")

    source_context = build_source_context(
        normalized_content,
        web_search_enabled,
        source_provider,
    )
    now = now_iso()
    content_with_sources = build_content_with_sources(normalized_content, source_context)
    content_hash = hash_content(content_with_sources)
    knowledge_base = KnowledgeBase(
        id=f"kb-{uuid.uuid4().hex[:12]}",
        title=build_title(title, normalized_content),
        summary=build_summary(normalized_content, source_context),
        content=content_with_sources,
        materials=[
            KnowledgeBaseMaterial(
                id=f"mat-{uuid.uuid4().hex[:10]}",
                type="text",
                name="initial knowledge",
                summary=trim_for_summary(normalized_content, 90),
                contentHash=content_hash,
                createdAt=now,
            )
        ],
        chunks=build_chunks(content_with_sources, "initial"),
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
        raise HTTPException(status_code=404, detail="Knowledge base not found.")
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
    require_search_for_url_only_content(normalized_content, web_search_enabled)
    source_context = build_source_context(
        normalized_content,
        web_search_enabled,
        source_provider,
    )
    now = now_iso()
    supplement = build_content_with_sources(normalized_content, source_context)
    content_hash = hash_content(supplement)
    if any(material.contentHash == content_hash for material in knowledge_base.materials):
        knowledge_base.updatedAt = now
        store.save_knowledge_base(owner_id, knowledge_base)
        return knowledge_base

    knowledge_base.content = trim_for_storage(
        f"{knowledge_base.content}\n\n[Supplement]\n{supplement}"
    )
    knowledge_base.summary = build_summary(knowledge_base.content, source_context)
    knowledge_base.updatedAt = now
    knowledge_base.chunks = merge_chunks(
        knowledge_base.chunks,
        build_chunks(supplement, "supplement"),
    )
    knowledge_base.materials.insert(
        0,
        KnowledgeBaseMaterial(
            id=f"mat-{uuid.uuid4().hex[:10]}",
            type="text",
            name="supplement",
            summary=trim_for_summary(normalized_content, 90),
            contentHash=content_hash,
            createdAt=now,
        ),
    )
    if web_search_enabled:
        knowledge_base.sourceMeta = build_source_meta(True, source_context)
    store.save_knowledge_base(owner_id, knowledge_base)
    return knowledge_base


def start_quiz_from_knowledge_base(owner_id: str, knowledge_base_id: str):
    knowledge_base = get_knowledge_base(owner_id, knowledge_base_id)
    retrieved_chunks = retrieve_chunks(
        knowledge_base,
        f"{knowledge_base.title}\n{knowledge_base.summary}",
    )
    retrieved_context = format_retrieved_chunks(retrieved_chunks)
    existing_stems = "\n".join(
        f"- {question.stem}" for question in knowledge_base.questions[-40:]
    ) or "- None yet"
    quiz_content = (
        "Generate quiz questions from this knowledge base only.\n"
        "Hard constraints:\n"
        "- Do not generate generic learning-method questions.\n"
        "- Every question must test one concrete detail from the retrieved chunks.\n"
        "- Every option must be related to the knowledge base domain.\n"
        "- Use retrieved chunks and included source summaries as the source of truth.\n"
        "- If the knowledge base is about a new product/tool/framework, ask about that exact product/tool/framework, not a similarly named concept.\n"
        "- Prefer concepts that appear in multiple chunks or have explicit keywords.\n\n"
        f"Knowledge base title: {knowledge_base.title}\n"
        f"Knowledge base summary: {knowledge_base.summary}\n"
        f"Most relevant knowledge chunks:\n{retrieved_context}\n\n"
        f"Full knowledge base fallback:\n{knowledge_base.content[:3500]}\n\n"
        "Existing question stems that must not be repeated:\n"
        f"{existing_stems}"
    )

    uncompleted_questions = get_uncompleted_questions(knowledge_base)
    remaining_capacity = min(
        knowledge_base.maxQuestions,
        MAX_QUESTIONS_PER_KNOWLEDGE_BASE,
    ) - len(knowledge_base.questions)
    if len(uncompleted_questions) < CHALLENGE_QUESTION_COUNT and remaining_capacity > 0:
        batch_size = min(QUESTION_BATCH_SIZE, remaining_capacity)
        generated_quiz = generate_quiz(
            quiz_content,
            question_count=batch_size,
        )
        add_questions_to_knowledge_base(
            owner_id,
            knowledge_base_id,
            generated_quiz.questions,
            source_chunk_ids=[chunk.id for chunk in retrieved_chunks],
        )

    knowledge_base = get_knowledge_base(owner_id, knowledge_base_id)
    uncompleted_questions = get_uncompleted_questions(knowledge_base)
    selected_questions = (
        uncompleted_questions[:CHALLENGE_QUESTION_COUNT]
        if uncompleted_questions
        else knowledge_base.questions[:CHALLENGE_QUESTION_COUNT]
    )
    if not selected_questions:
        raise HTTPException(status_code=502, detail="No usable questions were generated.")

    quiz = Quiz(
        title=knowledge_base.title,
        summary=f'Challenge from knowledge base "{knowledge_base.title}".',
        questions=[question.model_copy(deep=True) for question in selected_questions],
        knowledgeBaseId=knowledge_base_id,
        sourceMeta=knowledge_base.sourceMeta,
    )
    store.save_quiz(owner_id, quiz)
    knowledge_base.quizIds.insert(0, quiz.quizId)
    knowledge_base.updatedAt = now_iso()
    store.save_knowledge_base(owner_id, knowledge_base)
    return quiz


def get_uncompleted_questions(knowledge_base: KnowledgeBase) -> list[Question]:
    completed_ids = set(knowledge_base.completedQuestionIds)
    return [
        question
        for question in knowledge_base.questions
        if question.id not in completed_ids
    ]


def add_questions_to_knowledge_base(
    owner_id: str,
    knowledge_base_id: str,
    questions: list[Question],
    source_chunk_ids: list[str] | None = None,
) -> list[Question]:
    knowledge_base = get_knowledge_base(owner_id, knowledge_base_id)
    capacity = max(
        0,
        min(knowledge_base.maxQuestions, MAX_QUESTIONS_PER_KNOWLEDGE_BASE)
        - len(knowledge_base.questions),
    )
    if capacity == 0:
        return []

    fingerprints = {
        question_fingerprint(question) for question in knowledge_base.questions
    }
    question_ids = {question.id for question in knowledge_base.questions}
    accepted: list[Question] = []
    for question in questions:
        fingerprint = question_fingerprint(question)
        if fingerprint in fingerprints:
            continue

        stored_question = question.model_copy(deep=True)
        stored_question.id = f"kbq-{uuid.uuid4().hex[:16]}"
        if source_chunk_ids and not stored_question.sourceChunkIds:
            stored_question.sourceChunkIds = list(dict.fromkeys(source_chunk_ids))

        accepted.append(stored_question)
        fingerprints.add(fingerprint)
        question_ids.add(stored_question.id)
        if len(accepted) >= capacity:
            break

    if accepted:
        knowledge_base.questions.extend(accepted)
        knowledge_base.updatedAt = now_iso()
        store.save_knowledge_base(owner_id, knowledge_base)
    return accepted


def mark_question_completed(
    owner_id: str,
    knowledge_base_id: str,
    question_id: str,
) -> bool:
    knowledge_base = store.get_knowledge_base(owner_id, knowledge_base_id)
    if knowledge_base is None:
        return False
    if not any(question.id == question_id for question in knowledge_base.questions):
        return False
    if question_id in knowledge_base.completedQuestionIds:
        return False

    knowledge_base.completedQuestionIds.append(question_id)
    knowledge_base.updatedAt = now_iso()
    store.save_knowledge_base(owner_id, knowledge_base)
    return True


def fill_quiz_from_pool(
    accepted_questions: list[Question],
    pool: list[Question],
    requested_count: int,
) -> list[Question]:
    selected = list(accepted_questions)
    selected_ids = {question.id for question in selected}
    for question in pool:
        if len(selected) >= requested_count:
            break
        if question.id not in selected_ids:
            selected.append(question.model_copy(deep=True))
            selected_ids.add(question.id)
    return selected


def question_fingerprint(question: Question) -> str:
    normalized_stem = re.sub(r"\s+", " ", question.stem).strip().lower()
    return hash_content(f"{question.type}:{normalized_stem}")


def to_summary(knowledge_base: KnowledgeBase) -> KnowledgeBaseSummary:
    return KnowledgeBaseSummary(
        id=knowledge_base.id,
        title=knowledge_base.title,
        summary=knowledge_base.summary,
        materialCount=len(knowledge_base.materials),
        sourceCount=knowledge_base.sourceMeta.sourceCount if knowledge_base.sourceMeta else 0,
        quizCount=len(knowledge_base.quizIds),
        questionCount=len(knowledge_base.questions),
        completedQuestionCount=len(knowledge_base.completedQuestionIds),
        maxQuestions=knowledge_base.maxQuestions,
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
        f"{content}\n\n[Search source summaries]\n" + "\n".join(source_lines)
    )


def build_title(title: str, content: str) -> str:
    cleaned_title = title.strip()
    if cleaned_title:
        return cleaned_title[:30]
    first_line = content.strip().splitlines()[0] if content.strip() else "Jelly knowledge base"
    return trim_for_summary(first_line, 18) or "Jelly knowledge base"


def build_summary(content: str, source_context: SourceContext) -> str:
    suffix = ""
    if source_context.documents:
        suffix = f" Referenced {len(source_context.documents)} web sources."
    return f"{trim_for_summary(content, 80)}{suffix}"


def normalize_content(content: str) -> str:
    cleaned = content.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail="Knowledge content is required.")
    return trim_for_storage(cleaned)


def require_search_for_url_only_content(content: str, web_search_enabled: bool) -> None:
    if not web_search_enabled and is_url_only_content(content):
        raise HTTPException(
            status_code=422,
            detail="A URL requires web search. Enable web search or upload readable content.",
        )


def trim_for_storage(content: str) -> str:
    return content[:MAX_KNOWLEDGE_CONTENT_CHARS].strip()


def trim_for_summary(content: str, limit: int) -> str:
    compact = " ".join(content.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_content(content: str) -> str:
    return hashlib.sha256(content.strip().encode("utf-8")).hexdigest()[:16]


def build_chunks(content: str, source: str) -> list[KnowledgeBaseChunk]:
    normalized = " ".join(content.split())
    if not normalized:
        return []

    words = normalized.split()
    if len(words) <= CHUNK_WORD_SIZE:
        texts = [normalized]
    else:
        texts = []
        start = 0
        while start < len(words):
            end = min(start + CHUNK_WORD_SIZE, len(words))
            texts.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start = max(end - CHUNK_WORD_OVERLAP, start + 1)

    chunks: list[KnowledgeBaseChunk] = []
    for index, text in enumerate(texts):
        chunks.append(
            KnowledgeBaseChunk(
                id=f"chunk-{hash_content(source + ':' + str(index) + ':' + text)}",
                text=text,
                keywords=extract_keywords(text),
                source=source,
            )
        )
    return chunks


def merge_chunks(
    existing_chunks: list[KnowledgeBaseChunk],
    next_chunks: list[KnowledgeBaseChunk],
) -> list[KnowledgeBaseChunk]:
    seen = {chunk.id for chunk in existing_chunks}
    merged = list(existing_chunks)
    for chunk in next_chunks:
        if chunk.id not in seen:
            merged.append(chunk)
            seen.add(chunk.id)
    return merged[:80]


def retrieve_chunks(
    knowledge_base: KnowledgeBase,
    query: str,
    limit: int = MAX_RETRIEVED_CHUNKS,
) -> list[KnowledgeBaseChunk]:
    chunks = knowledge_base.chunks or build_chunks(knowledge_base.content, "legacy")
    scored = [(score_chunk(query, chunk), chunk) for chunk in chunks]
    scored.sort(key=lambda item: item[0], reverse=True)
    top = [chunk for score, chunk in scored if score > 0][:limit]
    if top:
        return top
    return chunks[:limit]


def score_chunk(query: str, chunk: KnowledgeBaseChunk) -> float:
    query_keywords = set(extract_keywords(query))
    chunk_keywords = set(chunk.keywords or extract_keywords(chunk.text))
    score = len(query_keywords & chunk_keywords) * 2.0
    score += len(cjk_bigrams(query) & cjk_bigrams(chunk.text)) * 0.8
    if query.strip() and query.strip() in chunk.text:
        score += 3.0
    return score


def format_retrieved_chunks(chunks: list[KnowledgeBaseChunk]) -> str:
    if not chunks:
        return "No relevant chunks found."

    lines = []
    for index, chunk in enumerate(chunks, 1):
        keywords = ", ".join(chunk.keywords[:8])
        lines.append(
            f"[Chunk {index} | source={chunk.source} | keywords={keywords}]\n{chunk.text[:1200]}"
        )
    return "\n\n".join(lines)


def extract_keywords(text: str, limit: int = 18) -> list[str]:
    lowered = text.lower()
    latin_tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", lowered)
    cjk_tokens = list(cjk_bigrams(text))
    candidates = latin_tokens + cjk_tokens
    counts: dict[str, int] = {}
    for token in candidates:
        counts[token] = counts.get(token, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [token for token, _ in ordered[:limit]]


def cjk_bigrams(text: str) -> set[str]:
    return {
        text[index:index + 2]
        for index in range(len(text) - 1)
        if all("\u4e00" <= char <= "\u9fff" for char in text[index:index + 2])
    }
