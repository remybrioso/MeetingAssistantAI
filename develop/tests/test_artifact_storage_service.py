import json
from pathlib import Path

from models.artifacts.summary import Summary
from services.artifact_storage_service import ArtifactStorageService


output_dir = Path("output") / "test_artifacts"
output_file = output_dir / "summary.json"

summary = Summary(
    artifact_type="summary",
    provider="ollama",
    model="qwen2.5:3b",
    prompt_version="summary_v1",
    title="Resumen Ejecutivo",
    executive_summary=(
        "Durante la reunión se revisó el avance del proyecto "
        "Meeting Assistant AI y se validó el almacenamiento de artefactos."
    ),
    key_points=[
        "Se creó ArtifactStorageService.",
        "Se validó summary.json.",
        "Se mantiene la arquitectura por dominio."
    ]
)

storage = ArtifactStorageService()

storage.save(
    summary,
    output_file
)

assert output_file.exists()

with open(output_file, "r", encoding="utf-8") as file:
    data = json.load(file)

print(data)

assert data["title"] == "Resumen Ejecutivo"
assert data["artifact_type"] == "summary"

print()
print("ArtifactStorageService validado correctamente.")