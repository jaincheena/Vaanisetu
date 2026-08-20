"""
VaaniSetu — Export Service
Generates PDF (fpdf2) and DOCX (python-docx) export files.
"""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("vaanisetu.export")



# ---------------------------------------------------------------------------
# PDF text safety
# ---------------------------------------------------------------------------
# fpdf2's built-in Helvetica is latin-1 only. The report is full of characters
# that are not — the rupee sign, the em dash in the title, "≥" in the glossary
# footer — and each one raises FPDFUnicodeEncodingException rather than
# degrading, so the Impact Ledger's "Export Formal PDF Report" button failed
# 100% of the time. Register a real Unicode face when the machine has one and
# transliterate when it does not; a report that says "Rs." beats no report.
_UNICODE_FONT_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "assets" / "DejaVuSans.ttf",
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
]

_LATIN1_SUBSTITUTIONS = {
    "₹": "Rs.",   # ₹
    "—": "-",     # em dash
    "–": "-",     # en dash
    "≥": ">=",    # ≥
    "≤": "<=",    # ≤
    "·": "-",     # ·
    "‘": "'", "’": "'",
    "“": '"', "”": '"',
    "…": "...",
    "×": "x",
}


def _register_unicode_font(pdf) -> bool:
    """Attach a Unicode TTF to `pdf`, returning whether one was found."""
    for candidate in _UNICODE_FONT_CANDIDATES:
        try:
            if candidate.exists():
                pdf.add_font("VaaniUnicode", "", str(candidate))
                pdf.add_font("VaaniUnicode", "B", str(candidate))
                return True
        except Exception as e:
            logger.debug(f"Could not load PDF font {candidate}: {e}")
    logger.info("No Unicode font available — PDF export will transliterate symbols")
    return False


def _pdf_safe(text: str, unicode_ok: bool) -> str:
    """Make `text` renderable by the active font."""
    if unicode_ok:
        return text
    for src, dst in _LATIN1_SUBSTITUTIONS.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "replace").decode("latin-1")

# ---------------------------------------------------------------------------
# Impact Ledger → PDF
# ---------------------------------------------------------------------------
def export_impact_pdf(summary: dict, output_path: str) -> str:
    from fpdf import FPDF

    pdf = FPDF()
    unicode_ok = _register_unicode_font(pdf)
    family = "VaaniUnicode" if unicode_ok else "Helvetica"
    txt = lambda t: _pdf_safe(str(t), unicode_ok)

    pdf.add_page()

    # Header
    pdf.set_fill_color(27, 67, 50)   # --green-dark
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(family, "B", 18)
    pdf.set_xy(10, 8)
    pdf.cell(0, 12, txt("VaaniSetu — Impact Ledger Report"), ln=True)

    pdf.set_text_color(180, 210, 180)
    pdf.set_font(family, "", 10)
    pdf.set_xy(10, 20)
    pdf.cell(0, 6, txt(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}"), ln=True)

    pdf.set_xy(10, 38)
    pdf.set_text_color(30, 30, 30)

    # Summary tiles
    pdf.set_font(family, "B", 14)
    pdf.cell(0, 8, txt("Summary"), ln=True)
    pdf.set_font(family, "", 11)
    pdf.ln(2)

    metrics = [
        ("Advisory Hours Localized", f"{summary['total_hours']:,.1f} hrs"),
        ("Cost Saved vs Agency",     f"₹ {summary['total_cost_saved']:,.0f}"),
        ("Farmers Reachable",        f"{int(summary['total_farmers_reachable']):,}"),
        ("Completed Jobs",           str(summary['job_count'])),
    ]
    for label, val in metrics:
        pdf.set_font(family, "B", 11)
        pdf.cell(90, 7, txt(label + ":"), ln=False)
        pdf.set_font(family, "", 11)
        pdf.cell(0, 7, txt(val), ln=True)

    # Language breakdown table
    pdf.ln(6)
    pdf.set_font(family, "B", 13)
    pdf.cell(0, 8, txt("Language Breakdown"), ln=True)
    pdf.ln(2)

    # Table header
    col_w = [50, 25, 35, 35, 40]
    headers = ["Language", "Jobs", "Hours", "₹ Saved", "Farmers"]
    pdf.set_fill_color(82, 183, 136)   # --green-accent
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(family, "B", 10)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, txt(h), border=1, fill=True)
    pdf.ln()

    pdf.set_text_color(30, 30, 30)
    pdf.set_font(family, "", 10)
    fill = False
    for row in summary.get("language_breakdown", []):
        if fill:
            pdf.set_fill_color(235, 250, 241)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_w[0], 6, txt(row["language"]),                    border=1, fill=True)
        pdf.cell(col_w[1], 6, txt(row["job_count"]),                   border=1, fill=True)
        pdf.cell(col_w[2], 6, txt(f"{row['total_minutes']/60:.1f}"),   border=1, fill=True)
        pdf.cell(col_w[3], 6, txt(f"₹{row['cost_saved']:,.0f}"),  border=1, fill=True)
        pdf.cell(col_w[4], 6, txt(f"{int(row['farmers_reachable']):,}"), border=1, fill=True)
        pdf.ln()
        fill = not fill

    # Method note. These numbers go to donors and auditors; the assumptions
    # behind them belong on the same page as the figures.
    pdf.ln(6)
    pdf.set_font(family, "B", 11)
    pdf.cell(0, 7, txt("How these figures are calculated"), ln=True)
    pdf.set_font(family, "", 9)
    unmeasured = summary.get("unmeasured_job_count", 0)
    notes = [
        "Hours are the runtime of the source advisories, counted once per job "
        "regardless of how many languages it was localized into.",
        "Cost saved is advisory minutes x the configured agency rate, per target "
        "language, using the rates in Regional Rate Configuration.",
        "Farmers Reachable is a capacity estimate at the configured farmers-per-hour "
        "rate. VaaniSetu produces the files; it does not deliver them, so this is "
        "potential reach and not a count of farmers served.",
    ]
    if unmeasured:
        notes.append(
            f"{unmeasured} completed job(s) predate duration tracking and are "
            "excluded from every figure above."
        )
    for note in notes:
        pdf.multi_cell(0, 5, txt("- " + note))
        pdf.ln(1)

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
