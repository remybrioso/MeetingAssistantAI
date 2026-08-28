"""
probe_chunk_knowledge_contract_v2.py

Prueba diagnóstica de una posible evolución de chunk_knowledge_v1.

Objetivo:
- no pedir al LLM speaker/start/end/excerpt;
- entregar segmentos con segment_id estable;
- pedir al LLM únicamente referencias por segment_id;
- comprobar si una clasificación más exclusiva reduce
  decisiones/acciones/riesgos/pendientes falsos.

Este script NO modifica contratos de producción, reuniones ni artefactos.
"""

import json

from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from providers.ollama_provider import OllamaProvider


def build_chunk() -> TranscriptChunk:
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


def build_prompt(
    chunk: TranscriptChunk,
) -> str:
    segments = [
        {
            "segment_id": index,
            "speaker": segment.speaker,
            "text": segment.text,
        }
        for index, segment in enumerate(
            chunk.segments
        )
    ]

    serialized_segments = json.dumps(
        segments,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Analiza únicamente los segmentos de reunión incluidos al final.

Tu tarea es extraer conocimiento estructurado verificable.

REGLA DE EVIDENCIA:
- Cada segmento tiene un segment_id.
- Nunca devuelvas speaker, start, end ni excerpt como evidencia.
- Para respaldar un elemento devuelve únicamente segment_ids existentes.
- No inventes segment_ids.

CLASIFICACIÓN:
- topics: asuntos sustantivos tratados.
- decisions: únicamente decisiones explícitamente aprobadas, adoptadas,
  aceptadas, rechazadas o seleccionadas.
- action_items: únicamente tareas o compromisos concretos que alguien
  debe ejecutar después o como siguiente paso.
- risks: únicamente riesgos, problemas, bloqueos o impedimentos explícitos.
- pending_items: únicamente asuntos explícitamente abiertos, pendientes,
  sin resolver o por confirmar.
- key_points: hechos globalmente relevantes del bloque.

EXCLUSIVIDAD SEMÁNTICA:
No copies automáticamente una misma frase en varias categorías operativas.

Ejemplos:
- "Se aprobó migrar el sistema." -> decision, NO action_item.
- "Ana debe preparar el plan." -> action_item, NO decision.
- "Existe riesgo de interrupción." -> risk, NO decision.
- "Quedó pendiente confirmar la fecha." -> pending_item, NO decision.
- "Se revisó la arquitectura." -> topic/key_point; NO decision,
  NO action_item y NO pending_item.

Una misma evidencia puede aparecer en más de una categoría solo cuando
el segmento expresa literalmente más de una proposición distinta.

ACCIONES:
- owner: usa el nombre explícito del responsable; de lo contrario null.
- due_date: usa YYYY-MM-DD únicamente si la fecha completa es explícita.
- status: pending cuando la tarea está claramente pendiente de ejecución;
  de lo contrario unknown.

Devuelve únicamente el JSON solicitado.

SEGMENTOS:

{serialized_segments}
""".strip()


def build_schema() -> dict:
    evidence_ids = {
        "type": "array",
        "items": {
            "type": "integer",
            "minimum": 0,
        },
        "minItems": 1,
    }

    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "key_points",
            "topics",
            "decisions",
            "action_items",
            "risks",
            "pending_items",
        ],
        "properties": {
            "key_points": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "topics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "title",
                        "summary",
                        "segment_ids",
                    ],
                    "properties": {
                        "title": {
                            "type": "string",
                        },
                        "summary": {
                            "type": "string",
                        },
                        "segment_ids": evidence_ids,
                    },
                },
            },
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "description",
                        "rationale",
                        "segment_ids",
                    ],
                    "properties": {
                        "description": {
                            "type": "string",
                        },
                        "rationale": {
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                        "segment_ids": evidence_ids,
                    },
                },
            },
            "action_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "description",
                        "owner",
                        "due_date",
                        "status",
                        "segment_ids",
                    ],
                    "properties": {
                        "description": {
                            "type": "string",
                        },
                        "owner": {
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                        "due_date": {
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                        "status": {
                            "type": "string",
                            "enum": [
                                "unknown",
                                "pending",
                                "completed",
                                "cancelled",
                            ],
                        },
                        "segment_ids": evidence_ids,
                    },
                },
            },
            "risks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "description",
                        "impact",
                        "segment_ids",
                    ],
                    "properties": {
                        "description": {
                            "type": "string",
                        },
                        "impact": {
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                        "segment_ids": evidence_ids,
                    },
                },
            },
            "pending_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "description",
                        "segment_ids",
                    ],
                    "properties": {
                        "description": {
                            "type": "string",
                        },
                        "segment_ids": evidence_ids,
                    },
                },
            },
        },
    }


def validate_segment_ids(
    data: dict,
    chunk: TranscriptChunk,
) -> list[str]:
    errors = []
    maximum_id = len(
        chunk.segments
    ) - 1

    for field_name in (
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
    ):
        for item_index, item in enumerate(
            data[field_name],
            start=1,
        ):
            for segment_id in item[
                "segment_ids"
            ]:
                if (
                    not isinstance(
                        segment_id,
                        int,
                    )
                    or isinstance(
                        segment_id,
                        bool,
                    )
                    or segment_id < 0
                    or segment_id > maximum_id
                ):
                    errors.append(
                        f"{field_name} #{item_index}: "
                        f"segment_id inválido "
                        f"{segment_id}."
                    )

    return errors


def print_evidence_resolution(
    data: dict,
    chunk: TranscriptChunk,
) -> None:
    print(
        "\n=== EVIDENCIA RESUELTA POR EL SISTEMA ==="
    )

    for field_name in (
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
    ):
        print(
            f"\n{field_name}:"
        )

        if not data[field_name]:
            print(
                "  []"
            )
            continue

        for item_index, item in enumerate(
            data[field_name],
            start=1,
        ):
            print(
                f"  #{item_index}"
            )

            for segment_id in item[
                "segment_ids"
            ]:
                segment = chunk.segments[
                    segment_id
                ]

                print(
                    "    "
                    f"segment_id={segment_id} "
                    f"[{segment.start:.1f}-{segment.end:.1f}] "
                    f"{segment.speaker}: "
                    f"{segment.text}"
                )


def evaluate_semantics(
    data: dict,
) -> list[str]:
    errors = []

    expected_counts = {
        "decisions": 1,
        "action_items": 1,
        "risks": 1,
        "pending_items": 1,
    }

    for field_name, expected_count in (
        expected_counts.items()
    ):
        actual_count = len(
            data[field_name]
        )

        if actual_count != expected_count:
            errors.append(
                f"{field_name}: se esperaba "
                f"{expected_count}, se obtuvo "
                f"{actual_count}."
            )

    if data["decisions"]:
        if data["decisions"][0][
            "segment_ids"
        ] != [
            0
        ]:
            errors.append(
                "decisions debe estar respaldado "
                "únicamente por segment_id 0."
            )

    if data["action_items"]:
        action = data[
            "action_items"
        ][0]

        if action[
            "segment_ids"
        ] != [
            1
        ]:
            errors.append(
                "action_items debe estar respaldado "
                "únicamente por segment_id 1."
            )

        owner = action[
            "owner"
        ]

        if (
            not isinstance(
                owner,
                str,
            )
            or owner.strip().casefold()
            != "maría".casefold()
        ):
            errors.append(
                "La acción no identificó correctamente "
                "a María como owner."
            )

        if action[
            "due_date"
        ] != "2026-08-30":
            errors.append(
                "La acción no normalizó correctamente "
                "due_date=2026-08-30."
            )

    if data["risks"]:
        if data["risks"][0][
            "segment_ids"
        ] != [
            2
        ]:
            errors.append(
                "risks debe estar respaldado "
                "únicamente por segment_id 2."
            )

    if data["pending_items"]:
        if data["pending_items"][0][
            "segment_ids"
        ] != [
            3
        ]:
            errors.append(
                "pending_items debe estar respaldado "
                "únicamente por segment_id 3."
            )

    return errors


def main() -> int:
    chunk = build_chunk()

    print(
        "=== CONTRATO DIAGNÓSTICO V2 ==="
    )
    print(
        f"Segmentos: {len(chunk.segments)}"
    )
    print(
        f"Palabras: {chunk.word_count}"
    )

    for index, segment in enumerate(
        chunk.segments
    ):
        print(
            f"- segment_id={index} "
            f"[{segment.start:.1f}-{segment.end:.1f}] "
            f"{segment.speaker}: "
            f"{segment.text}"
        )

    provider = OllamaProvider()

    print(
        "\n=== OLLAMA ==="
    )
    print(
        f"Modelo: {provider.model}"
    )

    print(
        "\n=== GENERACIÓN ==="
    )
    print(
        "Probando clasificación exclusiva + "
        "evidencia por segment_id..."
    )

    response = provider.generate(
        build_prompt(
            chunk
        ),
        build_schema(),
    )

    print(
        "\n=== RESPUESTA CRUDA ==="
    )
    print(
        response
    )

    try:
        data = json.loads(
            response
        )
    except json.JSONDecodeError as ex:
        print(
            "\nDIAGNÓSTICO: JSON INVÁLIDO."
        )
        print(
            ex
        )
        return 2

    grounding_errors = (
        validate_segment_ids(
            data=data,
            chunk=chunk,
        )
    )

    if grounding_errors:
        print(
            "\n=== ERRORES DE SEGMENT_ID ==="
        )

        for error in grounding_errors:
            print(
                f"- {error}"
            )

        return 3

    print_evidence_resolution(
        data=data,
        chunk=chunk,
    )

    semantic_errors = (
        evaluate_semantics(
            data
        )
    )

    print(
        "\n=== CONTEOS ==="
    )

    for field_name in (
        "key_points",
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
    ):
        print(
            f"{field_name}: "
            f"{len(data[field_name])}"
        )

    if semantic_errors:
        print(
            "\nDIAGNÓSTICO: EL GROUNDING MECÁNICO "
            "FUNCIONA, PERO LA CLASIFICACIÓN "
            "SIGUE SIENDO INCORRECTA."
        )

        for error in semantic_errors:
            print(
                f"- {error}"
            )

        return 4

    print(
        "\nPRUEBA COMPLETADA: el modelo respetó "
        "clasificación exclusiva y segment_ids. "
        "La evidencia puede ser reconstruida "
        "determinísticamente por MAI."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
