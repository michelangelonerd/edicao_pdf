"""Tests for edicao_pdf.reorder."""

import pytest
from pypdf import PdfReader

from edicao_pdf.reorder import reorder_pages


def test_reorder_reverses_pages(three_page_pdf, tmp_path):
    out = tmp_path / "reordered.pdf"
    reorder_pages(three_page_pdf, out, [3, 2, 1])
    assert out.exists()
    assert len(PdfReader(str(out)).pages) == 3


def test_reorder_subset(three_page_pdf, tmp_path):
    out = tmp_path / "subset.pdf"
    reorder_pages(three_page_pdf, out, [2, 1])
    assert len(PdfReader(str(out)).pages) == 2


def test_reorder_duplicate_pages(three_page_pdf, tmp_path):
    out = tmp_path / "dup.pdf"
    reorder_pages(three_page_pdf, out, [1, 1, 1])
    assert len(PdfReader(str(out)).pages) == 3


def test_reorder_invalid_page_raises(three_page_pdf, tmp_path):
    with pytest.raises(ValueError):
        reorder_pages(three_page_pdf, tmp_path / "out.pdf", [1, 99])


def test_reorder_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        reorder_pages(tmp_path / "ghost.pdf", tmp_path / "out.pdf", [1])
