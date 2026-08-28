"""
probe_chunk_knowledge_contract_v3_staged.py

Prueba diagnóstica por etapas para modelos pequeños y equipos limitados.

Etapa 1:
- clasifica conocimiento en una lista plana;
- cada proposición aparece una sola vez;
- el LLM devuelve kind, description y segment_ids.

Etapa 2:
- solo para items kind=action;
- extrae owner, due_date y status desde los segmentos que respaldan la acción.

La evidencia completa se reconstruye determinísticamente desde segment_ids.
No modifica contratos de producción, reuniones ni artefactos.
"""

import argparse
import json
import time

from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from providers.ollama_provider import OllamaProvider


EXPECTED_KIND_BY_SEGMENT = {
    0: "decision",
    1: "action",
    2: "risk",
    3: "pending",
    4: "topic",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prueba staged para clasificación y "
            "enriquecimiento de acciones."
        )
    )
    parser.add_argument(
        "--model",
        default="qwen2.5:3b",
        help="Modelo Ollama. Default: qwen2.5:3b.",
    )
    return parser.parse_args()


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


def build_classification_prompt(
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
        separators=(",", ":"),
    )

    return f"""
Clasifica conocimiento de reunión usando SOLO los segmentos dados.

Devuelve cada proposición relevante UNA SOLA VEZ.

kind permitido:
- decision: decisión explícitamente aprobada, adoptada, rechazada o elegida.
- action: tarea o compromiso concreto que alguien debe ejecutar.
- risk: riesgo, problema, bloqueo o impedimento explícito.
- pending: asunto explícitamente pendiente, abierto o por confirmar.
- topic: asunto sustantivo tratado que no pertenece a las clases anteriores.

PRIORIDAD:
1. decisión explícita -> decision
2. tarea concreta asignada -> action
3. riesgo/problema -> risk
4. asunto pendiente/por confirmar -> pending
5. otro asunto sustantivo -> topic

No dupliques la misma proposición entre clases.

segment_ids:
- usa únicamente IDs existentes;
- incluye solo segmentos que respalden directamente el item.

description:
- describe únicamente lo expresado;
- no inventes motivos, impactos, responsables ni fechas.

Devuelve únicamente JSON.

SEGMENTOS:
{serialized_segments}
""".strip()


def build_classification_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "items",
        ],
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "kind",
                        "description",
                        "segment_ids",
                    ],
                    "properties": {
                        "kind": {
                            "type": "string",
                            "enum": [
                                "topic",
                                "decision",
                                "action",
                                "risk",
                                "pending",
                            ],
                        },
                        "description": {
                            "type": "string",
                        },
                        "segment_ids": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "integer",
                                "minimum": 0,
                            },
                        },
                    },
                },
            },
        },
    }


def build_action_prompt(
    action_item: dict,
    chunk: TranscriptChunk,
) -> str:
    source_segments = []

    for segment_id in action_item[
        "segment_ids"
    ]:
        segment = chunk.segments[
            segment_id
        ]
        source_segments.append(
            {
                "segment_id": segment_id,
                "speaker": segment.speaker,
                "text": segment.text,
            }
        )

    serialized_segments = json.dumps(
        source_segments,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return f"""
Extrae metadatos SOLO para esta acción de reunión.

ACCIÓN:
{action_item["description"]}

REGLAS:

owner:
- devuelve el nombre de la persona o entidad a quien se asigna la tarea;
- usa solo un responsable explícitamente nombrado en el texto;
- NUNCA uses etiquetas de canal o speaker como LOCAL, REMOTE, USER o SYSTEM
  como owner, salvo que sean literalmente el nombre de una persona o entidad;
- ejemplo: "María debe preparar el plan" -> owner="María";
- si no existe responsable explícito -> null.

due_date:
- usa YYYY-MM-DD solo si la fecha completa puede obtenerse sin asumir datos;
- ejemplo: "30 de agosto de 2026" -> "2026-08-30";
- si es ambigua o falta información -> null.

status:
- pending: tarea que debe ejecutarse;
- completed: el texto afirma que ya fue completada;
- cancelled: el texto afirma que fue cancelada;
- unknown: no puede determinarse.

No inventes información.
Devuelve únicamente JSON.

SEGMENTOS DE EVIDENCIA:
{serialized_segments}
""".strip()


def build_action_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "owner",
            "due_date",
            "status",
        ],
        "properties": {
            "owner": {
                "anyOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "null",
                    },
                ],
            },
            "due_date": {
                "anyOf": [
                    {
                        "type": "string",
                    },
                    {
                        "type": "null",
                    },
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
        },
    }


