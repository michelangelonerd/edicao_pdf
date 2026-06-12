"""Tests for edicao_pdf.to_markdown."""

import pytest

from edicao_pdf.to_markdown import pdf_to_markdown


def test_to_markdown_returns_string(three_page_pdf):
    md = pdf_to_markdown(three_page_pdf)
    assert isinstance(md, str)
    assert len(md) > 0


def test_to_markdown_page_separator(three_page_pdf):
    md = pdf_to_markdown(three_page_pdf)
    # Three pages → two separators
    assert md.count("---") == 2


def test_to_markdown_specific_pages(three_page_pdf):
    md = pdf_to_markdown(three_page_pdf, pages=[1, 2])
    assert md.count("---") == 1


def test_to_markdown_saves_file(three_page_pdf, tmp_path):
    out = tmp_path / "output.md"
    pdf_to_markdown(three_page_pdf, output_path=out)
    assert out.exists()
    assert out.read_text(encoding="utf-8").count("---") == 2


def test_to_markdown_invalid_page_raises(three_page_pdf):
    with pytest.raises(ValueError):
        pdf_to_markdown(three_page_pdf, pages=[99])


def test_to_markdown_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        pdf_to_markdown(tmp_path / "ghost.pdf")
