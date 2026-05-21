#!/usr/bin/env python3
"""Convert a simple Markdown/text file to a verified PDF for Discord bot deliverables.

Usage:
  python scripts/markdown_to_pdf.py input.md output.pdf --title "Title"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, PageBreak
    from reportlab.pdfbase.ttfonts import TTFont
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"Missing dependency: reportlab. Install in the Hermes venv with: uv pip install reportlab\n{exc}")


def clean_inline(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = text.replace("&", "&amp;").replace("<b>", "__BOLD_OPEN__").replace("</b>", "__BOLD_CLOSE__")
    text = text.replace("<font name='Courier'>", "__CODE_OPEN__").replace("</font>", "__CODE_CLOSE__")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("__BOLD_OPEN__", "<b>").replace("__BOLD_CLOSE__", "</b>")
    text = text.replace("__CODE_OPEN__", "<font name='Courier'>").replace("__CODE_CLOSE__", "</font>")
    return text


def build_pdf(markdown_path: Path, pdf_path: Path, title: str | None = None) -> None:
    raw = markdown_path.read_text(encoding="utf-8")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallBody", parent=styles["BodyText"], fontSize=9.5, leading=13, spaceAfter=6))
    styles.add(ParagraphStyle(name="BotTitle", parent=styles["Title"], fontSize=18, leading=22, spaceAfter=14, textColor=colors.HexColor("#1F2937")))
    styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontSize=15, leading=18, spaceBefore=10, spaceAfter=8, textColor=colors.HexColor("#111827")))
    styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontSize=12.5, leading=15, spaceBefore=8, spaceAfter=6, textColor=colors.HexColor("#374151")))
    styles.add(ParagraphStyle(name="BulletText", parent=styles["SmallBody"], leftIndent=0))

    story = []
    if title:
        story.append(Paragraph(clean_inline(title), styles["BotTitle"]))

    pending_bullets = []

    def flush_bullets():
        nonlocal pending_bullets
        if pending_bullets:
            story.append(ListFlowable([ListItem(Paragraph(clean_inline(x), styles["BulletText"])) for x in pending_bullets], bulletType="bullet", leftIndent=18))
            story.append(Spacer(1, 4))
            pending_bullets = []

    paragraph_lines = []

    def flush_para():
        nonlocal paragraph_lines
        if paragraph_lines:
            story.append(Paragraph(clean_inline(" ".join(paragraph_lines)), styles["SmallBody"]))
            paragraph_lines = []

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_para(); flush_bullets(); story.append(Spacer(1, 4)); continue
        if stripped == "---PAGE---":
            flush_para(); flush_bullets(); story.append(PageBreak()); continue
        if stripped.startswith("# "):
            flush_para(); flush_bullets(); story.append(Paragraph(clean_inline(stripped[2:]), styles["H1x"])); continue
        if stripped.startswith("## "):
            flush_para(); flush_bullets(); story.append(Paragraph(clean_inline(stripped[3:]), styles["H2x"])); continue
        if re.match(r"^[-*]\s+", stripped):
            flush_para(); pending_bullets.append(re.sub(r"^[-*]\s+", "", stripped)); continue
        if re.match(r"^\d+[.)]\s+", stripped):
            flush_para(); pending_bullets.append(re.sub(r"^\d+[.)]\s+", "", stripped)); continue
        paragraph_lines.append(stripped)

    flush_para(); flush_bullets()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=0.72*inch, leftMargin=0.72*inch, topMargin=0.65*inch, bottomMargin=0.65*inch, title=title or markdown_path.stem)
    doc.build(story)


def verify_pdf(pdf_path: Path) -> tuple[bool, str]:
    if not pdf_path.exists():
        return False, "missing output file"
    data = pdf_path.read_bytes()
    if len(data) < 100:
        return False, f"too small ({len(data)} bytes)"
    if not data.startswith(b"%PDF"):
        return False, "missing %PDF header"
    if b"%%EOF" not in data[-2048:]:
        return False, "missing EOF marker near end"
    return True, f"ok ({len(data)} bytes)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Markdown/text source")
    ap.add_argument("output", help="Output PDF path")
    ap.add_argument("--title", default=None)
    args = ap.parse_args()
    inp = Path(args.input).expanduser().resolve()
    out = Path(args.output).expanduser().resolve()
    if not inp.exists():
        print(f"Input not found: {inp}", file=sys.stderr)
        return 2
    build_pdf(inp, out, args.title)
    ok, detail = verify_pdf(out)
    print(f"PDF verification: {detail}")
    print(str(out))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
