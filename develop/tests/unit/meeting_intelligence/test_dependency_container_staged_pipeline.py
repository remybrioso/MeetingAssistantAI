from application.dependency_container import (
    chunk_knowledge_service,
    container,
    meeting_report_generator,
    staged_chunk_knowledge_service,
)
from services.staged_chunk_knowledge_service import (
    StagedChunkKnowledgeService,
)


def test_container_registers_staged_chunk_knowledge_service() -> None:
    registered = container.get(
        "staged_chunk_knowledge_service"
    )

    assert registered is staged_chunk_knowledge_service
    assert isinstance(
        registered,
        StagedChunkKnowledgeService,
    )


def test_container_keeps_generic_chunk_service_alias() -> None:
    registered = container.get(
        "chunk_knowledge_service"
    )

    assert registered is staged_chunk_knowledge_service
    assert chunk_knowledge_service is staged_chunk_knowledge_service


def test_generator_uses_registered_staged_chunk_service() -> None:
    assert (
        meeting_report_generator.chunk_knowledge_service
        is staged_chunk_knowledge_service
    )


def test_container_does_not_register_legacy_chunk_formatter() -> None:
    assert (
        container.get(
            "chunk_prompt_formatter"
        )
        is None
    )
