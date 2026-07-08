from pathlib import Path

from models.artifacts.summary import Summary
from services.summary_markdown_exporter import SummaryMarkdownExporter


summary = Summary(
    artifact_type="summary",
    provider="ollama",
    model="qwen2.5:3b",
    prompt_version="summary_v1",
    title="Resumen Ejecutivo",
    executive_summary=(
        "Durante la reunión se revisó el avance del proyecto "
        "Meeting Assistant AI y se validó la exportación Markdown."
    ),
    key_points=[
        "Se creó TemplateEngine.",
        "Se creó SummaryMarkdownExporter.",
        "Se generó summary.md."
    ]
)

output_file = Path("output") / "test_artifacts" / "summary.md"

exporter = SummaryMarkdownExporter()

exporter.export(
    summary,
    output_file
)

assert output_file.exists()

content = output_file.read_text(
    encoding="utf-8"
)

print(content)

assert "# Resumen Ejecutivo" in content
assert "- Se creó TemplateEngine." in content

print()
print("SummaryMarkdownExporter validado correctamente.")