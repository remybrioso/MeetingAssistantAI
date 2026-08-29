"""
setup_wizard_policy.py

Define las reglas utilizadas para decidir
si MAI puede continuar después del diagnóstico.
"""

from dataclasses import dataclass, field


@dataclass
class SetupWizardPolicy:

    required_capability_ids: set[str] = field(
        default_factory=lambda: {
            "runtime-resources",
            "workspace",
            "transcription",
            "artificial-intelligence",
            "audio",
        }
    )

    allow_degraded: bool = True

    def is_required(
        self,
        capability_id: str,
    ) -> bool:

        return (
            capability_id
            in self.required_capability_ids
        )
