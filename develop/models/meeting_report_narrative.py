"""
meeting_report_narrative.py

Representación intermedia y grounded de la narrativa global de una
reunión antes de construir el MeetingReport final.
"""

from dataclasses import dataclass, field


@dataclass(
    frozen=True,
    slots=True,
)
class GroundedNarrativeText:
    """
    Texto narrativo respaldado por uno o más items semánticos de G1.
    """

    text: str
    source_item_ids: list[int] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.text,
            str,
        ):
            raise TypeError(
                "GroundedNarrativeText text debe ser una cadena."
            )

        normalized_text = self.text.strip()

        if not normalized_text:
            raise ValueError(
                "GroundedNarrativeText text no puede estar vacío."
            )

        object.__setattr__(
            self,
            "text",
            normalized_text,
        )

        if not isinstance(
            self.source_item_ids,
            list,
        ):
            raise TypeError(
                "GroundedNarrativeText source_item_ids debe ser "
                "una lista."
            )

        if not self.source_item_ids:
            raise ValueError(
                "GroundedNarrativeText requiere al menos un "
                "source_item_id."
            )

        normalized_ids: list[int] = []
        seen_ids: set[int] = set()

        for index, source_item_id in enumerate(
            self.source_item_ids,
            start=1,
        ):
            if (
                not isinstance(
                    source_item_id,
                    int,
                )
                or isinstance(
                    source_item_id,
                    bool,
                )
            ):
                raise TypeError(
                    "GroundedNarrativeText source_item_ids "
                    f"elemento #{index} debe ser entero."
                )

            if source_item_id < 0:
                raise ValueError(
                    "GroundedNarrativeText source_item_ids "
                    f"elemento #{index} no puede ser negativo."
                )

            if source_item_id in seen_ids:
                raise ValueError(
                    "GroundedNarrativeText source_item_ids no puede "
                    "contener valores duplicados."
                )

            seen_ids.add(
                source_item_id
            )
            normalized_ids.append(
                source_item_id
            )

        object.__setattr__(
            self,
            "source_item_ids",
            normalized_ids,
        )

    def as_dict(self) -> dict:
        return {
            "text": self.text,
            "source_item_ids": list(
                self.source_item_ids
            ),
        }


@dataclass
class MeetingReportNarrative:
    """
    Resultado estructurado de la etapa global G2.

    Las referencias se conservan hasta K2C para que el sistema pueda
    validar y ensamblar el MeetingReport de forma determinista.
    """

    title: GroundedNarrativeText
    objective: GroundedNarrativeText | None
    executive_summary: GroundedNarrativeText
    key_points: list[
        GroundedNarrativeText
    ] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.title,
            GroundedNarrativeText,
        ):
            raise TypeError(
                "MeetingReportNarrative title debe ser una instancia "
                "de GroundedNarrativeText."
            )

        if (
            self.objective is not None
            and not isinstance(
                self.objective,
                GroundedNarrativeText,
            )
        ):
            raise TypeError(
                "MeetingReportNarrative objective debe ser una "
                "instancia de GroundedNarrativeText o None."
            )

        if not isinstance(
            self.executive_summary,
            GroundedNarrativeText,
        ):
            raise TypeError(
                "MeetingReportNarrative executive_summary debe ser "
                "una instancia de GroundedNarrativeText."
            )

        if not isinstance(
            self.key_points,
            list,
        ):
            raise TypeError(
                "MeetingReportNarrative key_points debe ser una lista."
            )

        if not self.key_points:
            raise ValueError(
                "MeetingReportNarrative key_points debe contener "
                "al menos un elemento."
            )

        normalized_key_points = list(
            self.key_points
        )
        seen_texts: set[str] = set()

        for index, key_point in enumerate(
            normalized_key_points,
            start=1,
        ):
            if not isinstance(
                key_point,
                GroundedNarrativeText,
            ):
                raise TypeError(
                    "MeetingReportNarrative key_points elemento "
                    f"#{index} debe ser una instancia de "
                    "GroundedNarrativeText."
                )

            normalized_key = " ".join(
                key_point.text.casefold().split()
            )

            if normalized_key in seen_texts:
                raise ValueError(
                    "MeetingReportNarrative key_points no puede "
                    "contener textos duplicados."
                )

            seen_texts.add(
                normalized_key
            )

        self.key_points = (
            normalized_key_points
        )

    def as_dict(self) -> dict:
        return {
            "title": self.title.as_dict(),
            "objective": (
                self.objective.as_dict()
                if self.objective is not None
                else None
            ),
            "executive_summary": (
                self.executive_summary.as_dict()
            ),
            "key_points": [
                item.as_dict()
                for item in self.key_points
            ],
        }
