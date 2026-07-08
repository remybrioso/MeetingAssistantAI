"""
artifact_storage_service.py

Persistencia de artefactos del dominio.
"""

import json
from pathlib import Path


class ArtifactStorageService:

    def save(
        self,
        artifact,
        filename: Path
    ) -> None:

        filename.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                artifact.as_dict(),
                file,
                ensure_ascii=False,
                indent=4
            )