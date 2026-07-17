"""
VaaniSetu — Export Service
Generates PDF (fpdf2) and DOCX (python-docx) export files.
"""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("vaanisetu.export")


# ---------------------------------------------------------------------------
# Impact Ledger → PDF
# ---------------------------------------------------------------------------
def export_impact_pdf(summary: dict, output_path: str) -> str:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_fill_color(27, 67, 50)   # --green-dark
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(10, 8)
    pdf.cell(0, 12, "VaaniSetu — Impact Ledger Report", ln=True)

    pdf.set_text_color(180, 210, 180)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(10, 20)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", ln=True)

    pdf.set_xy(10, 38)
    pdf.set_text_color(30, 30, 30)

    # Summary tiles
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)

    metrics = [
        ("Total Hours Translated",   f"{summary['total_hours']:,.1f} hrs"),
        ("Cost Saved (₹)",           f"₹ {summary['total_cost_saved']:,.0f}"),
        ("Farmers Reachable",        f"{int(summary['total_farmers_reachable']):,}"),
        ("Completed Jobs",           str(summary['job_count'])),
    ]
    for label, val in metrics:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(90, 7, label + ":", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, val, ln=True)

    # Language breakdown table
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Language Breakdown", ln=True)
    pdf.ln(2)

    # Table header
    col_w = [50, 25, 35, 35, 40]
    headers = ["Language", "Jobs", "Hours", "₹ Saved", "Farmers"]
    pdf.set_fill_color(82, 183, 136)   # --green-accent
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, h, border=1, fill=True)
    pdf.ln()

    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 10)
    fill = False
    for row in summary.get("language_breakdown", []):
        if fill:
            pdf.set_fill_color(235, 250, 241)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_w[0], 6, row["language"],              border=1, fill=True)
        pdf.cell(col_w[1], 6, str(row["job_count"]),         border=1, fill=True)
        pdf.cell(col_w[2], 6, f"{row['total_minutes']/60:.1f}", border=1, fill=True)
        pdf.cell(col_w[3], 6, f"₹{row['cost_saved']:,.0f}", border=1, fill=True)
        pdf.cell(col_w[4], 6, f"{int(row['farmers_reachable']):,}", border=1, fill=True)
        pdf.ln()
        fill = not fill

    pdf.output(output_path)
    return output_path


# ---------------------------------------------------------------------------
# Glossary → DOCX
# ---------------------------------------------------------------------------
def export_glossary_docx(terms: list[dict], output_path: str) -> str:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Title
    title = doc.add_heading("VaaniSetu — Translation Glossary", level=1)
    title.runs[0].font.color.rgb = RGBColor(27, 67, 50)

    doc.add_paragraph(
        f"Exported on {datetime.now().strftime('%d %b %Y, %H:%M')} · "
        f"{len(terms)} terms (used ≥ 3×, confidence ≥ 0.85)"
    )

    if not terms:
        doc.add_paragraph("No glossary terms yet.")
        doc.save(output_path)
        return output_path

    # Collect all target languages
    all_langs: set[str] = set()
    for t in terms:
        all_langs.update(t["translations"].keys())
    lang_cols = sorted(all_langs)

    # Table
    headers = ["Source Term", "Source Lang", "Times Used"] + lang_cols
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(27, 67, 50)

    for term in terms:
        row = table.add_row().cells
        row[0].text = term["source_text"]
        row[1].text = term["source_lang"]
        row[2].text = str(term["times_used"])
        for j, lang in enumerate(lang_cols):
            row[3 + j].text = term["translations"].get(lang, "")

    doc.save(output_path)
    return output_path
