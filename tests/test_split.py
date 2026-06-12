"""Tests for edicao_pdf.split."""

import pytest
from pypdf import PdfReader

from edicao_pdf.split import split_pdf


def test_split_each_page(three_page_pdf, tmp_path):
    files = split_pdf(three_page_pdf, tmp_path / "out")
    assert len(files) == 3
    for f in files:
        assert f.exists()
        assert len(PdfReader(str(f)).pages) == 1


def test_split_with_ranges(three_page_pdf, tmp_path):
    files = split_pdf(three_page_pdf, tmp_path / "out", [(1, 2), (3, 3)])
    assert len(files) == 2
    assert len(PdfReader(str(files[0])).pages) == 2
    assert len(PdfReader(str(files[1])).pages) == 1


def test_split_invalid_range_raises(three_page_pdf, tmp_path):
    with pytest.raises(ValueError):
        split_pdf(three_page_pdf, tmp_path / "out", [(2, 5)])


def test_split_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        split_pdf(tmp_path / "ghost.pdf", tmp_path / "out")
