"""
capability_registry.py

Registro central de capacidades de MAI.
"""


class CapabilityRegistry:

    def __init__(self):

        self._capabilities = {}

    def register(self, capability) -> None:

        capability_id = capability.capability_id

        if not capability_id:
            raise ValueError(
                "La capacidad necesita un identificador."
            )

        if capability_id in self._capabilities:
            raise ValueError(
                "Ya existe una capacidad registrada "
                f"con el ID '{capability_id}'."
            )

        self._capabilities[
            capability_id
        ] = capability

    def get(self, capability_id):

        return self._capabilities.get(
            capability_id
        )

    def get_all(self) -> list:

        return list(
            self._capabilities.values()
        )

    def __len__(self) -> int:

        return len(self._capabilities)

    def __iter__(self):

        return iter(
            self._capabilities.values()
        )
