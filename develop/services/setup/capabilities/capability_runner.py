"""
capability_runner.py

Ejecuta las tareas de una capacidad y genera
su resultado funcional.
"""

from services.setup.capabilities.capability_result import (
    CapabilityResult,
    CapabilityStatus,
)
from services.setup.setup_engine import SetupEngine


class CapabilityRunner:

    def __init__(self, event_bus=None):

        self.event_bus = event_bus

    def run(self, capability) -> CapabilityResult:

        self._emit(
            "capability_started",
            capability.capability_id,
            capability.name
        )

        try:
            engine = SetupEngine(
                tasks=capability.get_tasks(),
                event_bus=self.event_bus
            )

            setup_result = engine.run()

            capability_result = capability.evaluate(
                setup_result.task_results
            )

            if not isinstance(
                capability_result,
                CapabilityResult
            ):

                raise TypeError(
                    "La capacidad no devolvió "
                    "CapabilityResult."
                )

        except Exception as ex:

            capability_result = CapabilityResult(
                capability_id=getattr(
                    capability,
                    "capability_id",
                    capability.__class__.__name__
                ),
                name=getattr(
                    capability,
                    "name",
                    capability.__class__.__name__
                ),
                status=(
                    CapabilityStatus.UNAVAILABLE
                ),
                message=(
                    "La capacidad no pudo evaluarse."
                ),
                details={
                    "error": str(ex),
                },
            )

        self._emit(
            "capability_completed",
            capability_result
        )

        return capability_result

    def _emit(self, event_name, *args) -> None:

        if self.event_bus:

            self.event_bus.emit(
                event_name,
                *args
            )
