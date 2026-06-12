"""Tests for edicao_pdf.zip_to_pdf."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from pypdf import PdfReader

from edicao_pdf.zip_to_pdf import zip_to_pdf
from tests.conftest import _make_pdf, _make_png


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_zip(tmp_path: Path, members: dict[str, bytes]) -> Path:
    """Write a ZIP file with the given {name: data} members."""
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return zip_path


# ---------------------------------------------------------------------------
# Basic success cases
# ---------------------------------------------------------------------------

def test_zip_with_pdfs(tmp_path):
    """ZIPs containing PDFs should be merged into one output PDF."""
    members = {
        "a.pdf": _make_pdf("Page A"),
        "b.pdf": _make_pdf("Page B"),
    }
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out)
    assert result.exists()
    assert len(PdfReader(str(result)).pages) == 2


def test_zip_with_png_image(tmp_path, png_bytes):
    """ZIPs containing PNG images should produce a PDF with one page each."""
    members = {"photo.png": png_bytes}
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out)
    assert result.exists()
    assert len(PdfReader(str(result)).pages) == 1


def test_zip_with_text_file(tmp_path):
    """ZIPs containing .txt files should produce a PDF page per file."""
    members = {"readme.txt": "Hello, PDF world!".encode("utf-8")}
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out)
    assert result.exists()
    assert len(PdfReader(str(result)).pages) == 1


def test_zip_mixed_content(tmp_path, png_bytes):
    """Mixed PDF, image and text files are all included."""
    members = {
        "doc.pdf": _make_pdf("From PDF"),
        "image.png": png_bytes,
        "notes.txt": "Some notes".encode("utf-8"),
    }
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out)
    assert len(PdfReader(str(result)).pages) == 3


def test_zip_unsupported_files_are_skipped(tmp_path):
    """Unsupported file types are silently ignored."""
    members = {
        "data.csv": b"col1,col2\n1,2",
        "script.py": b"print('hi')",
        "page.pdf": _make_pdf("Kept"),
    }
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out)
    # Only the PDF contributes a page.
    assert len(PdfReader(str(result)).pages) == 1


def test_zip_sort_names_alphabetical(tmp_path):
    """Files are processed in alphabetical order by default."""
    members = {
        "c.pdf": _make_pdf("Page C"),
        "a.pdf": _make_pdf("Page A"),
        "b.pdf": _make_pdf("Page B"),
    }
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out, sort_names=True)
    import fitz
    doc = fitz.open(str(result))
    texts = [doc[i].get_text().strip() for i in range(len(doc))]
    doc.close()
    assert texts == ["Page A", "Page B", "Page C"]


def test_zip_no_sort_preserves_order(tmp_path):
    """With sort_names=False the internal ZIP order is preserved."""
    # zipfile.ZipFile preserves insertion order when reading
    members_ordered = [
        ("z.pdf", _make_pdf("Page Z")),
        ("a.pdf", _make_pdf("Page A")),
    ]
    zip_path = tmp_path / "ordered.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, data in members_ordered:
            zf.writestr(name, data)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out, sort_names=False)
    import fitz
    doc = fitz.open(str(result))
    texts = [doc[i].get_text().strip() for i in range(len(doc))]
    doc.close()
    assert texts == ["Page Z", "Page A"]


def test_zip_creates_output_dir(tmp_path):
    """Output directory is created automatically if it does not exist."""
    members = {"a.pdf": _make_pdf("Page A")}
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "sub" / "deep" / "result.pdf"
    result = zip_to_pdf(zip_path, out)
    assert result.exists()


def test_zip_returns_resolved_path(tmp_path):
    members = {"a.pdf": _make_pdf("Page A")}
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out)
    assert result == out.resolve()


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_zip_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        zip_to_pdf(tmp_path / "ghost.zip", tmp_path / "out.pdf")


def test_zip_no_convertible_files_raises(tmp_path):
    members = {"data.csv": b"col1,col2\n1,2"}
    zip_path = _make_zip(tmp_path, members)
    with pytest.raises(ValueError, match="no convertible files"):
        zip_to_pdf(zip_path, tmp_path / "out.pdf")


def test_zip_invalid_zip_raises(tmp_path):
    bad_zip = tmp_path / "bad.zip"
    bad_zip.write_bytes(b"this is not a zip file")
    with pytest.raises(zipfile.BadZipFile):
        zip_to_pdf(bad_zip, tmp_path / "out.pdf")


def test_zip_custom_text_encoding(tmp_path):
    """Text files with non-UTF-8 encoding are decoded with the given codec."""
    text = "Olá mundo"
    members = {"latin.txt": text.encode("latin-1")}
    zip_path = _make_zip(tmp_path, members)
    out = tmp_path / "result.pdf"
    result = zip_to_pdf(zip_path, out, encoding="latin-1")
    assert result.exists()
