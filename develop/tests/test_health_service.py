from services.health.health_check import HealthCheck
from services.health.health_result import (
    HealthResult,
    HealthStatus,
)
from services.health.health_service import HealthService


class SuccessfulCheck(HealthCheck):

    def run(self) -> HealthResult:

        return HealthResult(
            name="Prueba correcta",
            status=HealthStatus.OK,
            message="El componente funciona correctamente.",
        )


class FailedCheck(HealthCheck):

    def run(self) -> HealthResult:

        return HealthResult(
            name="Prueba fallida",
            status=HealthStatus.FAILED,
            message="El componente no está disponible.",
            details="Fallo simulado.",
        )


class BrokenCheck(HealthCheck):

    def run(self) -> HealthResult:

        raise RuntimeError(
            "Excepción simulada durante el diagnóstico."
        )


service = HealthService(
    checks=[
        SuccessfulCheck(),
        FailedCheck(),
        BrokenCheck(),
    ]
)

results = service.run_all()

for result in results:

    print(
        f"[{result.status.value}] "
        f"{result.name}: {result.message}"
    )

    if result.details:
        print(f"  Detalle: {result.details}")


assert len(results) == 3

assert results[0].status == HealthStatus.OK
assert results[1].status == HealthStatus.FAILED

# BrokenCheck no debe detener el diagnóstico.
assert results[2].status == HealthStatus.FAILED

assert not service.is_ready(results)

print()
print("Health Check Framework validado correctamente.")