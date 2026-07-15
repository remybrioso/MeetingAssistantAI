"""
ai_provider_check.py

Convierte el diagnóstico técnico de un proveedor
de IA en un resultado del Health Check de MAI.
"""

from services.health.health_check import HealthCheck
from services.health.health_result import (
    HealthResult,
    HealthStatus,
)


class AIProviderCheck(HealthCheck):

    def __init__(self, provider):

        self.provider = provider

    def run(self) -> HealthResult:

        provider_health = (
            self.provider.health()
        )

        details = {
            "provider": provider_health.provider,
            "model": provider_health.model,
            "connected": provider_health.connected,
            "model_found": provider_health.model_found,
            "response_time_ms": (
                provider_health.response_time_ms
            ),
            "available_models": (
                provider_health.available_models
            ),
        }

        if provider_health.error:

            details["error"] = (
                provider_health.error
            )

        if not provider_health.connected:

            return HealthResult(
                name="AI Provider",
                status=HealthStatus.FAILED,
                message=provider_health.message,
                details=details,
            )

        if not provider_health.model_found:

            return HealthResult(
                name="AI Provider",
                status=HealthStatus.FAILED,
                message=provider_health.message,
                details=details,
            )

        return HealthResult(
            name="AI Provider",
            status=HealthStatus.OK,
            message=provider_health.message,
            details=details,
        )