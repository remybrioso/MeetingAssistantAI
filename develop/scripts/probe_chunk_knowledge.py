"""
probe_chunk_knowledge.py

Prueba diagnóstica real del pipeline de extracción por chunks.

Selecciona, por defecto, la reunión disponible con mayor duración,
extrae un chunk concreto y lo procesa con Ollama usando el contrato
chunk_knowledge_v1.

Este script no modifica reuniones ni persiste artefactos.
"""

import argparse
import json
import sys
from pathlib import Path

from providers.ollama_provider import OllamaProvider
from services.chunk_knowledge_parser import ChunkKnowledgeParser
from services.chunk_knowledge_service import ChunkKnowledgeService
from services.chunk_prompt_formatter import ChunkPromptFormatter
from services.transcript_chunker import TranscriptChunker
from services.transcript_storage_service import TranscriptStorageService


class CapturingProvider:
    """Adaptador diagnóstico que conserva la respuesta cruda."""

    def __init__(self, provider: OllamaProvider) -> None:
        self.provider = provider
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prueba real de ChunkKnowledge sobre una "
            "transcripción existente."
        )
    )
    parser.add_argument(
        "--meeting",
        type=Path,
        default=None,
        help=(
            "Directorio meeting_* específico. Si se omite, "
            "se usa la reunión disponible con mayor duración."
        ),
    )
    parser.add_argument(
        "--chunk",
        type=int,
        default=0,
        help="Índice del chunk a procesar. Default: 0.",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=1200,
        help="Máximo de palabras por chunk. Default: 1200.",
    )
    return parser.parse_args()


def resolve_transcript_path(meeting_dir: Path) -> Path | None:
    candidates = (
        meeting_dir / ".mai" / "transcript.json",
        meeting_dir / "transcript.json",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def transcript_duration(transcript) -> float:
    if not transcript.segments:
        return 0.0
    return max(float(segment.end) for segment in transcript.segments)


def discover_meetings(storage: TranscriptStorageService):
    meetings = []
    for meeting_dir in sorted(Path("output").glob("meeting_*")):
        if not meeting_dir.is_dir():
            continue

        transcript_path = resolve_transcript_path(meeting_dir)
        if transcript_path is None:
            continue

        try:
            transcript = storage.load(transcript_path)
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            json.JSONDecodeError,
        ):
            continue

        if not transcript.segments:
            continue

        meetings.append(
            (
                meeting_dir,
                transcript_path,
                transcript,
                transcript_duration(transcript),
            )
        )

    return meetings


def select_meeting(
    storage: TranscriptStorageService,
    requested_meeting: Path | None,
):
    if requested_meeting is not None:
        meeting_dir = requested_meeting
        if not meeting_dir.is_dir():
            raise FileNotFoundError(
                f"No existe el directorio: {meeting_dir}"
            )

        transcript_path = resolve_transcript_path(meeting_dir)
        if transcript_path is None:
            raise FileNotFoundError(
                "La reunión indicada no contiene transcript.json."
            )

        transcript = storage.load(transcript_path)
        if not transcript.segments:
            raise ValueError(
                "La transcripción indicada no contiene segmentos."
            )

        return (
            meeting_dir,
            transcript_path,
            transcript,
            transcript_duration(transcript),
        )

    meetings = discover_meetings(storage)
    if not meetings:
        raise FileNotFoundError(
            "No se encontró ninguna reunión con transcript.json "
            "dentro de output/meeting_*."
        )

    return max(meetings, key=lambda item: item[3])


