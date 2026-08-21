from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

BASE = Path(__file__).resolve().parents[1]
OUTPUT = BASE / "reports" / "production_architecture.pdf"
DIAGRAM = BASE / "reports" / "architecture.png"

PAGE_W, PAGE_H = A4

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=21,
    leading=25,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#17365D"),
    spaceAfter=8
)

subtitle = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontSize=9,
    leading=12,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#666666"),
    spaceAfter=12
)

section = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=17,
    textColor=colors.HexColor("#17365D"),
    spaceBefore=5,
    spaceAfter=7
)

subsection = ParagraphStyle(
    "Subsection",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    textColor=colors.HexColor("#2F5597"),
    spaceBefore=5,
    spaceAfter=3
)

body = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8.3,
    leading=11.5,
    textColor=colors.HexColor("#222222"),
    spaceAfter=4
)

small = ParagraphStyle(
    "Small",
    parent=styles["BodyText"],
    fontSize=7.2,
    leading=9.5,
    textColor=colors.HexColor("#555555")
)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E1F2"))
    canvas.line(15 * mm, 11 * mm, PAGE_W - 15 * mm, 11 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(
        15 * mm,
        6.5 * mm,
        "CredResolve Production Analytics Architecture"
    )
    canvas.drawRightString(
        PAGE_W - 15 * mm,
        6.5 * mm,
        f"Page {doc.page}"
    )
    canvas.restoreState()

def make_table(data, widths):
    table = Table(data, colWidths=widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.2),
        ("LEADING", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5)
    ]))
    return table

