"""
action_status.py

Estados válidos para una acción identificada
durante una reunión.
"""

from enum import StrEnum


class ActionStatus(StrEnum):
    """
    Representa el estado conocido de un ActionItem.

    UNKNOWN:
        La acción fue identificada, pero su estado
        no fue expresado claramente.

    PENDING:
        La acción está pendiente de ejecución.

    COMPLETED:
        La acción fue indicada como completada.

    CANCELLED:
        La acción fue cancelada.
    """

    UNKNOWN = "unknown"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def from_value(
        cls,
        value: str | "ActionStatus",
    ) -> "ActionStatus":
        """
        Convierte una cadena o ActionStatus en un estado válido.

        La comparación no distingue entre mayúsculas y
        minúsculas y elimina espacios externos.

        Raises:
            TypeError:
                Si value no es str ni ActionStatus.

            ValueError:
                Si la cadena no representa un estado válido.
        """

        if isinstance(
            value,
            cls,
        ):
            return value

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "ActionStatus requiere una cadena "
                "o una instancia de ActionStatus."
            )

        normalized_value = value.strip().lower()

        try:
            return cls(
                normalized_value
            )

        except ValueError as ex:
            valid_values = ", ".join(
                status.value
                for status in cls
            )

            raise ValueError(
                "Estado de acción no válido: "
                f"{value!r}. Valores permitidos: "
                f"{valid_values}."
            ) from ex