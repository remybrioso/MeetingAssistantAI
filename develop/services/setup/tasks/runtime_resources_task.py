"""
runtime_resources_task.py

Comprueba los recursos internos indispensables para el pipeline
productivo de Meeting Assistant AI.
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
        "chunk_classification_v2",
        "chunk_ignored_segment_audit_v1",
        "chunk_action_metadata_v1",
        "meeting_semantic_consolidation_v1",
        "meeting_report_narrative_v1",
    )

    REQUIRED_PROMPT_CONTRACTS = (
        (
            "chunk_classification_v2",
            "{{SEGMENTS}}",
        ),
        (
            "chunk_classification_repair_v1",
            "{{REPAIR_CONTEXT}}",
        ),
        (
            "chunk_ignored_segment_audit_v1",
            "{{CANDIDATE_SEGMENTS}}",
        ),
        (
            "chunk_action_metadata_v1",
            "{{ACTIONS}}",
        ),
        (
            "meeting_semantic_consolidation_v1",
            "{{SOURCE_CATALOG}}",
        ),
        (
            "meeting_report_narrative_v1",
            "{{CONSOLIDATED_ITEMS}}",
        ),
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
                "runtime_paths debe ser una instancia "
                "de RuntimePaths."
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
        validated_schema_contracts = []
        validated_prompt_contracts = []

        try:
            for contract in (
                self.REQUIRED_SCHEMA_CONTRACTS
            ):
                self.schema_loader.load(
                    contract
                )
                validated_schema_contracts.append(
                    contract
                )

            for contract, placeholder in (
                self.REQUIRED_PROMPT_CONTRACTS
            ):
                template_file = (
                    self.runtime_paths
                    .prompts_directory
                    / f"{contract}.md"
                )

                template = template_file.read_text(
                    encoding="utf-8"
                )

                if template.count(
                    placeholder
                ) != 1:
                    raise ValueError(
                        "La plantilla productiva "
                        f"{template_file.name} debe contener "
                        f"exactamente una vez {placeholder}."
                    )

                validated_prompt_contracts.append(
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
                    "prompts_directory": str(
                        self.runtime_paths
                        .prompts_directory
                    ),
                    "schemas_directory": str(
                        self.runtime_paths
                        .schemas_directory
                    ),
                    "validated_schema_contracts": (
                        validated_schema_contracts
                    ),
                    "validated_prompt_contracts": (
                        validated_prompt_contracts
                    ),
                    "required_schema_count": len(
                        self.REQUIRED_SCHEMA_CONTRACTS
                    ),
                    "required_prompt_count": len(
                        self.REQUIRED_PROMPT_CONTRACTS
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
                    "prompts_directory": str(
                        self.runtime_paths
                        .prompts_directory
                    ),
                    "schemas_directory": str(
                        self.runtime_paths
                        .schemas_directory
                    ),
                    "validated_schema_contracts": (
                        validated_schema_contracts
                    ),
                    "validated_prompt_contracts": (
                        validated_prompt_contracts
                    ),
                    "required_schema_contracts": list(
                        self.REQUIRED_SCHEMA_CONTRACTS
                    ),
                    "required_prompt_contracts": [
                        contract
                        for contract, _ in (
                            self.REQUIRED_PROMPT_CONTRACTS
                        )
                    ],
                },
                error=str(ex),
            )

    def verify(self) -> bool:
        return (
            self.run().status
            == TaskStatus.SUCCESS
        )
