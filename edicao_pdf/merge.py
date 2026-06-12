"""Merge multiple PDF files into a single PDF."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pypdf import PdfWriter


def merge_pdfs(input_paths: Iterable[str | Path], output_path: str | Path) -> Path:
    """Merge multiple PDF files into one.

    Parameters
    ----------
    input_paths:
        Ordered sequence of paths to the PDF files to be merged.
    output_path:
        Destination path for the merged PDF.

    Returns
    -------
    Path
        The resolved path of the output file.

    Raises
    ------
    FileNotFoundError
        If any of the input files do not exist.
    ValueError
        If fewer than two input files are provided.
    """
    paths = [Path(p) for p in input_paths]
    if len(paths) < 2:
        raise ValueError("At least two PDF files are required for merging.")
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Input file not found: {p}")

    writer = PdfWriter()
    for p in paths:
        writer.append(str(p))

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as fh:
        writer.write(fh)

    return output.resolve()
