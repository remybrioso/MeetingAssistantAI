"""
chunk_action_metadata.py

Metadatos enriquecidos para acciones previamente clasificadas
dentro de un TranscriptChunk.
"""

from dataclasses import dataclass, field
from datetime import date

from models.meeting_report import (
    ActionOwner,
    ActionStatus,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ActionMetadataEntry:
    """
    Metadatos de una acción vinculados por índice al resultado
    de ChunkClassification.

    classification_item_index es propiedad del sistema y apunta
    al índice exacto dentro de ChunkClassification.items.
    """

    classification_item_index: int
    owner: ActionOwner | str | None = None
    due_date: date | None = None
    status: ActionStatus | str = ActionStatus.UNKNOWN

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.classification_item_index,
                int,
            )
            or isinstance(
                self.classification_item_index,
                bool,
            )
        ):
            raise TypeError(
                "ActionMetadataEntry classification_item_index "
                "debe ser entero."
            )

        if self.classification_item_index < 0:
            raise ValueError(
                "ActionMetadataEntry classification_item_index "
                "no puede ser negativo."
            )

        normalized_owner = self._normalize_owner(
            self.owner
        )
        normalized_due_date = self._normalize_due_date(
            self.due_date
        )
        normalized_status = ActionStatus.from_value(
            self.status
        )

        object.__setattr__(
            self,
            "owner",
            normalized_owner,
        )
        object.__setattr__(
            self,
            "due_date",
            normalized_due_date,
        )
        object.__setattr__(
            self,
            "status",
            normalized_status,
        )

    @staticmethod
    def _normalize_owner(
        owner: ActionOwner | str | None,
    ) -> ActionOwner | None:
        if owner is None:
            return None

        return ActionOwner.from_value(
            owner
        )

    @staticmethod
    def _normalize_due_date(
        due_date: date | None,
    ) -> date | None:
        if due_date is None:
            return None

        if not isinstance(
            due_date,
            date,
        ):
            raise TypeError(
                "ActionMetadataEntry due_date debe ser una "
                "fecha o None."
            )

        return due_date

    def as_dict(self) -> dict:
        return {
            "classification_item_index": (
                self.classification_item_index
            ),
            "owner": (
                self.owner.as_dict()
                if self.owner is not None
                else None
            ),
            "due_date": (
                self.due_date.isoformat()
                if self.due_date is not None
                else None
            ),
            "status": self.status.value,
        }


@dataclass
class ChunkActionMetadata:
    """
    Colección de metadatos de acciones para un único chunk.

    Puede estar vacía cuando el chunk no contiene acciones.
    """

    chunk_index: int
    entries: list[ActionMetadataEntry] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.chunk_index,
                int,
            )
            or isinstance(
                self.chunk_index,
                bool,
            )
        ):
            raise TypeError(
                "ChunkActionMetadata chunk_index debe ser entero."
            )

        if self.chunk_index < 0:
            raise ValueError(
                "ChunkActionMetadata chunk_index no puede ser "
                "negativo."
            )

        if not isinstance(
            self.entries,
            list,
        ):
            raise TypeError(
                "ChunkActionMetadata entries debe ser una lista."
            )

        normalized_entries = list(
            self.entries
        )
        seen_indices: set[int] = set()

        for index, entry in enumerate(
            normalized_entries,
            start=1,
        ):
            if not isinstance(
                entry,
                ActionMetadataEntry,
            ):
                raise TypeError(
                    "ChunkActionMetadata entries elemento "
                    f"#{index} debe ser una instancia de "
                    "ActionMetadataEntry."
                )

            item_index = (
                entry.classification_item_index
            )

            if item_index in seen_indices:
                raise ValueError(
                    "ChunkActionMetadata no puede contener "
                    "classification_item_index duplicados."
                )

            seen_indices.add(
                item_index
            )

        self.entries = normalized_entries

    @property
    def has_actions(self) -> bool:
        return bool(
            self.entries
        )

    def for_classification_item(
        self,
        item_index: int,
    ) -> ActionMetadataEntry | None:
        if (
            not isinstance(
                item_index,
                int,
            )
            or isinstance(
                item_index,
                bool,
            )
        ):
            raise TypeError(
                "item_index debe ser entero."
            )

        if item_index < 0:
            raise ValueError(
                "item_index no puede ser negativo."
            )

        for entry in self.entries:
            if (
                entry.classification_item_index
                == item_index
            ):
                return entry

        return None

    def as_dict(self) -> dict:
        return {
            "chunk_index": self.chunk_index,
            "entries": [
                entry.as_dict()
                for entry in self.entries
            ],
        }
