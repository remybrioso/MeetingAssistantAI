"""
meeting_report_markdown_exporter.py

Exporta MeetingReport como un documento Markdown
formal y legible.
"""

from pathlib import Path

from models.artifacts.meeting_report import MeetingReport


class MeetingReportMarkdownExporter:
    """
    Convierte un MeetingReport validado en un documento
    Markdown formal.

    El exportador no modifica el dominio ni realiza
    validación semántica.
    """

    def export(
        self,
        report: MeetingReport,
        output_file: Path,
    ) -> None:
        """
        Exporta MeetingReport a Markdown.

        Args:
            report:
                Reporte de reunión a exportar.

            output_file:
                Archivo Markdown de destino.
        """

        if not isinstance(
            report,
            MeetingReport,
        ):
            raise TypeError(
                "report debe ser una instancia "
                "de MeetingReport."
            )

        if not isinstance(
            output_file,
            Path,
        ):
            raise TypeError(
                "output_file debe ser una instancia "
                "de Path."
            )

        markdown = self.render(
            report
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file.write_text(
            markdown,
            encoding="utf-8",
        )

    def render(
        self,
        report: MeetingReport,
    ) -> str:
        """
        Construye el documento Markdown sin escribirlo
        físicamente.

        Esto permite probar o reutilizar la representación
        independientemente del sistema de archivos.
        """

        if not isinstance(
            report,
            MeetingReport,
        ):
            raise TypeError(
                "report debe ser una instancia "
                "de MeetingReport."
            )

        data = report.as_dict()

        sections = [
            self._render_header(
                data
            ),
            self._render_executive_summary(
                data
            ),
            self._render_key_points(
                data
            ),
            self._render_topics(
                data
            ),
            self._render_decisions(
                data
            ),
            self._render_action_items(
                data
            ),
            self._render_risks(
                data
            ),
            self._render_pending_items(
                data
            ),
            self._render_participants(
                data
            ),
            self._render_conclusions(
                data
            ),
        ]

        return (
            "\n\n".join(
                section
                for section in sections
                if section
            ).strip()
            + "\n"
        )

    @staticmethod
    def _render_header(
        data: dict,
    ) -> str:
        lines = [
            f"# {data['title']}",
            "",
            "## Objetivo",
            "",
        ]

        objective = data.get(
            "objective"
        )

        lines.append(
            objective
            if objective
            else (
                "No se identificó un objetivo explícito "
                "en la reunión."
            )
        )

        return "\n".join(
            lines
        )

    @staticmethod
    def _render_executive_summary(
        data: dict,
    ) -> str:
        return "\n".join(
            [
                "## Resumen ejecutivo",
                "",
                data[
                    "executive_summary"
                ],
            ]
        )

    @staticmethod
    def _render_key_points(
        data: dict,
    ) -> str:
        lines = [
            "## Puntos clave",
            "",
        ]

        for point in data[
            "key_points"
        ]:
            lines.append(
                f"- {point}"
            )

        return "\n".join(
            lines
        )

    def _render_topics(
        self,
        data: dict,
    ) -> str:
        lines = [
            "## Temas tratados",
            "",
        ]

        topics = data.get(
            "topics",
            [],
        )

        if not topics:
            lines.append(
                "No se registraron temas adicionales."
            )

            return "\n".join(
                lines
            )

        for index, topic in enumerate(
            topics,
            start=1,
        ):
            lines.extend(
                [
                    (
                        f"### {index}. "
                        f"{topic['title']}"
                    ),
                    "",
                    topic[
                        "summary"
                    ],
                ]
            )

            self._append_evidence(
                lines=lines,
                evidence=topic.get(
                    "evidence",
                    [],
                ),
            )

        return "\n".join(
            lines
        )

    def _render_decisions(
        self,
        data: dict,
    ) -> str:
        lines = [
            "## Decisiones",
            "",
        ]

        decisions = data.get(
            "decisions",
            [],
        )

        if not decisions:
            lines.append(
                "No se registraron decisiones."
            )

            return "\n".join(
                lines
            )

        for index, decision in enumerate(
            decisions,
            start=1,
        ):
            lines.extend(
                [
                    (
                        f"### Decisión {index}"
                    ),
                    "",
                    decision[
                        "description"
                    ],
                ]
            )

            rationale = decision.get(
                "rationale"
            )

            if rationale:
                lines.extend(
                    [
                        "",
                        (
                            f"**Justificación:** "
                            f"{rationale}"
                        ),
                    ]
                )

            self._append_evidence(
                lines=lines,
                evidence=decision.get(
                    "evidence",
                    [],
                ),
            )

        return "\n".join(
            lines
        )

    def _render_action_items(
        self,
        data: dict,
    ) -> str:
        lines = [
            "## Acciones y compromisos",
            "",
        ]

        action_items = data.get(
            "action_items",
            [],
        )

        if not action_items:
            lines.append(
                "No se registraron acciones o compromisos."
            )

            return "\n".join(
                lines
            )

        for index, action in enumerate(
            action_items,
            start=1,
        ):
            lines.extend(
                [
                    (
                        f"### Acción {index}"
                    ),
                    "",
                    action[
                        "description"
                    ],
                    "",
                ]
            )

            owner = action.get(
                "owner"
            )

            owner_name = (
                owner.get(
                    "display_name"
                )
                if owner
                else None
            )

            lines.append(
                "**Responsable:** "
                + (
                    owner_name
                    if owner_name
                    else "No asignado"
                )
            )

            due_date = action.get(
                "due_date"
            )

            lines.append(
                "**Fecha límite:** "
                + (
                    due_date
                    if due_date
                    else "No definida"
                )
            )

            lines.append(
                "**Estado:** "
                + self._format_status(
                    action.get(
                        "status"
                    )
                )
            )

            self._append_evidence(
                lines=lines,
                evidence=action.get(
                    "evidence",
                    [],
                ),
            )

        return "\n".join(
            lines
        )

    def _render_risks(
        self,
        data: dict,
    ) -> str:
        lines = [
            "## Riesgos y bloqueos",
            "",
        ]

        risks = data.get(
            "risks",
            [],
        )

        if not risks:
            lines.append(
                "No se registraron riesgos o bloqueos."
            )

            return "\n".join(
                lines
            )

        for index, risk in enumerate(
            risks,
            start=1,
        ):
            lines.extend(
                [
                    (
                        f"### Riesgo {index}"
                    ),
                    "",
                    risk[
                        "description"
                    ],
                ]
            )

            impact = risk.get(
                "impact"
            )

            if impact:
                lines.extend(
                    [
                        "",
                        (
                            f"**Impacto:** "
                            f"{impact}"
                        ),
                    ]
                )

            self._append_evidence(
                lines=lines,
                evidence=risk.get(
                    "evidence",
                    [],
                ),
            )

        return "\n".join(
            lines
        )

    def _render_pending_items(
        self,
        data: dict,
    ) -> str:
        lines = [
            "## Asuntos pendientes",
            "",
        ]

        pending_items = data.get(
            "pending_items",
            [],
        )

        if not pending_items:
            lines.append(
                "No se registraron asuntos pendientes."
            )

            return "\n".join(
                lines
            )

        for index, pending in enumerate(
            pending_items,
            start=1,
        ):
            lines.extend(
                [
                    (
                        f"### Pendiente {index}"
                    ),
                    "",
                    pending[
                        "description"
                    ],
                ]
            )

            self._append_evidence(
                lines=lines,
                evidence=pending.get(
                    "evidence",
                    [],
                ),
            )

        return "\n".join(
            lines
        )

    @staticmethod
    def _render_participants(
        data: dict,
    ) -> str:
        lines = [
            "## Participantes",
            "",
        ]

        participants = data.get(
            "participants",
            [],
        )

        if not participants:
            lines.append(
                "No fue posible identificar participantes."
            )

            return "\n".join(
                lines
            )

        for participant in participants:
            name = (
                participant.get(
                    "name"
                )
                or participant.get(
                    "speaker"
                )
                or "Participante"
            )

            details = []

            speaker = participant.get(
                "speaker"
            )

            role = participant.get(
                "role"
            )

            if speaker:
                details.append(
                    f"speaker: {speaker}"
                )

            if role:
                details.append(
                    f"rol: {role}"
                )

            if details:
                lines.append(
                    f"- **{name}** — "
                    + ", ".join(
                        details
                    )
                )
            else:
                lines.append(
                    f"- **{name}**"
                )

        return "\n".join(
            lines
        )

    @staticmethod
    def _render_conclusions(
        data: dict,
    ) -> str:
        lines = [
            "## Conclusiones",
            "",
        ]

        conclusions = data.get(
            "conclusions",
            [],
        )

        if not conclusions:
            lines.append(
                "No se registraron conclusiones explícitas."
            )

            return "\n".join(
                lines
            )

        for conclusion in conclusions:
            lines.append(
                f"- {conclusion}"
            )

        return "\n".join(
            lines
        )

    @staticmethod
    def _append_evidence(
        lines: list[str],
        evidence: list[dict],
    ) -> None:
        """
        Añade trazabilidad documental cuando existe
        evidencia enlazada.
        """

        if not evidence:
            return

        lines.extend(
            [
                "",
                "**Evidencia:**",
                "",
            ]
        )

        for reference in evidence:
            speaker = reference[
                "speaker"
            ]

            start = (
                MeetingReportMarkdownExporter
                ._format_timestamp(
                    reference[
                        "start"
                    ]
                )
            )

            end = (
                MeetingReportMarkdownExporter
                ._format_timestamp(
                    reference[
                        "end"
                    ]
                )
            )

            excerpt = reference[
                "excerpt"
            ]

            lines.append(
                (
                    f"- `{start}–{end}` "
                    f"**{speaker}:** "
                    f"“{excerpt}”"
                )
            )

    @staticmethod
    def _format_timestamp(
        seconds: float,
    ) -> str:
        """
        Convierte segundos a HH:MM:SS.
        """

        total_seconds = int(
            seconds
        )

        hours, remainder = divmod(
            total_seconds,
            3600,
        )

        minutes, seconds_value = divmod(
            remainder,
            60,
        )

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds_value:02d}"
        )

    @staticmethod
    def _format_status(
        status: str | None,
    ) -> str:
        labels = {
            "unknown": "No especificado",
            "pending": "Pendiente",
            "completed": "Completado",
            "cancelled": "Cancelado",
        }

        return labels.get(
            status,
            "No especificado",
        )