"""
python_check.py

Comprueba la instalación y versión de Python.
"""

import platform
import struct
import sys

from services.health.health_check import HealthCheck
from services.health.health_result import (
    HealthResult,
    HealthStatus,
)


class PythonCheck(HealthCheck):

    MIN_VERSION = (3, 12)

    def run(self) -> HealthResult:

        version = sys.version_info
        version_text = (
            f"{version.major}."
            f"{version.minor}."
            f"{version.micro}"
        )

        architecture = (
            f"{struct.calcsize('P') * 8}-bit"
        )

        if (
            version.major,
            version.minor,
        ) < self.MIN_VERSION:

            return HealthResult(
                name="Python",
                status=HealthStatus.FAILED,
                message=(
                    "Versión de Python no soportada."
                ),
                details={
                    "version": version_text,
                    "architecture": architecture,
                    "platform": platform.platform(),
                },
            )

        return HealthResult(
            name="Python",
            status=HealthStatus.OK,
            message="Python compatible.",
            details={
                "version": version_text,
                "architecture": architecture,
                "platform": platform.platform(),
            },
        )