---
name: discord-pdf-workflow
description: Create, edit, improve, review, extract, revise, and post PDFs from Discord bot tasks. Use for any Discord fleet agent asked to make a PDF, update an existing PDF/SOW/MSA/proposal/report, improve formatting/content, convert markdown/text to PDF, revise from feedback, or avoid accidentally sending canned ideas PDFs.
---

# Discord PDF Workflow

Use this skill for Discord bot PDF work: creating a new PDF, editing a PDF, improving an existing draft, revising a SOW/MSA/proposal/report from feedback, or turning bot output into a Discord-ready PDF.

## Core rule

Do not substitute a canned ideas PDF for document-review or document-revision tasks. If the request mentions SOW, MSA, contract, proposal, invoice, report, review, feedback, update, revise, improve, or attached/current PDF, treat it as a document task.

## Workflow

1. Identify the job type:
   - Create: user wants a new PDF from text/markdown/outline.
   - Improve: user wants better wording, structure, formatting, completeness, or role-specific feedback.
   - Edit: user wants specific changes to an existing PDF.
   - Review + revise: user wants findings plus an updated version.
2. Gather source material:
   - Use attached PDF text/context if provided by the runtime.
   - If a local file path is provided, extract text with `pymupdf`/`fitz` if available or ask for text if extraction fails.
   - If prior channel context is needed, use recent task/channel context; do not claim no document/task exists without checking context.
3. Draft the revised source in markdown first. Keep a `.md` source next to the generated PDF whenever possible.
4. Generate the PDF with `scripts/markdown_to_pdf.py`.
5. Verify before claiming success:
   - file exists
   - size is nonzero
   - starts with `%PDF`
   - has a `%%EOF` marker
6. In Discord, post a concise status and attach/post the PDF in the requesting or assigned private channel.

## Editing decision tree

- If the original source `.md`/`.txt` exists: edit the source, regenerate the PDF, and verify.
- If only a PDF exists and the edit is a small text typo/title/date/client-name change: use `nano-pdf edit <file.pdf> <page> "instruction"` if available, then verify visually/structurally.
- If only a PDF exists and the requested changes are substantive: extract the text, rebuild a clean markdown source, then generate a replacement PDF. State that it is a revised replacement, not a pixel-perfect in-place edit.
- If the PDF is scanned/image-only and extraction fails: ask for source text or use OCR/marker-pdf only if available and appropriate.

## Helper script

Use the bundled script:

```bash
python scripts/markdown_to_pdf.py input.md output.pdf --title "Document Title"
```

The script uses ReportLab and is designed for the Discord fleet environment. It supports headings, bullets, simple numbered lists, paragraphs, and basic bold marker cleanup.

## Recommended Discord response

Keep responses short and clear:

```text
## PDF Update Complete
Status: Complete
Prepared by: <bot>
Source: <provided PDF / notes / feedback>

Summary:
- Created/revised the PDF based on the requested changes.
- Verified PDF structure before posting.

Open items:
- <anything the user still needs to fill in>

Recommended Next Step:
Review the attached PDF and tell me any exact wording changes.
```

## Pitfalls

- Do not say a PDF was created or posted unless the file was generated and verified.
- Do not expose local secrets, tokens, API keys, or hidden paths in the PDF.
- Avoid raw diffs in Discord unless requested. Summarize changes instead.
- For legal/security/financial documents, label work as internal draft/review unless the user says it is final.
- Use role expertise: Harvey flags legal issues, Achilles flags security controls, EPSN tightens operations/SOW scope, Hellen checks accounting/billing, Jenko checks finance/pricing, etc.
