"""
summary_markdown_exporter.py

Exporta Summary a Markdown.
"""

from pathlib import Path

from models.artifacts.summary import Summary
from services.template_engine import TemplateEngine


class SummaryMarkdownExporter:

    def __init__(self):

        self.template_engine = TemplateEngine()

    def export(
        self,
        summary: Summary,
        output_file: Path
    ) -> None:

        key_points = "\n".join(
            f"- {point}"
            for point in summary.key_points
        )

        markdown = self.template_engine.render(
            Path("templates/summary.md"),
            {
                "TITLE": summary.title,
                "EXECUTIVE_SUMMARY": summary.executive_summary,
                "KEY_POINTS": key_points,
            }
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(
            markdown,
            encoding="utf-8"
        )