"""Shared pytest fixtures for edicao_pdf tests."""

from __future__ import annotations

import io
import struct
import zlib
from pathlib import Path

import pytest
import fitz  # PyMuPDF


def _make_pdf(text: str = "Test page") -> bytes:
    """Return a minimal one-page PDF with *text* as body content."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def _make_png(width: int = 10, height: int = 10) -> bytes:
    """Return a tiny valid PNG image (solid grey)."""
    raw = b"\x00" + bytes([128] * width * 3) * height
    compressed = zlib.compress(raw)
    def chunk(tag: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return length + tag + data + crc
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )
    return png


@pytest.fixture
def pdf_bytes() -> bytes:
    return _make_pdf()


@pytest.fixture
def two_pdfs(tmp_path: Path) -> tuple[Path, Path]:
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    a.write_bytes(_make_pdf("Page A"))
    b.write_bytes(_make_pdf("Page B"))
    return a, b


@pytest.fixture
def three_page_pdf(tmp_path: Path) -> Path:
    doc = fitz.open()
    for i in range(1, 4):
        p = doc.new_page()
        p.insert_text((72, 72), f"Page {i}")
    path = tmp_path / "three_pages.pdf"
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture
def png_bytes() -> bytes:
    return _make_png()
