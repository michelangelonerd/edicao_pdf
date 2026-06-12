"""Tests for edicao_pdf.merge."""

from pathlib import Path

import pytest
from pypdf import PdfReader

from edicao_pdf.merge import merge_pdfs


def test_merge_two_pdfs(two_pdfs, tmp_path):
    a, b = two_pdfs
    out = tmp_path / "merged.pdf"
    result = merge_pdfs([a, b], out)
    assert result.exists()
    reader = PdfReader(str(result))
    assert len(reader.pages) == 2


def test_merge_returns_resolved_path(two_pdfs, tmp_path):
    a, b = two_pdfs
    out = tmp_path / "merged.pdf"
    result = merge_pdfs([a, b], out)
    assert result == out.resolve()


def test_merge_requires_at_least_two(tmp_path, two_pdfs):
    a, _ = two_pdfs
    with pytest.raises(ValueError, match="least two"):
        merge_pdfs([a], tmp_path / "out.pdf")


def test_merge_missing_file_raises(tmp_path, two_pdfs):
    a, _ = two_pdfs
    with pytest.raises(FileNotFoundError):
        merge_pdfs([a, tmp_path / "ghost.pdf"], tmp_path / "out.pdf")


def test_merge_creates_output_dir(two_pdfs, tmp_path):
    a, b = two_pdfs
    out = tmp_path / "sub" / "deep" / "merged.pdf"
    merge_pdfs([a, b], out)
    assert out.exists()