def validate_classification(
    data: dict,
    chunk: TranscriptChunk,
) -> list[str]:
    errors: list[str] = []

    if set(data.keys()) != {"items"}:
        errors.append(
            "La raíz debe contener únicamente items."
        )
        return errors

    items = data["items"]

    if not isinstance(items, list):
        errors.append("items debe ser una lista.")
        return errors

    maximum_id = len(chunk.segments) - 1

    for index, item in enumerate(
        items,
        start=1,
    ):
        if not isinstance(item, dict):
            errors.append(
                f"item #{index} no es objeto."
            )
            continue

        if set(item.keys()) != {
            "kind",
            "description",
            "segment_ids",
        }:
            errors.append(
                f"item #{index} contiene campos "
                "inesperados o faltantes."
            )
            continue

        segment_ids = item[
            "segment_ids"
        ]

        if not isinstance(
            segment_ids,
            list,
        ):
            errors.append(
                f"item #{index} segment_ids no es lista."
            )
            continue

        for segment_id in segment_ids:
            if (
                not isinstance(segment_id, int)
                or isinstance(segment_id, bool)
                or segment_id < 0
                or segment_id > maximum_id
            ):
                errors.append(
                    f"item #{index} usa segment_id "
                    f"inválido: {segment_id}."
                )

    return errors


def evaluate_classification(
    data: dict,
) -> list[str]:
    errors: list[str] = []

    by_segment: dict[int, list[dict]] = {
        segment_id: []
        for segment_id in EXPECTED_KIND_BY_SEGMENT
    }

    for item in data[
        "items"
    ]:
        for segment_id in item[
            "segment_ids"
        ]:
            if segment_id in by_segment:
                by_segment[
                    segment_id
                ].append(item)

    for (
        segment_id,
        expected_kind,
    ) in EXPECTED_KIND_BY_SEGMENT.items():
        matches = by_segment[
            segment_id
        ]

        if len(matches) != 1:
            errors.append(
                f"segment_id {segment_id}: se esperaba "
                "exactamente 1 item, se obtuvieron "
                f"{len(matches)}."
            )
            continue

        actual_kind = matches[0][
            "kind"
        ]

        if actual_kind != expected_kind:
            errors.append(
                f"segment_id {segment_id}: se esperaba "
                f"kind={expected_kind}, se obtuvo "
                f"kind={actual_kind}."
            )

    return errors


def evaluate_action_metadata(
    metadata: dict,
) -> list[str]:
    errors: list[str] = []

    owner = metadata[
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
            "owner debe ser María."
        )

    if (
        metadata["due_date"]
        != "2026-08-30"
    ):
        errors.append(
            "due_date debe ser 2026-08-30."
        )

    if (
        metadata["status"]
        != "pending"
    ):
        errors.append(
            "status debe ser pending."
        )

    return errors


def print_classification(
    data: dict,
    chunk: TranscriptChunk,
) -> None:
    print(
        "\n=== ETAPA 1: CLASIFICACIÓN ==="
    )

    for index, item in enumerate(
        data["items"],
        start=1,
    ):
        print(
            f"\n#{index} "
            f"kind={item['kind']} "
            f"description={item['description']}"
        )

        for segment_id in item[
            "segment_ids"
        ]:
            segment = chunk.segments[
                segment_id
            ]
            print(
                "  "
                f"segment_id={segment_id} "
                f"[{segment.start:.1f}-{segment.end:.1f}] "
                f"{segment.speaker}: "
                f"{segment.text}"
            )


