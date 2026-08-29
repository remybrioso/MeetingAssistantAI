"""
runtime_resources_task.py

Comprueba que los recursos internos indispensables para el
pipeline productivo de MAI estén disponibles y sean válidos.
"""

from application.runtime_paths import RuntimePaths
from services.json_schema_loader import JsonSchemaLoader
from services.setup.setup_task import SetupTask
from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)


class RuntimeResourcesTask(SetupTask):

    task_id = "verify-runtime-resources"
    name = "Verificar recursos internos"
    critical = True

    REQUIRED_SCHEMA_CONTRACTS = (
        "chunk_classification_v1",
        "chunk_action_metadata_v1",
        "meeting_semantic_consolidation_v1",
        "meeting_report_narrative_v1",
    )

    def __init__(
        self,
        runtime_paths: RuntimePaths,
        schema_loader=None,
    ) -> None:
        if not isinstance(
            runtime_paths,
            RuntimePaths,
        ):
            raise TypeError(
                "runtime_paths debe ser una "
                "instancia de RuntimePaths."
            )

        self.runtime_paths = runtime_paths

        self.schema_loader = (
            schema_loader
            if schema_loader is not None
            else JsonSchemaLoader(
                schemas_directory=(
                    runtime_paths.schemas_directory
                )
            )
        )

    def should_run(self) -> bool:
        return True

    def run(self) -> TaskResult:
        validated_contracts = []

        try:
            for contract in (
                self.REQUIRED_SCHEMA_CONTRACTS
            ):
                self.schema_loader.load(
                    contract
                )

                validated_contracts.append(
                    contract
                )

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.SUCCESS,
                message=(
                    "Los recursos internos de MAI "
                    "están disponibles."
                ),
                details={
                    "resource_root": str(
                        self.runtime_paths.resource_root
                    ),
                    "schemas_directory": str(
                        self.runtime_paths
                        .schemas_directory
                    ),
                    "validated_contracts": (
                        validated_contracts
                    ),
                    "required_contract_count": len(
                        self.REQUIRED_SCHEMA_CONTRACTS
                    ),
                },
            )

        except Exception as ex:
            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.FAILED,
                message=(
                    "Faltan recursos internos o "
                    "algún recurso no es válido."
                ),
                details={
                    "resource_root": str(
                        self.runtime_paths.resource_root
                    ),
                    "schemas_directory": str(
                        self.runtime_paths
                        .schemas_directory
                    ),
                    "validated_contracts": (
                        validated_contracts
                    ),
                    "required_contracts": list(
                        self.REQUIRED_SCHEMA_CONTRACTS
                    ),
                },
                error=str(ex),
            )

    def verify(self) -> bool:
        return (
            self.run().status
            == TaskStatus.SUCCESS
        )
