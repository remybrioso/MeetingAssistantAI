"""
action_owner.py

Responsable textual de una acción identificada
durante una reunión.
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class ActionOwner:
    """
    Representa la persona, equipo, área o grupo responsable
    de una acción.

    Examples:
        Remy
        Equipo Oracle
        Infraestructura
        DBA
        Todos
    """

    display_name: str

    def __post_init__(self) -> None:
        normalized_display_name = (
            self.display_name.strip()
        )

        if not normalized_display_name:
            raise ValueError(
                "ActionOwner display_name no puede "
                "estar vacío."
            )

        object.__setattr__(
            self,
            "display_name",
            normalized_display_name,
        )

    @classmethod
    def from_value(
        cls,
        value: str | "ActionOwner",
    ) -> "ActionOwner":
        """
        Convierte una cadena o ActionOwner en una instancia
        válida.

        Raises:
            TypeError:
                Si value no es str ni ActionOwner.

            ValueError:
                Si la cadena está vacía.
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
                "ActionOwner requiere una cadena "
                "o una instancia de ActionOwner."
            )

        return cls(
            display_name=value,
        )

    def as_dict(self) -> dict:
        """
        Devuelve una representación serializable.
        """

        return {
            "display_name": self.display_name,
        }

    def __str__(self) -> str:
        return self.display_name