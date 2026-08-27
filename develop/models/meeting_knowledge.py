"""
meeting_knowledge.py

Representación intermedia de conocimiento para una reunión
completa, construida a partir de todos sus ChunkKnowledge.
"""

from dataclasses import dataclass, field

from models.chunk_knowledge import ChunkKnowledge


@dataclass
class MeetingKnowledge:
    """
    Agrupa el conocimiento extraído de todos los chunks de una
    reunión sin resumir, deduplicar ni reinterpretar contenido.

    La colección debe representar cobertura completa:
    - exactamente source_chunk_count elementos;
    - índices contiguos;
    - orden 0..N-1.

    La consolidación semántica pertenece a una capa posterior.
    """

    source_chunk_count: int
    chunks: list[ChunkKnowledge] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        self._validate_source_chunk_count()

        if not isinstance(
            self.chunks,
            list,
        ):
            raise TypeError(
                "MeetingKnowledge chunks debe ser una lista."
            )

        self.chunks = list(
            self.chunks
        )

        self._validate_chunk_types()
        self._validate_complete_coverage()

    @property
    def analyzed_chunk_count(self) -> int:
        return len(
            self.chunks
        )

    @property
    def content_chunk_count(self) -> int:
        return sum(
            1
            for chunk in self.chunks
            if chunk.has_content
        )

    @property
    def has_content(self) -> bool:
        return any(
            chunk.has_content
            for chunk in self.chunks
        )

    @property
    def start(self) -> float:
        return self.chunks[0].start

    @property
    def end(self) -> float:
        return self.chunks[-1].end

    def as_dict(self) -> dict:
        return {
            "source_chunk_count": self.source_chunk_count,
            "analyzed_chunk_count": self.analyzed_chunk_count,
            "content_chunk_count": self.content_chunk_count,
            "start": self.start,
            "end": self.end,
            "chunks": [
                chunk.as_dict()
                for chunk in self.chunks
            ],
        }

    def _validate_source_chunk_count(self) -> None:
        if (
            not isinstance(
                self.source_chunk_count,
                int,
            )
            or isinstance(
                self.source_chunk_count,
                bool,
            )
        ):
            raise TypeError(
                "MeetingKnowledge source_chunk_count "
                "debe ser entero."
            )

        if self.source_chunk_count <= 0:
            raise ValueError(
                "MeetingKnowledge source_chunk_count "
                "debe ser mayor que cero."
            )

    def _validate_chunk_types(self) -> None:
        for index, chunk in enumerate(
            self.chunks,
            start=1,
        ):
            if not isinstance(
                chunk,
                ChunkKnowledge,
            ):
                raise TypeError(
                    "MeetingKnowledge chunks elemento "
                    f"#{index} debe ser una instancia "
                    "de ChunkKnowledge."
                )

    def _validate_complete_coverage(self) -> None:
        if len(
            self.chunks
        ) != self.source_chunk_count:
            raise ValueError(
                "MeetingKnowledge requiere cobertura completa: "
                f"se esperaban {self.source_chunk_count} chunks "
                f"y se recibieron {len(self.chunks)}."
            )

        expected_indices = list(
            range(
                self.source_chunk_count
            )
        )

        actual_indices = [
            chunk.chunk_index
            for chunk in self.chunks
        ]

        if actual_indices != expected_indices:
            raise ValueError(
                "MeetingKnowledge requiere chunks ordenados "
                "con índices contiguos desde 0. "
                f"Esperados: {expected_indices}. "
                f"Recibidos: {actual_indices}."
            )
