from app.schemas import KnowledgeBase, KnowledgeBaseChunk, Option, Question, SourceMeta
from app.services.knowledge_base_service import (
    add_questions_to_knowledge_base,
    create_knowledge_base,
    mark_question_completed,
    retrieve_chunks,
    supplement_knowledge_base,
    to_summary,
)
from app.storage.memory_store import store


def test_create_knowledge_base_builds_hash_and_chunks():
    owner_id = "kb-chunk-owner"
    store.knowledge_bases[owner_id] = []

    knowledge_base = create_knowledge_base(
        owner_id=owner_id,
        title="Harness Engineering",
        content=(
            "Harness Engineering focuses on software delivery workflows. "
            "It includes CI pipelines, CD deployments, feature flags, and service reliability."
        ),
    )

    assert knowledge_base.materials[0].contentHash
    assert knowledge_base.chunks
    assert "harness" in knowledge_base.chunks[0].keywords


def test_supplement_knowledge_base_skips_duplicate_content():
    owner_id = "kb-dedupe-owner"
    store.knowledge_bases[owner_id] = []

    knowledge_base = create_knowledge_base(
        owner_id=owner_id,
        title="Redis",
        content="Redis is an in-memory data store.",
    )
    first_count = len(knowledge_base.materials)

    first = supplement_knowledge_base(
        owner_id=owner_id,
        knowledge_base_id=knowledge_base.id,
        content="Redis persistence includes RDB snapshots and AOF logs.",
    )
    second = supplement_knowledge_base(
        owner_id=owner_id,
        knowledge_base_id=knowledge_base.id,
        content="Redis persistence includes RDB snapshots and AOF logs.",
    )

    assert len(first.materials) == first_count + 1
    assert len(second.materials) == len(first.materials)


def test_retrieve_chunks_prioritizes_matching_keywords():
    knowledge_base = KnowledgeBase(
        id="kb-test",
        title="Mixed knowledge",
        summary="Redis and HTTP notes",
        content="",
        materials=[],
        sourceMeta=SourceMeta(),
        chunks=[
            KnowledgeBaseChunk(
                id="chunk-http",
                text="HTTP status code 404 means the requested resource was not found.",
                keywords=["http", "status", "404"],
                source="test",
            ),
            KnowledgeBaseChunk(
                id="chunk-redis",
                text="Redis RDB snapshots save point-in-time copies of in-memory data.",
                keywords=["redis", "rdb", "snapshots"],
                source="test",
            ),
        ],
    )

    top = retrieve_chunks(knowledge_base, "Redis persistence RDB", limit=1)

    assert top[0].id == "chunk-redis"


def build_question(index: int, stem: str | None = None) -> Question:
    return Question(
        id=f"generated-{index}",
        type="single",
        stem=stem or f"Question {index}",
        options=[Option(key="A", text="Right"), Option(key="B", text="Wrong")],
        answer=["A"],
        explanation="Explanation",
        knowledge_point=f"Point {index}",
        difficulty="easy",
    )


def test_question_pool_deduplicates_and_caps_at_two_hundred():
    owner_id = "kb-question-pool-owner"
    store.knowledge_bases[owner_id] = []
    knowledge_base = create_knowledge_base(owner_id, "Question pool", "Source material")

    questions = [build_question(index) for index in range(205)]
    questions.append(build_question(999, stem="Question 0"))
    accepted = add_questions_to_knowledge_base(
        owner_id,
        knowledge_base.id,
        questions,
        source_chunk_ids=["chunk-source"],
    )

    updated = store.get_knowledge_base(owner_id, knowledge_base.id)
    assert updated is not None
    assert len(accepted) == 200
    assert len(updated.questions) == 200
    assert len({question.id for question in updated.questions}) == 200
    assert all(question.sourceChunkIds == ["chunk-source"] for question in updated.questions)

    summary = to_summary(updated)
    assert summary.questionCount == 200
    assert summary.completedQuestionCount == 0
    assert summary.maxQuestions == 200


def test_mark_question_completed_counts_each_question_once():
    owner_id = "kb-progress-owner"
    store.knowledge_bases[owner_id] = []
    knowledge_base = create_knowledge_base(owner_id, "Progress", "Source material")
    accepted = add_questions_to_knowledge_base(
        owner_id,
        knowledge_base.id,
        [build_question(1)],
    )

    assert mark_question_completed(owner_id, knowledge_base.id, accepted[0].id) is True
    assert mark_question_completed(owner_id, knowledge_base.id, accepted[0].id) is False
    assert mark_question_completed(owner_id, knowledge_base.id, "missing") is False

    updated = store.get_knowledge_base(owner_id, knowledge_base.id)
    assert updated is not None
    assert updated.completedQuestionIds == [accepted[0].id]
    assert to_summary(updated).completedQuestionCount == 1
