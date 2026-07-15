"""
health_service.py

Ejecuta todas las comprobaciones registradas
y genera un informe completo.
"""

from services.health.health_result import (
    HealthResult,
    HealthStatus,
)


class HealthService:

    def __init__(self, checks=None):

        self.checks = list(checks or [])

    def add_check(self, check) -> None:

        self.checks.append(check)

    def run_all(self) -> list[HealthResult]:

        results = []

        for check in self.checks:

            try:
                result = check.run()

                if not isinstance(result, HealthResult):
                    raise TypeError(
                        "El HealthCheck no devolvió HealthResult."
                    )

                results.append(result)

            except Exception as ex:

                results.append(
                    HealthResult(
                        name=check.__class__.__name__,
                        status=HealthStatus.FAILED,
                        message=(
                            "La comprobación no pudo ejecutarse."
                        ),
                        details=str(ex),
                    )
                )

        return results

    @staticmethod
    def is_ready(
        results: list[HealthResult]
    ) -> bool:

        return all(
            result.status != HealthStatus.FAILED
            for result in results
        )
