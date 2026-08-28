"""
probe_chunk_knowledge_synthetic.py

Prueba diagnóstica controlada del contrato chunk_knowledge_v1.
No modifica reuniones ni persiste artefactos.
"""

import json

from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from providers.ollama_provider import OllamaProvider
from services.chunk_knowledge_parser import ChunkKnowledgeParser
from services.chunk_knowledge_service import ChunkKnowledgeService
from services.chunk_prompt_formatter import ChunkPromptFormatter


class CapturingProvider:
    def __init__(self, provider: OllamaProvider) -> None:
        self.provider = provider
        self.model = provider.model
        self.last_response: str | None = None

    def generate(
        self,
        prompt: str,
        output_schema: dict | None = None,
    ) -> str:
        response = self.provider.generate(
            prompt,
            output_schema,
        )
        self.last_response = response
        return response


def build_synthetic_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=0,
        segments=[
            Segment(
                start=0.0,
                end=8.0,
                speaker="LOCAL",
                text=(
                    "El equipo aprobó migrar la base de datos "
                    "principal a la nube."
                ),
            ),
            Segment(
                start=8.0,
                end=16.0,
                speaker="REMOTE",
                text=(
                    "María debe preparar el plan de migración "
                    "antes del 30 de agosto de 2026."
                ),
            ),
            Segment(
                start=16.0,
                end=24.0,
                speaker="LOCAL",
                text=(
                    "El principal riesgo identificado es una "
                    "interrupción del servicio durante la migración."
                ),
            ),
            Segment(
                start=24.0,
                end=32.0,
                speaker="REMOTE",
                text=(
                    "Quedó pendiente confirmar la ventana de "
                    "mantenimiento con Operaciones."
                ),
            ),
            Segment(
                start=32.0,
                end=40.0,
                speaker="LOCAL",
                text=(
                    "También se revisó la arquitectura actual "
                    "y la capacidad del servidor."
                ),
            ),
        ],
    )


def main() -> int:
    chunk = build_synthetic_chunk()

    print("=== CHUNK SINTÉTICO ===")
    print(f"Rango: {chunk.start:.1f} → {chunk.end:.1f}")
    print(f"Segmentos: {len(chunk.segments)}")
    print(f"Palabras: {chunk.word_count}")

    for segment in chunk.segments:
        print(
            f"- [{segment.start:.1f}-{segment.end:.1f}] "
            f"{segment.speaker}: {segment.text}"
        )

    formatter = ChunkPromptFormatter()
    real_provider = OllamaProvider()
    capturing_provider = CapturingProvider(real_provider)

    service = ChunkKnowledgeService(
        provider=capturing_provider,
        parser=ChunkKnowledgeParser(),
    )

    prompt = formatter.format(chunk)

    print("\n=== OLLAMA ===")
    print(f"Modelo: {real_provider.model}")

    print("\n=== GENERACIÓN ===")
    print("Enviando chunk sintético con chunk_knowledge_v1...")

    try:
        knowledge = service.generate(
            prompt=prompt,
            chunk=chunk,
        )
    except Exception as ex:
        print("\nPRUEBA FALLIDA DURANTE GENERACIÓN/PARSER")
        print(f"{type(ex).__name__}: {ex}")

        if capturing_provider.last_response:
            print("\n=== RESPUESTA CRUDA DE OLLAMA ===")
            print(capturing_provider.last_response)

        raise

    print("\n=== RESPUESTA CRUDA DE OLLAMA ===")
    print(capturing_provider.last_response)

    print("\n=== CHUNK KNOWLEDGE VALIDADO ===")
    print(
        json.dumps(
            knowledge.as_dict(),
            ensure_ascii=False,
            indent=4,
        )
    )

    print("\n=== CONTEOS ===")
    for field_name in (
        "key_points",
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
        "participants",
        "conclusions",
    ):
        print(
            f"{field_name}: "
            f"{len(getattr(knowledge, field_name))}"
        )

    expected = {
        "decisions": knowledge.decisions,
        "action_items": knowledge.action_items,
        "risks": knowledge.risks,
        "pending_items": knowledge.pending_items,
    }

    missing = [
        field_name
        for field_name, values in expected.items()
        if not values
    ]

    if not knowledge.has_content:
        print("\nDIAGNÓSTICO: EXTRACCIÓN COMPLETAMENTE VACÍA.")
        return 2

    if missing:
        print("\nDIAGNÓSTICO: EXTRACCIÓN PARCIAL.")
        print(
            "Faltaron categorías explícitas: "
            + ", ".join(missing)
        )
        return 3

    print(
        "\nPRUEBA COMPLETADA: las cuatro categorías "
        "operativas explícitas fueron extraídas y validadas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