def format_timestamp(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def print_chunk_preview(chunk) -> None:
    print()
    print("=== CHUNK SELECCIONADO ===")
    print(f"Índice: {chunk.index}")
    print(
        "Rango: "
        f"{format_timestamp(chunk.start)} "
        f"→ {format_timestamp(chunk.end)}"
    )
    print(f"Duración: {chunk.duration:.2f} s")
    print(f"Segmentos: {len(chunk.segments)}")
    print(f"Palabras: {chunk.word_count}")

    preview_segments = chunk.segments[:2]
    if len(chunk.segments) > 2:
        preview_segments += chunk.segments[-2:]

    seen_ids = set()
    print()
    print("Vista previa:")

    for segment in preview_segments:
        segment_id = id(segment)
        if segment_id in seen_ids:
            continue
        seen_ids.add(segment_id)
        print(
            "- "
            f"[{segment.start:.2f}-{segment.end:.2f}] "
            f"{segment.speaker}: {segment.text}"
        )


def main() -> int:
    args = parse_args()

    if args.chunk < 0:
        print(
            "ERROR: --chunk no puede ser negativo.",
            file=sys.stderr,
        )
        return 2

    if args.max_words <= 0:
        print(
            "ERROR: --max-words debe ser mayor que cero.",
            file=sys.stderr,
        )
        return 2

    storage = TranscriptStorageService()

    try:
        meeting_dir, transcript_path, transcript, duration = select_meeting(
            storage=storage,
            requested_meeting=args.meeting,
        )
    except Exception as ex:
        print(
            f"ERROR seleccionando reunión: {ex}",
            file=sys.stderr,
        )
        return 1

    chunker = TranscriptChunker(max_words=args.max_words)
    chunks = chunker.chunk(transcript)

    if args.chunk >= len(chunks):
        print(
            "ERROR: índice de chunk fuera de rango. "
            f"Disponibles: 0-{len(chunks) - 1}.",
            file=sys.stderr,
        )
        return 2

    chunk = chunks[args.chunk]

    print("=== REUNIÓN SELECCIONADA ===")
    print(f"Directorio: {meeting_dir}")
    print(f"Transcript: {transcript_path}")
    print(
        "Duración total: "
        f"{format_timestamp(duration)} ({duration:.2f} s)"
    )
    print(f"Segmentos totales: {len(transcript.segments)}")
    print(f"Chunks generados: {len(chunks)}")
    print(f"max_words: {args.max_words}")

    print_chunk_preview(chunk)

    provider = OllamaProvider()
    health = provider.health()

    print()
    print("=== OLLAMA ===")
    print(f"Conectado: {health.connected}")
    print(f"Modelo encontrado: {health.model_found}")
    print(f"Modelo: {health.model}")

    if not health.connected:
        print(
            "ERROR: Ollama no está disponible.",
            file=sys.stderr,
        )
        if health.error:
            print(f"Detalle: {health.error}", file=sys.stderr)
        return 1

    if not health.model_found:
        print(
            "ERROR: el modelo configurado no está instalado.",
            file=sys.stderr,
        )
        return 1

    formatter = ChunkPromptFormatter()
    prompt = formatter.format(chunk)

    capturing_provider = CapturingProvider(provider)
    service = ChunkKnowledgeService(
        provider=capturing_provider,
        parser=ChunkKnowledgeParser(),
    )

    print()
    print("=== GENERACIÓN REAL ===")
    print("Enviando chunk a Ollama con chunk_knowledge_v1...")

    try:
        knowledge = service.generate(
            prompt=prompt,
            chunk=chunk,
        )
    except Exception as ex:
        print()
        print("=== ERROR ===")
        print(f"{type(ex).__name__}: {ex}")

        if capturing_provider.last_response is not None:
            print()
            print("=== RESPUESTA CRUDA DE OLLAMA ===")
            print(capturing_provider.last_response)

        raise

    print()
    print("=== CHUNK KNOWLEDGE VALIDADO ===")
    print(
        json.dumps(
            knowledge.as_dict(),
            ensure_ascii=False,
            indent=4,
        )
    )

    print()
    print("=== RESUMEN DE EXTRACCIÓN ===")
    print(f"key_points: {len(knowledge.key_points)}")
    print(f"topics: {len(knowledge.topics)}")
    print(f"decisions: {len(knowledge.decisions)}")
    print(f"action_items: {len(knowledge.action_items)}")
    print(f"risks: {len(knowledge.risks)}")
    print(f"pending_items: {len(knowledge.pending_items)}")
    print(f"participants: {len(knowledge.participants)}")
    print(f"conclusions: {len(knowledge.conclusions)}")

    print()
    print(
        "PRUEBA COMPLETADA: el ChunkKnowledge pasó parser "
        "y validación de evidencia."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
