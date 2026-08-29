"""
meeting_report_pdf_exporter.py

Exporta MeetingReport como un documento PDF formal y legible.
"""

from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from models.artifacts.meeting_report import MeetingReport


class MeetingReportPdfExporter:
    """
    Convierte un MeetingReport validado en un PDF formal.

    El exportador es determinista:
    no modifica el dominio, no reinterpreta contenido
    y no realiza llamadas a proveedores de IA.
    """

    PAGE_SIZE = A4

    def export(
        self,
        report: MeetingReport,
        output_file: Path,
    ) -> None:
        """
        Construye y persiste el PDF.
        """

        self._validate_report(
            report
        )
        self._validate_output_file(
            output_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = self._build_pdf_document(
            output_file
        )

        story = self.build_story(
            report
        )

        document.build(
            story,
            onFirstPage=self._draw_page_footer,
            onLaterPages=self._draw_page_footer,
        )

    def build_story(
        self,
        report: MeetingReport,
    ) -> list:
        """
        Construye los elementos Platypus del PDF sin escribir
        físicamente el archivo.

        Esto permite probar la representación de forma aislada.
        """

        self._validate_report(
            report
        )

        data = report.as_dict()
        styles = self._build_styles()

        story: list = []

        self._append_title(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_objective(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_executive_summary(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_key_points(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_topics(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_decisions(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_action_items(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_risks(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_pending_items(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_participants(
            story=story,
            data=data,
            styles=styles,
        )
        self._append_conclusions(
            story=story,
            data=data,
            styles=styles,
        )

        return story

    def _build_pdf_document(
        self,
        output_file: Path,
    ) -> SimpleDocTemplate:
        return SimpleDocTemplate(
            str(
                output_file
            ),
            pagesize=self.PAGE_SIZE,
            rightMargin=0.65 * inch,
            leftMargin=0.65 * inch,
            topMargin=0.65 * inch,
            bottomMargin=0.65 * inch,
            title="Meeting Assistant AI",
            author="Meeting Assistant AI",
            subject="Minuta de reunión",
        )

    def _build_styles(
        self,
    ) -> dict[str, ParagraphStyle]:
        stylesheet = getSampleStyleSheet()

        return {
            "eyebrow": ParagraphStyle(
                "MAIEyebrow",
                parent=stylesheet[
                    "Normal"
                ],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#4B5563"
                ),
                spaceAfter=5,
            ),
            "title": ParagraphStyle(
                "MAITitle",
                parent=stylesheet[
                    "Title"
                ],
                fontName="Helvetica-Bold",
                fontSize=19,
                leading=23,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#111827"
                ),
                spaceAfter=5,
            ),
            "metadata": ParagraphStyle(
                "MAIMetadata",
                parent=stylesheet[
                    "Normal"
                ],
                fontName="Helvetica-Oblique",
                fontSize=8,
                leading=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#6B7280"
                ),
                spaceAfter=15,
            ),
            "heading": ParagraphStyle(
                "MAIHeading",
                parent=stylesheet[
                    "Heading1"
                ],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=16,
                textColor=colors.HexColor(
                    "#111827"
                ),
                spaceBefore=10,
                spaceAfter=5,
                keepWithNext=True,
            ),
            "subheading": ParagraphStyle(
                "MAISubheading",
                parent=stylesheet[
                    "Heading2"
                ],
                fontName="Helvetica-Bold",
                fontSize=10.5,
                leading=13,
                textColor=colors.HexColor(
                    "#1F2937"
                ),
                spaceBefore=7,
                spaceAfter=3,
                keepWithNext=True,
            ),
            "body": ParagraphStyle(
                "MAIBody",
                parent=stylesheet[
                    "BodyText"
                ],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor(
                    "#1F2937"
                ),
                spaceAfter=6,
            ),
            "bullet": ParagraphStyle(
                "MAIBullet",
                parent=stylesheet[
                    "BodyText"
                ],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13,
                leftIndent=14,
                firstLineIndent=-8,
                bulletIndent=6,
                textColor=colors.HexColor(
                    "#1F2937"
                ),
                spaceAfter=3,
            ),
            "empty": ParagraphStyle(
                "MAIEmpty",
                parent=stylesheet[
                    "BodyText"
                ],
                fontName="Helvetica-Oblique",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor(
                    "#6B7280"
                ),
                spaceAfter=6,
            ),
            "evidence_label": ParagraphStyle(
                "MAIEvidenceLabel",
                parent=stylesheet[
                    "BodyText"
                ],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=10,
                textColor=colors.HexColor(
                    "#374151"
                ),
                spaceBefore=3,
                spaceAfter=2,
            ),
            "evidence": ParagraphStyle(
                "MAIEvidence",
                parent=stylesheet[
                    "BodyText"
                ],
                fontName="Helvetica",
                fontSize=8.3,
                leading=11,
                leftIndent=8,
                rightIndent=8,
                borderColor=colors.HexColor(
                    "#E5E7EB"
                ),
                borderWidth=0.5,
                borderPadding=6,
                backColor=colors.HexColor(
                    "#F9FAFB"
                ),
                textColor=colors.HexColor(
                    "#374151"
                ),
                spaceAfter=4,
            ),
            "table_label": ParagraphStyle(
                "MAITableLabel",
                parent=stylesheet[
                    "BodyText"
                ],
                fontName="Helvetica-Bold",
                fontSize=7.5,
                leading=9,
                textColor=colors.HexColor(
                    "#374151"
                ),
                spaceAfter=1,
            ),
            "table_value": ParagraphStyle(
                "MAITableValue",
                parent=stylesheet[
                    "BodyText"
                ],
                fontName="Helvetica",
                fontSize=8.5,
                leading=10,
                textColor=colors.HexColor(
                    "#111827"
                ),
            ),
        }

    def _append_title(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        story.append(
            Paragraph(
                "MINUTA DE REUNIÓN",
                styles["eyebrow"],
            )
        )

        story.append(
            Paragraph(
                self._escape_text(
                    data[
                        "title"
                    ]
                ),
                styles["title"],
            )
        )

        created_at = self._format_created_at(
            data.get(
                "created_at"
            )
        )

        metadata = (
            "Generado por Meeting Assistant AI"
        )

        if created_at:
            metadata += (
                f" - {created_at}"
            )

        story.append(
            Paragraph(
                self._escape_text(
                    metadata
                ),
                styles["metadata"],
            )
        )

    def _append_objective(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Objetivo",
            styles,
        )

        objective = data.get(
            "objective"
        )

        self._add_body(
            story,
            (
                objective
                if objective
                else (
                    "No se identificó un objetivo "
                    "explícito en la reunión."
                )
            ),
            styles,
        )

    def _append_executive_summary(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Resumen ejecutivo",
            styles,
        )

        self._add_body(
            story,
            data[
                "executive_summary"
            ],
            styles,
        )

    def _append_key_points(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Puntos clave",
            styles,
        )

        for point in data[
            "key_points"
        ]:
            story.append(
                Paragraph(
                    (
                        "• "
                        + self._escape_text(
                            point
                        )
                    ),
                    styles[
                        "bullet"
                    ],
                )
            )

    def _append_topics(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Temas tratados",
            styles,
        )

        topics = data.get(
            "topics",
            [],
        )

        if not topics:
            self._add_empty_message(
                story,
                (
                    "No se registraron temas "
                    "adicionales."
                ),
                styles,
            )
            return

        for index, topic in enumerate(
            topics,
            start=1,
        ):
            self._add_subheading(
                story,
                (
                    f"{index}. "
                    f"{topic['title']}"
                ),
                styles,
            )

            self._add_body(
                story,
                topic[
                    "summary"
                ],
                styles,
            )

            self._append_evidence(
                story=story,
                evidence=topic.get(
                    "evidence",
                    [],
                ),
                styles=styles,
            )

    def _append_decisions(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Decisiones",
            styles,
        )

        decisions = data.get(
            "decisions",
            [],
        )

        if not decisions:
            self._add_empty_message(
                story,
                "No se registraron decisiones.",
                styles,
            )
            return

        for index, decision in enumerate(
            decisions,
            start=1,
        ):
            self._add_subheading(
                story,
                f"Decisión {index}",
                styles,
            )

            self._add_body(
                story,
                decision[
                    "description"
                ],
                styles,
            )

            rationale = decision.get(
                "rationale"
            )

            if rationale:
                self._add_labeled_text(
                    story=story,
                    label="Justificación",
                    value=rationale,
                    styles=styles,
                )

            self._append_evidence(
                story=story,
                evidence=decision.get(
                    "evidence",
                    [],
                ),
                styles=styles,
            )

    def _append_action_items(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Acciones y compromisos",
            styles,
        )

        actions = data.get(
            "action_items",
            [],
        )

        if not actions:
            self._add_empty_message(
                story,
                (
                    "No se registraron acciones "
                    "o compromisos."
                ),
                styles,
            )
            return

        for index, action in enumerate(
            actions,
            start=1,
        ):
            self._add_subheading(
                story,
                f"Acción {index}",
                styles,
            )

            self._add_body(
                story,
                action[
                    "description"
                ],
                styles,
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

            story.append(
                self._build_action_table(
                    owner=(
                        owner_name
                        or "No asignado"
                    ),
                    due_date=(
                        action.get(
                            "due_date"
                        )
                        or "No definida"
                    ),
                    status=self._format_status(
                        action.get(
                            "status"
                        )
                    ),
                    styles=styles,
                )
            )

            story.append(
                Spacer(
                    1,
                    5,
                )
            )

            self._append_evidence(
                story=story,
                evidence=action.get(
                    "evidence",
                    [],
                ),
                styles=styles,
            )

    def _append_risks(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Riesgos y bloqueos",
            styles,
        )

        risks = data.get(
            "risks",
            [],
        )

        if not risks:
            self._add_empty_message(
                story,
                (
                    "No se registraron riesgos "
                    "o bloqueos."
                ),
                styles,
            )
            return

        for index, risk in enumerate(
            risks,
            start=1,
        ):
            self._add_subheading(
                story,
                f"Riesgo {index}",
                styles,
            )

            self._add_body(
                story,
                risk[
                    "description"
                ],
                styles,
            )

            impact = risk.get(
                "impact"
            )

            if impact:
                self._add_labeled_text(
                    story=story,
                    label="Impacto",
                    value=impact,
                    styles=styles,
                )

            self._append_evidence(
                story=story,
                evidence=risk.get(
                    "evidence",
                    [],
                ),
                styles=styles,
            )

    def _append_pending_items(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Asuntos pendientes",
            styles,
        )

        pending_items = data.get(
            "pending_items",
            [],
        )

        if not pending_items:
            self._add_empty_message(
                story,
                (
                    "No se registraron asuntos "
                    "pendientes."
                ),
                styles,
            )
            return

        for index, pending in enumerate(
            pending_items,
            start=1,
        ):
            self._add_subheading(
                story,
                f"Pendiente {index}",
                styles,
            )

            self._add_body(
                story,
                pending[
                    "description"
                ],
                styles,
            )

            self._append_evidence(
                story=story,
                evidence=pending.get(
                    "evidence",
                    [],
                ),
                styles=styles,
            )

    def _append_participants(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Participantes",
            styles,
        )

        participants = data.get(
            "participants",
            [],
        )

        if not participants:
            self._add_empty_message(
                story,
                (
                    "No fue posible identificar "
                    "participantes."
                ),
                styles,
            )
            return

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

            text = name

            if details:
                text += (
                    " - "
                    + ", ".join(
                        details
                    )
                )

            story.append(
                Paragraph(
                    (
                        "• "
                        + self._escape_text(
                            text
                        )
                    ),
                    styles[
                        "bullet"
                    ],
                )
            )

    def _append_conclusions(
        self,
        story: list,
        data: dict,
        styles: dict,
    ) -> None:
        self._add_heading(
            story,
            "Conclusiones",
            styles,
        )

        conclusions = data.get(
            "conclusions",
            [],
        )

        if not conclusions:
            self._add_empty_message(
                story,
                (
                    "No se registraron conclusiones "
                    "explícitas."
                ),
                styles,
            )
            return

        for conclusion in conclusions:
            story.append(
                Paragraph(
                    (
                        "• "
                        + self._escape_text(
                            conclusion
                        )
                    ),
                    styles[
                        "bullet"
                    ],
                )
            )

    def _append_evidence(
        self,
        story: list,
        evidence: list[dict],
        styles: dict,
    ) -> None:
        if not evidence:
            return

        evidence_flowables = [
            Paragraph(
                "Evidencia",
                styles[
                    "evidence_label"
                ],
            )
        ]

        for reference in evidence:
            start = self._format_timestamp(
                reference[
                    "start"
                ]
            )
            end = self._format_timestamp(
                reference[
                    "end"
                ]
            )

            speaker = self._escape_text(
                reference[
                    "speaker"
                ]
            )
            excerpt = self._escape_text(
                reference[
                    "excerpt"
                ]
            )

            evidence_flowables.append(
                Paragraph(
                    (
                        f"<b>{start} - {end} · "
                        f"{speaker}:</b> "
                        f"&quot;{excerpt}&quot;"
                    ),
                    styles[
                        "evidence"
                    ],
                )
            )

        story.append(
            KeepTogether(
                evidence_flowables[
                    :2
                ]
            )
        )

        story.extend(
            evidence_flowables[
                2:
            ]
        )

    def _build_action_table(
        self,
        owner: str,
        due_date: str,
        status: str,
        styles: dict,
    ) -> Table:
        values = [
            (
                "Responsable",
                owner,
            ),
            (
                "Fecha límite",
                due_date,
            ),
            (
                "Estado",
                status,
            ),
        ]

        cells = []

        for label, value in values:
            cells.append(
                Paragraph(
                    (
                        f"<b>{self._escape_text(label)}</b>"
                        "<br/>"
                        f"{self._escape_text(value)}"
                    ),
                    styles[
                        "table_value"
                    ],
                )
            )

        table = Table(
            [
                cells
            ],
            colWidths=[
                1.62 * inch,
                1.62 * inch,
                1.62 * inch,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (
                            0,
                            0,
                        ),
                        (
                            -1,
                            -1,
                        ),
                        colors.HexColor(
                            "#F3F4F6"
                        ),
                    ),
                    (
                        "BOX",
                        (
                            0,
                            0,
                        ),
                        (
                            -1,
                            -1,
                        ),
                        0.5,
                        colors.HexColor(
                            "#D1D5DB"
                        ),
                    ),
                    (
                        "INNERGRID",
                        (
                            0,
                            0,
                        ),
                        (
                            -1,
                            -1,
                        ),
                        0.5,
                        colors.HexColor(
                            "#D1D5DB"
                        ),
                    ),
                    (
                        "VALIGN",
                        (
                            0,
                            0,
                        ),
                        (
                            -1,
                            -1,
                        ),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (
                            0,
                            0,
                        ),
                        (
                            -1,
                            -1,
                        ),
                        7,
                    ),
                    (
                        "RIGHTPADDING",
                        (
                            0,
                            0,
                        ),
                        (
                            -1,
                            -1,
                        ),
                        7,
                    ),
                    (
                        "TOPPADDING",
                        (
                            0,
                            0,
                        ),
                        (
                            -1,
                            -1,
                        ),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (
                            0,
                            0,
                        ),
                        (
                            -1,
                            -1,
                        ),
                        6,
                    ),
                ]
            )
        )

        return table

    def _add_heading(
        self,
        story: list,
        text: str,
        styles: dict,
    ) -> None:
        story.append(
            Paragraph(
                self._escape_text(
                    text
                ),
                styles["heading"],
            )
        )

    def _add_subheading(
        self,
        story: list,
        text: str,
        styles: dict,
    ) -> None:
        story.append(
            Paragraph(
                self._escape_text(
                    text
                ),
                styles[
                    "subheading"
                ],
            )
        )

    def _add_body(
        self,
        story: list,
        text: str,
        styles: dict,
    ) -> None:
        story.append(
            Paragraph(
                self._escape_text(
                    text
                ),
                styles["body"],
            )
        )

    def _add_empty_message(
        self,
        story: list,
        text: str,
        styles: dict,
    ) -> None:
        story.append(
            Paragraph(
                self._escape_text(
                    text
                ),
                styles["empty"],
            )
        )

    def _add_labeled_text(
        self,
        story: list,
        label: str,
        value: str,
        styles: dict,
    ) -> None:
        story.append(
            Paragraph(
                (
                    f"<b>{self._escape_text(label)}:</b> "
                    f"{self._escape_text(value)}"
                ),
                styles["body"],
            )
        )

    @staticmethod
    def _draw_page_footer(
        canvas,
        document,
    ) -> None:
        canvas.saveState()

        width, _ = (
            document.pagesize
        )

        page_number = (
            canvas.getPageNumber()
        )

        canvas.setFont(
            "Helvetica",
            7.5,
        )
        canvas.setFillColor(
            colors.HexColor(
                "#6B7280"
            )
        )

        canvas.drawCentredString(
            width / 2,
            0.34 * inch,
            (
                "Meeting Assistant AI - "
                f"Página {page_number}"
            ),
        )

        canvas.restoreState()

    @staticmethod
    def _escape_text(
        value,
    ) -> str:
        if value is None:
            return ""

        return escape(
            str(
                value
            )
        )

    @staticmethod
    def _format_created_at(
        value: str | None,
    ) -> str | None:
        if not value:
            return None

        try:
            parsed = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError:
            return value

        formatted = parsed.strftime(
            "%d/%m/%Y %H:%M"
        )

        timezone_name = (
            parsed.tzname()
            if parsed.tzinfo
            else None
        )

        if timezone_name:
            formatted += (
                f" {timezone_name}"
            )

        return formatted

    @staticmethod
    def _format_timestamp(
        seconds: float,
    ) -> str:
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

    @staticmethod
    def _validate_report(
        report,
    ) -> None:
        if not isinstance(
            report,
            MeetingReport,
        ):
            raise TypeError(
                "report debe ser una instancia "
                "de MeetingReport."
            )

    @staticmethod
    def _validate_output_file(
        output_file,
    ) -> None:
        if not isinstance(
            output_file,
            Path,
        ):
            raise TypeError(
                "output_file debe ser una instancia "
                "de Path."
            )

        if (
            output_file.suffix.lower()
            != ".pdf"
        ):
            raise ValueError(
                "output_file debe usar extensión .pdf."
            )
