"""
prompt.py

Representa un prompt listo para ser enviado
a un proveedor de IA.
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class Prompt:
    """
    Prompt inmutable.

    Attributes:
        content:
            Prompt completo.

        version:
            Identificador de la plantilla utilizada.
    """

    content: str
    version: str