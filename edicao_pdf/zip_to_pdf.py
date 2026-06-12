"""Convert and merge files from a ZIP archive into a single PDF.

Supported file types inside the archive:
- Existing PDFs              — included as-is.
- Images (JPEG, PNG, BMP,
  GIF, TIFF, WEBP)          — each image becomes one PDF page.
- Plain-text files (.txt)   — rendered as a simple text PDF page.

Files in unsupported formats are silently skipped.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path, PurePosixPath
from typing import Sequence

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyMuPDF is required: pip install pymupdf"
    ) from exc

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"}
_TEXT_SUFFIXES = {".txt"}
_PDF_SUFFIX = ".pdf"

# Point size of the font used when rendering plain-text pages.
_TEXT_FONT_SIZE = 11
_PAGE_WIDTH = 595   # A4 width  in pt
_PAGE_HEIGHT = 842  # A4 height in pt
_MARGIN = 40        # pt


def _image_bytes_to_pdf_bytes(data: bytes) -> bytes:
    """Return a single-page PDF containing *data* as an image."""
    img_doc = fitz.open(stream=data, filetype="image")
    pdf_bytes = img_doc.convert_to_pdf()
    img_doc.close()
    return pdf_bytes


def _text_to_pdf_bytes(text: str) -> bytes:
    """Return a PDF with *text* rendered as plain paragraphs."""
    doc = fitz.open()
    page = doc.new_page(width=_PAGE_WIDTH, height=_PAGE_HEIGHT)
    rect = fitz.Rect(_MARGIN, _MARGIN, _PAGE_WIDTH - _MARGIN, _PAGE_HEIGHT - _MARGIN)
    page.insert_textbox(
        rect,
        text,
        fontsize=_TEXT_FONT_SIZE,
        fontname="helv",
        color=(0, 0, 0),
    )
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def zip_to_pdf(
    zip_path: str | Path,
    output_path: str | Path,
    sort_names: bool = True,
    encoding: str = "utf-8",
) -> Path:
    """Extract files from a ZIP archive, convert them and merge into one PDF.

    Parameters
    ----------
    zip_path:
        Path to the source ``.zip`` file.
    output_path:
        Destination path for the merged PDF.
    sort_names:
        When ``True`` (default) files are processed in alphabetical order by
        their path inside the archive.  Set to ``False`` to preserve the
        archive's internal order.
    encoding:
        Encoding used to decode plain-text (``.txt``) files.

    Returns
    -------
    Path
        The resolved path of the output PDF.

    Raises
    ------
    FileNotFoundError
        If *zip_path* does not exist.
    ValueError
        If the archive contains no convertible files.
    zipfile.BadZipFile
        If *zip_path* is not a valid ZIP file.
    """
    src = Path(zip_path)
    if not src.exists():
        raise FileNotFoundError(f"ZIP file not found: {src}")

    merged = fitz.open()

    with zipfile.ZipFile(src, "r") as zf:
        names: list[str] = [
            n for n in zf.namelist() if not n.endswith("/")
        ]
        if sort_names:
            names = sorted(names, key=lambda n: n.lower())

        for name in names:
            suffix = PurePosixPath(name).suffix.lower()
            data = zf.read(name)

            if suffix == _PDF_SUFFIX:
                chunk = fitz.open(stream=data, filetype="pdf")
            elif suffix in _IMAGE_SUFFIXES:
                pdf_bytes = _image_bytes_to_pdf_bytes(data)
                chunk = fitz.open(stream=pdf_bytes, filetype="pdf")
            elif suffix in _TEXT_SUFFIXES:
                text = data.decode(encoding, errors="replace")
                pdf_bytes = _text_to_pdf_bytes(text)
                chunk = fitz.open(stream=pdf_bytes, filetype="pdf")
            else:
                # Unsupported format — skip silently.
                continue

            merged.insert_pdf(chunk)
            chunk.close()

    if len(merged) == 0:
        merged.close()
        raise ValueError(
            "The ZIP archive contains no convertible files "
            "(supported: PDF, images, .txt)."
        )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    merged.save(str(out))
    merged.close()

    return out.resolve()
