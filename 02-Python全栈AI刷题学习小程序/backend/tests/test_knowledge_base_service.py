from app.schemas import KnowledgeBase, KnowledgeBaseChunk, SourceMeta
from app.services.knowledge_base_service import (
    create_knowledge_base,
    retrieve_chunks,
    supplement_knowledge_base,
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
