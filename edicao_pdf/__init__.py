"""edicao_pdf — PDF editing utilities.

Provides functions to merge, split, reorder pages, run OCR (via Tesseract),
convert PDFs to Markdown, and build a PDF from files inside a ZIP archive.
"""

from edicao_pdf.merge import merge_pdfs
from edicao_pdf.split import split_pdf
from edicao_pdf.reorder import reorder_pages
from edicao_pdf.ocr import ocr_pdf
from edicao_pdf.to_markdown import pdf_to_markdown
from edicao_pdf.zip_to_pdf import zip_to_pdf

__all__ = [
    "merge_pdfs",
    "split_pdf",
    "reorder_pages",
    "ocr_pdf",
    "pdf_to_markdown",
    "zip_to_pdf",
]
