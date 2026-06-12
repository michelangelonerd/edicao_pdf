"""Split a PDF into individual pages or page ranges."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from pypdf import PdfReader, PdfWriter


def split_pdf(
    input_path: str | Path,
    output_dir: str | Path,
    page_ranges: Sequence[tuple[int, int]] | None = None,
) -> list[Path]:
    """Split a PDF into separate files.

    When *page_ranges* is ``None`` each page is saved as its own file.
    Otherwise each ``(start, end)`` tuple (1-based, inclusive) produces one
    output file.

    Parameters
    ----------
    input_path:
        Path to the source PDF.
    output_dir:
        Directory where the output files are written.  Created if absent.
    page_ranges:
        Optional list of ``(start, end)`` page ranges (1-based, inclusive).
        ``None`` means one file per page.

    Returns
    -------
    list[Path]
        Paths of the generated PDF files in order.

    Raises
    ------
    FileNotFoundError
        If *input_path* does not exist.
    ValueError
        If a page range is out of bounds or malformed.
    """
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Input file not found: {src}")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(src))
    n_pages = len(reader.pages)
    stem = src.stem

    output_files: list[Path] = []

    if page_ranges is None:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            out_path = out_dir / f"{stem}_page_{i + 1:04d}.pdf"
            with open(out_path, "wb") as fh:
                writer.write(fh)
            output_files.append(out_path.resolve())
    else:
        for idx, (start, end) in enumerate(page_ranges):
            if start < 1 or end > n_pages or start > end:
                raise ValueError(
                    f"Invalid page range ({start}, {end}) for a PDF with {n_pages} pages."
                )
            writer = PdfWriter()
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])
            out_path = out_dir / f"{stem}_range_{idx + 1:04d}_p{start}-p{end}.pdf"
            with open(out_path, "wb") as fh:
                writer.write(fh)
            output_files.append(out_path.resolve())

    return output_files
