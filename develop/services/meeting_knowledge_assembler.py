"""
meeting_knowledge_assembler.py

Construye MeetingKnowledge a partir de las extracciones
individuales de todos los chunks de una reunión.
"""

from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge


class MeetingKnowledgeAssembler:
    """
    Ensambla cobertura completa sin realizar consolidación
    semántica.

    No resume, no deduplica y no reordena automáticamente.
    Un error de cobertura debe ser visible.
    """

    def assemble(
        self,
        chunks: list[ChunkKnowledge],
        source_chunk_count: int,
    ) -> MeetingKnowledge:
        if not isinstance(
            chunks,
            list,
        ):
            raise TypeError(
                "chunks debe ser una lista."
            )

        return MeetingKnowledge(
            source_chunk_count=source_chunk_count,
            chunks=chunks,
        )
