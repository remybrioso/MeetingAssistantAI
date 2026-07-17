"""
setup_wizard_service.py

Orquesta el diagnóstico funcional de todas las
capacidades registradas en Meeting Assistant AI.
"""

from datetime import datetime

from services.setup.capabilities.capability_result import (
    CapabilityResult,
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)
from services.setup.wizard.setup_wizard_policy import (
    SetupWizardPolicy,
)
from services.setup.wizard.setup_wizard_result import (
    SetupWizardResult,
    SetupWizardStatus,
)


class SetupWizardService:

    def __init__(
        self,
        capability_registry,
        capability_runner=None,
        policy=None,
        event_bus=None,
    ):

        self.capability_registry = (
            capability_registry
        )

        self.event_bus = event_bus

        self.capability_runner = (
            capability_runner
            or CapabilityRunner(
                event_bus=event_bus
            )
        )

        self.policy = (
            policy
            or SetupWizardPolicy()
        )

        self._last_result = None

    @property
    def last_result(
        self
    ) -> SetupWizardResult | None:

        return self._last_result

    def run(self) -> SetupWizardResult:

        started_at = datetime.now()

        capabilities = list(
            self.capability_registry.get_all()
        )

        self._emit(
            "setup_wizard_started",
            len(capabilities),
        )

        results = []

        for index, capability in enumerate(
            capabilities,
            start=1,
        ):

            self._emit(
                "setup_wizard_capability_started",
                capability.capability_id,
                capability.name,
                index,
                len(capabilities),
            )

            result = self.capability_runner.run(
                capability
            )

            results.append(result)

            self._emit(
                "setup_wizard_capability_completed",
                result,
                index,
                len(capabilities),
            )

        wizard_result = self._evaluate(
            started_at=started_at,
            completed_at=datetime.now(),
            capability_results=results,
        )

        self._last_result = wizard_result

        self._emit(
            "setup_wizard_completed",
            wizard_result,
        )

        return wizard_result

    def rerun_capability(
        self,
        capability_id: str,
    ) -> CapabilityResult:

        capability = (
            self.capability_registry.get(
                capability_id
            )
        )

        if capability is None:

            raise KeyError(
                "No existe una capacidad "
                f"registrada con el ID "
                f"'{capability_id}'."
            )

        self._emit(
            "setup_wizard_capability_retry_started",
            capability_id,
        )

        result = self.capability_runner.run(
            capability
        )

        self._emit(
            "setup_wizard_capability_retry_completed",
            result,
        )

        return result

    def refresh(
        self
    ) -> SetupWizardResult:

        return self.run()

    def _evaluate(
        self,
        started_at,
        completed_at,
        capability_results,
    ) -> SetupWizardResult:

        unavailable_required = [
            result
            for result in capability_results
            if (
                result.status
                == CapabilityStatus.UNAVAILABLE
                and self.policy.is_required(
                    result.capability_id
                )
            )
        ]

        degraded = [
            result
            for result in capability_results
            if (
                result.status
                == CapabilityStatus.DEGRADED
            )
        ]

        unavailable_optional = [
            result
            for result in capability_results
            if (
                result.status
                == CapabilityStatus.UNAVAILABLE
                and not self.policy.is_required(
                    result.capability_id
                )
            )
        ]

        if unavailable_required:

            status = SetupWizardStatus.BLOCKED

            message = (
                "MAI necesita completar algunas "
                "configuraciones antes de continuar."
            )

        elif (
            degraded
            or unavailable_optional
        ):

            if (
                degraded
                and not self.policy.allow_degraded
            ):

                status = SetupWizardStatus.BLOCKED

                message = (
                    "MAI detectó capacidades degradadas "
                    "que deben corregirse antes de "
                    "continuar."
                )

            else:

                status = SetupWizardStatus.ATTENTION

                message = (
                    "MAI puede continuar, pero algunas "
                    "funciones requieren atención."
                )

        else:

            status = SetupWizardStatus.READY

            message = (
                "MAI está configurado y listo "
                "para trabajar."
            )

        available_count = sum(
            1
            for result in capability_results
            if (
                result.status
                == CapabilityStatus.AVAILABLE
            )
        )

        degraded_count = len(degraded)

        unavailable_count = sum(
            1
            for result in capability_results
            if (
                result.status
                == CapabilityStatus.UNAVAILABLE
            )
        )

        repairable_count = sum(
            1
            for result in capability_results
            if result.repairable
        )

        return SetupWizardResult(
            status=status,
            message=message,
            started_at=started_at,
            completed_at=completed_at,
            capability_results=(
                capability_results
            ),
            details={
                "total_capabilities": len(
                    capability_results
                ),
                "available_count": (
                    available_count
                ),
                "degraded_count": (
                    degraded_count
                ),
                "unavailable_count": (
                    unavailable_count
                ),
                "repairable_count": (
                    repairable_count
                ),
                "required_capability_ids": sorted(
                    self.policy
                    .required_capability_ids
                ),
            },
        )

    def _emit(
        self,
        event_name,
        *args,
    ) -> None:

        if self.event_bus:

            self.event_bus.emit(
                event_name,
                *args,
            )