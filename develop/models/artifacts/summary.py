"""
summary.py

Dominio del resumen ejecutivo.
"""

from dataclasses import dataclass, field

from models.artifacts.artifact import Artifact


@dataclass
class Summary(Artifact):

    title: str = ""

    executive_summary: str = ""

    key_points: list[str] = field(default_factory=list)

    def as_dict(self):

        data = super().as_dict()

        data.update(
            {
                "title": self.title,
                "executive_summary": self.executive_summary,
                "key_points": self.key_points
            }
        )

        return data