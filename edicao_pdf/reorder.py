"""Reorder (or sort) pages inside a PDF."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from pypdf import PdfReader, PdfWriter


def reorder_pages(
    input_path: str | Path,
    output_path: str | Path,
    order: Sequence[int],
) -> Path:
    """Produce a new PDF with pages in the given order.

    Parameters
    ----------
    input_path:
        Path to the source PDF.
    output_path:
        Destination path for the reordered PDF.
    order:
        1-based page numbers in the desired output order.  Pages may be
        repeated or omitted.  Example: ``[3, 1, 2]`` puts page 3 first.

    Returns
    -------
    Path
        The resolved path of the output file.

    Raises
    ------
    FileNotFoundError
        If *input_path* does not exist.
    ValueError
        If *order* contains invalid page numbers.
    """
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Input file not found: {src}")

    reader = PdfReader(str(src))
    n_pages = len(reader.pages)

    for page_num in order:
        if page_num < 1 or page_num > n_pages:
            raise ValueError(
                f"Page number {page_num} is out of range for a PDF with {n_pages} pages."
            )

    writer = PdfWriter()
    for page_num in order:
        writer.add_page(reader.pages[page_num - 1])

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as fh:
        writer.write(fh)

    return output.resolve()
