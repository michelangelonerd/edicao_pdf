"""OCR a PDF using Tesseract (via pytesseract + pdf2image)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "OCR dependencies are required: pip install pytesseract pdf2image Pillow"
    ) from exc


def ocr_pdf(
    input_path: str | Path,
    output_path: str | Path | None = None,
    lang: str = "por+eng",
    pages: Sequence[int] | None = None,
    dpi: int = 300,
    tesseract_cmd: str | None = None,
) -> str:
    """Run OCR on a PDF using Tesseract and return the extracted text.

    Each page is converted to an image at *dpi* resolution and then passed to
    Tesseract.  The full text is returned as a single string with page breaks
    delimited by ``\\f`` (form-feed), matching Tesseract's native behaviour.

    Optionally the text is also saved to *output_path* when provided.

    Parameters
    ----------
    input_path:
        Path to the source PDF.
    output_path:
        Optional path where the plain-text result is saved (UTF-8).
    lang:
        Tesseract language string (e.g. ``"por"`` for Portuguese,
        ``"por+eng"`` for mixed).  Requires the corresponding language data
        installed on the system.
    pages:
        1-based list of page numbers to process.  ``None`` processes all pages.
    dpi:
        Resolution used when rasterising PDF pages.  Higher values improve
        accuracy at the cost of speed.
    tesseract_cmd:
        Full path to the ``tesseract`` binary.  Useful on Windows or when the
        binary is not on ``PATH``.  Ignored when ``None``.

    Returns
    -------
    str
        The OCR text for all requested pages joined by form-feed characters.

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

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    first_page: int | None = None
    last_page: int | None = None
    if pages:
        first_page = min(pages)
        last_page = max(pages)

    images: list[Image.Image] = convert_from_path(
        str(src),
        dpi=dpi,
        first_page=first_page,
        last_page=last_page,
    )

    # convert_from_path returns pages in the first_page..last_page window;
    # filter down to exactly the requested set when pages is not contiguous.
    if pages:
        window_start = first_page  # 1-based index of images[0]
        selected: list[Image.Image] = []
        for p in sorted(set(pages)):
            if p < first_page or p > last_page:  # type: ignore[operator]
                raise ValueError(f"Page {p} is out of range.")
            selected.append(images[p - window_start])  # type: ignore[operator]
        images = selected

    page_texts = [
        pytesseract.image_to_string(img, lang=lang) for img in images
    ]
    full_text = "\f".join(page_texts)

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(full_text, encoding="utf-8")

    return full_text
