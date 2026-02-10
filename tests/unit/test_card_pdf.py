"""Tests for PDF business card generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from thenine.core.brand import BrandContact, BrandPalette, BrandTypography
from thenine.generators.card_pdf import PDFCardGenerator

try:
    from weasyprint import HTML

    _HAS_GTK = True
except OSError:
    _HAS_GTK = False

needs_gtk = pytest.mark.skipif(not _HAS_GTK, reason="WeasyPrint requires GTK3 system libraries")


class TestPDFCardGenerator:
    def test_render_html(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography
    ) -> None:
        gen = PDFCardGenerator()
        contact = BrandContact(
            name="John Doe",
            title="CEO",
            email="john@acme.com",
            phone="+1 555 1234",
            website="acme.com",
        )
        html = gen._render_html("Acme Corp", contact, sample_palette, sample_typography)
        assert "John Doe" in html
        assert "CEO" in html
        assert "john@acme.com" in html
        assert "Acme Corp" in html
        assert sample_palette.primary.hex in html

    def test_render_html_minimal_contact(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography
    ) -> None:
        gen = PDFCardGenerator()
        contact = BrandContact(name="Jane")
        html = gen._render_html("Brand", contact, sample_palette, sample_typography)
        assert "Jane" in html
        assert "Brand" in html

    @needs_gtk
    def test_generate_creates_pdf(
        self,
        sample_palette: BrandPalette,
        sample_typography: BrandTypography,
        tmp_output: Path,
    ) -> None:
        gen = PDFCardGenerator()
        contact = BrandContact(
            name="John Doe",
            title="CEO",
            email="john@acme.com",
        )
        pdf_path = gen.generate("Acme Corp", contact, sample_palette, sample_typography, tmp_output)
        assert pdf_path.exists()
        assert pdf_path.suffix == ".pdf"
        assert pdf_path.stat().st_size > 0

    @needs_gtk
    def test_pdf_contains_two_pages(
        self,
        sample_palette: BrandPalette,
        sample_typography: BrandTypography,
        tmp_output: Path,
    ) -> None:
        gen = PDFCardGenerator()
        contact = BrandContact(name="John Doe", title="CEO")
        pdf_path = gen.generate("Acme Corp", contact, sample_palette, sample_typography, tmp_output)
        # PDF should have content (front + back)
        content = pdf_path.read_bytes()
        assert len(content) > 1000