def main() -> int:
    args = parse_args()
    chunk = build_chunk()
    provider = OllamaProvider(
        model=args.model
    )

    print(
        "=== CONTRATO DIAGNÓSTICO V3 STAGED ==="
    )
    print(
        f"Modelo: {args.model}"
    )
    print(
        f"Segmentos: {len(chunk.segments)}"
    )
    print(
        f"Palabras: {chunk.word_count}"
    )

    stage1_started = time.perf_counter()

    classification_response = (
        provider.generate(
            build_classification_prompt(
                chunk
            ),
            build_classification_schema(),
        )
    )

    stage1_elapsed = (
        time.perf_counter()
        - stage1_started
    )

    print(
        f"\nTiempo etapa 1: "
        f"{stage1_elapsed:.2f} s"
    )
    print(
        "\n=== RESPUESTA CRUDA ETAPA 1 ==="
    )
    print(
        classification_response
    )

    try:
        classification = json.loads(
            classification_response
        )
    except json.JSONDecodeError as ex:
        print(
            "\nDIAGNÓSTICO: JSON INVÁLIDO "
            "EN ETAPA 1."
        )
        print(ex)
        return 2

    structural_errors = (
        validate_classification(
            data=classification,
            chunk=chunk,
        )
    )

    if structural_errors:
        print(
            "\n=== ERRORES ESTRUCTURALES "
            "ETAPA 1 ==="
        )

        for error in structural_errors:
            print(
                f"- {error}"
            )

        return 3

    print_classification(
        data=classification,
        chunk=chunk,
    )

    classification_errors = (
        evaluate_classification(
            classification
        )
    )

    if classification_errors:
        print(
            "\nDIAGNÓSTICO: ETAPA 1 "
            "NO CUMPLE."
        )

        for error in classification_errors:
            print(
                f"- {error}"
            )

        return 4

    action_items = [
        item
        for item in classification[
            "items"
        ]
        if item[
            "kind"
        ] == "action"
    ]

    if len(action_items) != 1:
        print(
            "\nDIAGNÓSTICO: se esperaba "
            "exactamente una acción para "
            "la etapa 2."
        )
        return 5

    action_item = action_items[
        0
    ]

    stage2_started = time.perf_counter()

    metadata_response = (
        provider.generate(
            build_action_prompt(
                action_item=action_item,
                chunk=chunk,
            ),
            build_action_schema(),
        )
    )

    stage2_elapsed = (
        time.perf_counter()
        - stage2_started
    )

    print(
        "\n=== ETAPA 2: "
        "METADATOS DE ACCIÓN ==="
    )
    print(
        f"Tiempo etapa 2: "
        f"{stage2_elapsed:.2f} s"
    )
    print(
        "\n=== RESPUESTA CRUDA ETAPA 2 ==="
    )
    print(
        metadata_response
    )

    try:
        metadata = json.loads(
            metadata_response
        )
    except json.JSONDecodeError as ex:
        print(
            "\nDIAGNÓSTICO: JSON INVÁLIDO "
            "EN ETAPA 2."
        )
        print(ex)
        return 6

    metadata_errors = (
        evaluate_action_metadata(
            metadata
        )
    )

    total_elapsed = (
        stage1_elapsed
        + stage2_elapsed
    )

    print(
        "\n=== RESULTADO FINAL ==="
    )
    print(
        f"owner: {metadata['owner']}"
    )
    print(
        f"due_date: {metadata['due_date']}"
    )
    print(
        f"status: {metadata['status']}"
    )
    print(
        f"Tiempo total IA: "
        f"{total_elapsed:.2f} s"
    )

    if metadata_errors:
        print(
            "\nDIAGNÓSTICO: ETAPA 2 "
            "NO CUMPLE."
        )

        for error in metadata_errors:
            print(
                f"- {error}"
            )

        return 7

    print(
        "\nPRUEBA COMPLETADA: 3B resolvió "
        "clasificación y metadatos de acción "
        "en etapas separadas."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
