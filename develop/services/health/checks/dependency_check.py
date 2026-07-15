"""
dependency_check.py

Comprueba las dependencias críticas de MAI.
"""

import importlib

from services.health.health_check import HealthCheck
from services.health.health_result import (
    HealthResult,
    HealthStatus,
)


class DependencyCheck(HealthCheck):

    REQUIRED_MODULES = [
        "customtkinter",
        "soundcard",
        "soundfile",
        "faster_whisper",
        "requests",
        "numpy",
    ]

    def run(self) -> HealthResult:

        missing = []

        for module in self.REQUIRED_MODULES:

            try:
                importlib.import_module(module)

            except Exception:
                missing.append(module)

        if missing:

            return HealthResult(
                name="Dependencies",
                status=HealthStatus.FAILED,
                message=(
                    "Faltan dependencias críticas."
                ),
                details={
                    "missing": missing
                },
            )

        return HealthResult(
            name="Dependencies",
            status=HealthStatus.OK,
            message="Todas las dependencias están instaladas.",
            details={
                "count": len(self.REQUIRED_MODULES)
            },
        )