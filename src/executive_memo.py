from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib import colors

BASE = Path(__file__).resolve().parents[1]
OUTPUT = BASE / "reports" / "executive_memo.pdf"

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=16 * mm,
    leftMargin=16 * mm,
    topMargin=14 * mm,
    bottomMargin=14 * mm
)

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontSize=19,
    leading=23,
    alignment=TA_CENTER,
    spaceAfter=6
)

subtitle = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontSize=9,
    alignment=TA_CENTER,
    textColor=colors.grey,
    spaceAfter=12
)

heading = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontSize=11.5,
    leading=14,
    spaceBefore=7,
    spaceAfter=4
)

body = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=8.8,
    leading=12,
    spaceAfter=5
)

small = ParagraphStyle(
    "Small",
    parent=styles["BodyText"],
    fontSize=7.5,
    leading=10,
    textColor=colors.grey
)

decision = ParagraphStyle(
    "Decision",
    parent=styles["BodyText"],
    fontSize=10,
    leading=13,
    spaceAfter=5
)

story = []

story.append(Paragraph(
    "CredResolve Executive Decision Memo",
    title
))

story.append(Paragraph(
    "Recovery Performance, 11% Improvement Assessment and ₹10 Cr Investment Decision",
    subtitle
))

kpi_data = [
    [
        Paragraph("<b>Recovered Amount</b><br/>₹1,315.58 Cr", body),
        Paragraph("<b>Successful Payments</b><br/>17,534", body),
        Paragraph("<b>Recovery Rate</b><br/>12.54%", body),
        Paragraph("<b>11% Improvement</b><br/>UNVERIFIED", body)
    ]
]

kpi_table = Table(
    kpi_data,
    colWidths=[43 * mm, 43 * mm, 43 * mm, 43 * mm]
)

kpi_table.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 0.7, colors.grey),
    ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
]))

story.append(kpi_table)
story.append(Spacer(1, 7))

story.append(Paragraph("1. Executive Conclusion", heading))

story.append(Paragraph(
    "<b>The reported 11% improvement should not be accepted as a proven "
    "recovery-rate improvement.</b> The available data supports descriptive "
    "evidence of recovery and collection activity, but historical monthly "
    "eligible outstanding-balance denominators are unavailable. Portfolio "
    "mix, cohort comparability, selection, survivorship, attribution timing, "
    "and boundary-period effects also prevent a causal conclusion.",
    body
))

story.append(Paragraph(
    "The recommended business action is therefore a controlled collections "
    "and contactability pilot rather than an unconditional ₹10 Cr rollout.",
    decision
))

story.append(Paragraph("2. What Happened?", heading))

story.append(Paragraph(
    "The observed activity period is 2025-12 to 2026-08. December contains "
    "extremely low activity and August is materially lower than preceding "
    "months, so both boundary periods require caution.",
    body
))

story.append(Paragraph(
    "Among the observed months, March recorded the highest recovered amount "
    "at ₹188.91 million and the highest successful-payment count at 2,524. "
    "June recorded the highest observed answer rate at 20.40%.",
    body
))

story.append(Paragraph(
    "The monthly movement analysis identifies substantial volume changes, "
    "but those changes cannot by themselves establish an operational cause.",
    body
))

story.append(Paragraph("3. Why Did It Happen?", heading))

driver_data = [
    ["Observed driver", "Best observed segment", "Recovery rate"],
    ["DPD", "31–60", "13.20%"],
    ["Loan type", "Consumer", "12.88%"],
    ["Account status", "Writeoff", "12.63%"],
    ["Risk segment", "Medium", "12.58%"]
]

driver_table = Table(
    driver_data,
    colWidths=[50 * mm, 65 * mm, 45 * mm]
)

driver_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5)
]))

story.append(driver_table)
story.append(Spacer(1, 5))

story.append(Paragraph(
    "These are observed segment differences, not proven causal drivers. "
    "Campaign, channel, vendor, agent, calling-time, and attempt-frequency "
    "differences also require controls for portfolio composition and "
    "selection before being treated as causal explanations.",
    body
))

story.append(PageBreak())

story.append(Paragraph("4. Is the Reported 11% Improvement Real?", heading))

story.append(Paragraph(
    "<b>Decision: UNVERIFIED.</b>",
    decision
))

story.append(Paragraph(
    "The current portfolio recovery rate is 12.54%, calculated using the "
    "available current outstanding denominator. This cannot be used to "
    "reconstruct historical monthly recovery rates because historical "
    "eligible outstanding balances are not available.",
    body
))

story.append(Paragraph(
    "The counterfactual analysis compared accounts with at least one "
    "answered call against accounts without an answered call within common "
    "portfolio strata. The observed payment-account rates were 44.70% and "
    "43.94%, respectively, producing a +0.76 percentage-point difference.",
    body
))

story.append(Paragraph(
    "This difference is observational. It does not establish that answered "
    "calls caused the additional payments because treatment was not randomly "
    "assigned and contact selection may be related to account characteristics, "
    "priority, timing, campaign exposure, or agent allocation.",
    body
))

story.append(Paragraph("5. ₹10 Cr Investment Decision", heading))

investment_data = [
    ["Decision", "Controlled pilot"],
    ["Investment considered", "₹10 Cr"],
    ["Observed payment-rate difference", "+0.76 percentage points"],
    ["Break-even requirement", "1,010 additional paying accounts"],
    ["Scale condition", "Positive controlled incremental recovery"]
]

investment_table = Table(
    investment_data,
    colWidths=[70 * mm, 90 * mm]
)

investment_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
]))

story.append(investment_table)
story.append(Spacer(1, 6))

story.append(Paragraph(
    "The investment should be deployed through a treatment group and "
    "predefined holdout group. Recovery attribution, eligible balance, "
    "portfolio mix, DPD, risk, campaign, channel, agent, and timing should "
    "be measured consistently before any scale-up decision.",
    body
))

story.append(Paragraph("6. Key Risks", heading))

risks = [
    "Historical eligible-balance denominators are unavailable.",
    "Boundary months may represent incomplete operational periods.",
    "Treatment and comparison groups are observational rather than randomized.",
    "Portfolio and contact-selection effects may explain observed differences.",
    "Payment attribution requires an explicit attribution window for causal claims.",
    "Observed driver differences do not independently validate the 11% claim."
]

for risk in risks:
    story.append(Paragraph("• " + risk, body))

story.append(Paragraph("7. Final Recommendation", heading))

story.append(Paragraph(
    "<b>Do not present the 11% improvement as a proven causal result.</b> "
    "Treat it as an unverified reported claim. Approve a controlled pilot "
    "for collections and contactability optimization, with predefined "
    "treatment, holdout, attribution, recovery, and break-even criteria. "
    "Scale only when measured incremental recovery exceeds the required "
    "investment threshold.",
    decision
))

story.append(Spacer(1, 8))

story.append(Paragraph(
    "Evidence base: validated Clean/Golden analytical layer, monthly "
    "performance analysis, forensic analysis, driver analysis, statistical "
    "investigation, counterfactual analysis, and investment analysis.",
    small
))

doc.build(story)

print("Executive memo created")
print(f"Output: {OUTPUT}")