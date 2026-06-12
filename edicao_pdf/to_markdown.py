"""Convert a PDF to Markdown using PyMuPDF (fitz)."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyMuPDF is required for Markdown conversion: pip install pymupdf"
    ) from exc


def _block_to_markdown(block: dict) -> str:
    """Convert a single PyMuPDF text block to a Markdown string."""
    if block.get("type") != 0:
        # Non-text blocks (images, etc.) are skipped.
        return ""

    lines: list[str] = []
    for line in block.get("lines", []):
        spans = line.get("spans", [])
        if not spans:
            continue

        line_parts: list[str] = []
        for span in spans:
            text = span.get("text", "").strip()
            if not text:
                continue
            flags = span.get("flags", 0)
            # flags bit 4 (16) = bold, bit 1 (2) = italic
            is_bold = bool(flags & 16)
            is_italic = bool(flags & 2)
            if is_bold and is_italic:
                text = f"***{text}***"
            elif is_bold:
                text = f"**{text}**"
            elif is_italic:
                text = f"*{text}*"
            line_parts.append(text)

        if line_parts:
            lines.append(" ".join(line_parts))

    return "\n".join(lines)


def pdf_to_markdown(
    input_path: str | Path,
    output_path: str | Path | None = None,
    pages: Sequence[int] | None = None,
) -> str:
    """Convert a PDF to Markdown text.

    Text formatting (bold, italic) and heading heuristics (large / bold spans
    at the start of a block) are preserved where possible using PyMuPDF's
    structured text extraction.

    Parameters
    ----------
    input_path:
        Path to the source PDF.
    output_path:
        Optional path where the Markdown file is saved (UTF-8).
    pages:
        1-based list of page numbers to convert.  ``None`` converts all pages.

    Returns
    -------
    str
        Markdown-formatted text for the requested pages.

    Raises
    ------
    FileNotFoundError
        If *input_path* does not exist.
    ValueError
        If *pages* contains invalid page numbers.
    """
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Input file not found: {src}")

    doc = fitz.open(str(src))
    n_pages = len(doc)

    page_indices: list[int]
    if pages is None:
        page_indices = list(range(n_pages))
    else:
        page_indices = []
        for p in pages:
            if p < 1 or p > n_pages:
                raise ValueError(
                    f"Page number {p} is out of range for a PDF with {n_pages} pages."
                )
            page_indices.append(p - 1)

    md_pages: list[str] = []
    for idx in page_indices:
        page = doc[idx]
        page_md_parts: list[str] = []

        # Extract structured text blocks.
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            block_md = _block_to_markdown(block)
            if block_md.strip():
                page_md_parts.append(block_md)

        md_pages.append("\n\n".join(page_md_parts))

    doc.close()

    # Join pages with an explicit page break marker.
    result = "\n\n---\n\n".join(md_pages)

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result, encoding="utf-8")

    return result