def build():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm
    )

    story = []

    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("CredResolve Production Analytics Architecture", title))
    story.append(Paragraph(
        "Production design for controlled collection analytics, governed metrics, "
        "analytical investigation and executive decision-making",
        subtitle
    ))

    story.append(Paragraph("1. Architecture Objective", section))

    story.append(Paragraph(
        "The CredResolve production analytics architecture converts operational "
        "collections data into validated analytical information and finally into "
        "business decisions.",
        body
    ))

    story.append(Paragraph(
        "The architecture prevents raw operational inconsistencies from directly "
        "affecting recovery metrics or investment decisions.",
        body
    ))

    principle = Table(
        [[Paragraph(
            "<b>Core principle:</b> Raw operational data should not directly drive "
            "business decisions. Data must pass through controlled validation, "
            "cleaning, standardization and analytical layers first.",
            body
        )]],
        colWidths=[178 * mm]
    )

    principle.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF2F8")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#2F5597")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))

    story.append(principle)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Architecture Principles", section))

    data = [
        ["Principle", "Implementation"],
        ["Source preservation", "Raw operational records are preserved before transformation."],
        ["Controlled transformation", "Ingestion, validation, cleaning and business logic are separated."],
        ["Account-centric analysis", "account_id is the canonical analytical entity for recovery analysis."],
        ["Governed metrics", "Metrics use documented definitions and appropriate denominators."],
        ["Reproducibility", "SQL, Python and Golden-layer transformations are reproducible."],
        ["Traceability", "Analytical results can be traced back through the data layers."],
        ["Production controls", "Quality, governance, monitoring and orchestration operate across the pipeline."]
    ]

    story.append(make_table(data, [48 * mm, 130 * mm]))

    story.append(Paragraph("3. Business Objectives Supported", section))

    objectives = [
        "Reconstruct monthly recovery and collection performance.",
        "Identify meaningful changes in activity and performance.",
        "Investigate portfolio, DPD, risk, campaign, channel, agent and vendor effects.",
        "Validate payment attribution and analytical entity relationships.",
        "Evaluate the reported 11% recovery improvement.",
        "Perform observational counterfactual analysis.",
        "Evaluate the proposed ₹10 Cr investment.",
        "Produce governed executive reporting."
    ]

    for item in objectives:
        story.append(Paragraph("• " + item, body))

    story.append(PageBreak())

    story.append(Paragraph("4. Data Architecture Layers", section))

    layers = [
        (
            "Data Sources",
            "Operational collections datasets including accounts, borrowers, payments, "
            "calls, campaigns, agents, vendors and collection events."
        ),
        (
            "Acquire",
            "Batch and incremental ingestion brings source data into the analytical "
            "environment while preserving source context."
        ),
        (
            "Raw / Landing",
            "The source-preservation layer used for traceability, auditability and "
            "reprocessing. Business metrics are not calculated directly here."
        ),
        (
            "Staging",
            "Structural preparation including schema normalization, datatype handling, "
            "identifier normalization and timestamp parsing."
        ),
        (
            "Quality Gate",
            "Validation of identifiers, duplicates, relationships, timestamps, payment "
            "attribution and other structural quality conditions."
        ),
        (
            "Clean Layer",
            "Validated and standardized analytical datasets. The current validation "
            "framework recorded 49 of 49 checks passed."
        ),
        (
            "Golden Layer",
            "Stable analytical representation derived from the validated Clean layer. "
            "It provides the controlled source for downstream analytical work."
        )
    ]

    for name, description in layers:
        story.append(Paragraph(name, subsection))
        story.append(Paragraph(description, body))

    story.append(Paragraph("Golden Layer Analytical Decisions", subsection))

    golden = [
        ["Dataset", "Analytical role"],
        ["Accounts", "account_id is the canonical recovery-analysis entity."],
        ["Payments", "Payment attribution follows payment_id → account_id."],
        ["Calls", "Call activity connects accounts, agents, campaigns and vendors."],
        ["Campaigns", "campaign_id provides campaign and strategy context."],
        ["Agents", "agent_id provides operational identity and tenure context."],
        ["Collection events", "Supporting event-level evidence for contact and recovery analysis."]
    ]

    story.append(make_table(golden, [55 * mm, 123 * mm]))

    story.append(Paragraph("5. Data Quality Boundary", section))

    story.append(Paragraph(
        "Data-quality issues are not silently converted into business assumptions. "
        "Records that remain analytically usable can be retained with explicit quality "
        "indicators, while ambiguous issues remain visible for investigation.",
        body
    ))

    story.append(PageBreak())

    story.append(Paragraph("6. Architecture Overview", section))

    story.append(Paragraph(
        "The main production flow is intentionally simple:",
        body
    ))

    story.append(Paragraph(
        "<b>Data Sources → Acquire → Manage → Analyse & Visualise → Business Decision</b>",
        body
    ))

    story.append(Spacer(1, 3))

    if not DIAGRAM.exists():
        raise FileNotFoundError(
            "Architecture diagram not found. Render docs/architecture.mmd first."
        )

    image = Image(str(DIAGRAM))

    max_width = 178 * mm
    max_height = 92 * mm

    image._restrictSize(max_width, max_height)

    story.append(image)

    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "The architecture separates the main analytical pipeline from the "
        "cross-cutting production controls. Data Quality, Governance & Lineage, "
        "Monitoring and Orchestration support the pipeline without creating "
        "unnecessary dependencies between analytical stages.",
        body
    ))

    story.append(Paragraph(
        "The Golden layer acts as the controlled hand-off between data management "
        "and analytical processing. Features and governed metrics are produced "
        "from this stable analytical foundation.",
        body
    ))

    story.append(Paragraph("7. Analytical Processing", subsection))

    analytical = [
        ["Layer", "Purpose"],
        ["Feature Layer", "Reusable DPD, risk, status, loan, agent, campaign, channel and contact features."],
        ["Governed Metrics", "Standardized recovery, payment, contact and conversion measurements."],
        ["Analytical Investigation", "Forensic, statistical, driver, counterfactual and improvement analysis."],
        ["Executive Outputs", "Dashboard, executive memo and decision-support reporting."],
        ["Business Decision", "Recommendations and investment decisions based on governed evidence."]
    ]

    story.append(make_table(analytical, [48 * mm, 130 * mm]))

    story.append(PageBreak())

    story.append(Paragraph("8. Production Operations and Governance", section))

    operations = [
        (
            "Governance and Lineage",
            "Every analytical output should be traceable through Source → Raw/Landing → "
            "Staging → Quality Gate → Clean → Golden → Feature → Metric → Analysis → Output."
        ),
        (
            "Incremental Processing",
            "New or changed records should be processed without rebuilding unaffected historical "
            "data. Downstream features and metrics affected by those records should be refreshed."
        ),
        (
            "Late-Arriving Data",
            "Event timestamp and ingestion timestamp should be retained separately. Late records "
            "should trigger recalculation of affected reporting periods."
        ),
        (
            "Backfills",
            "Historical corrections and transformation changes should use reproducible backfill "
            "processes rather than manual modification of analytical results."
        ),
        (
            "Monitoring",
            "Monitor volume, missing identifiers, duplicates, schema changes, validation failures, "
            "late records, recovery anomalies and portfolio-mix changes."
        ),
        (
            "Anomaly Detection",
            "Unexpected movements in payment volume, recovered amount, answer rate, attempt frequency "
            "or portfolio composition should be flagged for investigation."
        ),
        (
            "Metric Governance",
            "Every metric requires an explicit numerator, denominator, population, time window and "
            "attribution definition."
        )
    ]

    for name, description in operations:
        story.append(Paragraph(name, subsection))
        story.append(Paragraph(description, body))

    story.append(Paragraph("9. Production Operating Model", section))

    model = [
        ["Stage", "Primary responsibility"],
        ["Source", "Operational collection records"],
        ["Acquire", "Batch and incremental acquisition"],
        ["Raw / Landing", "Source preservation and traceability"],
        ["Staging", "Structural preparation"],
        ["Quality Gate", "Validation and exception identification"],
        ["Clean", "Validated analytical datasets"],
        ["Golden", "Stable analytical source"],
        ["Features", "Reusable analytical attributes"],
        ["Metrics", "Governed business measurements"],
        ["Analysis", "Evidence and decision support"],
        ["Outputs", "Dashboard and executive reporting"],
        ["Decision", "Recommendation and investment action"]
    ]

    story.append(make_table(model, [42 * mm, 136 * mm]))

    story.append(Spacer(1, 5))

    story.append(Paragraph(
        "<b>Production principle:</b> A business decision is the final output of a "
        "controlled analytical chain, not a direct interpretation of raw operational data.",
        body
    ))

    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "Architecture status: designed for reproducible analytical processing, "
        "governed metrics, controlled investigation and executive decision support.",
        small
    ))

    doc.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer
    )

    pages = len(PdfReader(str(OUTPUT)).pages)

    if pages != 4:
        raise RuntimeError(f"Expected 4 pages, generated {pages} pages")

    print("Production architecture document created")
    print(f"Output: {OUTPUT}")
    print(f"Pages: {pages}")

if __name__ == "__main__":
    build()