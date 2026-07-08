"""
template_engine.py

Motor simple de plantillas.
"""

from pathlib import Path


class TemplateEngine:

    def render(
        self,
        template_file: Path,
        context: dict
    ) -> str:

        content = template_file.read_text(
            encoding="utf-8"
        )

        for key, value in context.items():

            content = content.replace(
                "{{" + key + "}}",
                str(value)
            )

        return content