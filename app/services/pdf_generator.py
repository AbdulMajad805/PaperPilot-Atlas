
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable,
)


def generate_pdf_report(markdown_path: str, pdf_path: str) -> Path:
    source = Path(markdown_path)
    destination = Path(pdf_path)

    if not source.exists():
        raise FileNotFoundError(f"Markdown report not found: {source}")

    markdown = source.read_text(encoding="utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="PaperPilot AI Research Report",
        author="PaperPilot AI",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=32,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#174C3C"),
        spaceAfter=20,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading1"],
        fontSize=17,
        leading=22,
        textColor=colors.HexColor("#174C3C"),
        spaceBefore=18,
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        name="SubHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#287A5B"),
        spaceBefore=12,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=15,
        alignment=TA_LEFT,
        spaceAfter=7,
    ))

    story = []

    for line in markdown.splitlines():
        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
            continue

        if line == "---":
            story.append(HRFlowable(
                width="100%",
                thickness=0.6,
                color=colors.HexColor("#D5E5DC"),
            ))
            story.append(Spacer(1, 8))
            continue

        if line.startswith("# "):
            story.append(Spacer(1, 35))
            story.append(Paragraph(
                escape(line[2:]),
                styles["ReportTitle"],
            ))
            continue

        if line.startswith("## "):
            story.append(Paragraph(
                escape(line[3:]),
                styles["SectionHeading"],
            ))
            continue

        if line.startswith("### "):
            story.append(Paragraph(
                escape(line[4:]),
                styles["SubHeading"],
            ))
            continue

        if line.startswith("- "):
            text = escape(line[2:])
            story.append(Paragraph(
                f"&bull;&nbsp;&nbsp;{text}",
                styles["ReportBody"],
            ))
            continue

        if line.startswith("*") and line.endswith("*"):
            story.append(Paragraph(
                f"<i>{escape(line.strip('*'))}</i>",
                styles["ReportBody"],
            ))
            continue

        # Handle bold text
        import re
        text = escape(line)
        text = re.sub(
            r"\*\*(.*?)\*\*",
            r"<b>\1</b>",
            text,
        )

        story.append(Paragraph(text, styles["ReportBody"]))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))

        canvas.drawString(
            20 * mm,
            12 * mm,
            "PaperPilot AI | Research Analysis",
        )

        canvas.drawRightString(
            A4[0] - 20 * mm,
            12 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return destination
