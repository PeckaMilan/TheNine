"""Tests for typography selector."""

from __future__ import annotations

from thenine.core.brand import BrandTypography
from thenine.core.typography import TypographySelector, _google_fonts_url, _infer_category


class TestInferCategory:
    def test_serif(self) -> None:
        assert _infer_category("Playfair Display") == "serif"
        assert _infer_category("Merriweather") == "serif"

    def test_sans_serif(self) -> None:
        assert _infer_category("Inter") == "sans-serif"
        assert _infer_category("Roboto") == "sans-serif"

    def test_monospace(self) -> None:
        assert _infer_category("JetBrains Mono") == "monospace"
        assert _infer_category("Fira Code") == "monospace"


class TestGoogleFontsUrl:
    def test_simple_font(self) -> None:
        url = _google_fonts_url("Inter", 700)
        assert "Inter:wght@700" in url
        assert "display=swap" in url

    def test_multi_word_font(self) -> None:
        url = _google_fonts_url("Source Sans 3", 400)
        assert "Source+Sans+3" in url


class TestTypographySelector:
    def test_selects_typography(self) -> None:
        selector = TypographySelector()
        result = selector.select("technology", "modern", "TestProject")
        assert isinstance(result, BrandTypography)
        assert result.heading.family
        assert result.body.family
        assert result.mono.family == "JetBrains Mono"

    def test_heading_is_bold(self) -> None:
        selector = TypographySelector()
        result = selector.select("technology", "modern")
        assert result.heading.weight == 700

    def test_body_is_regular(self) -> None:
        selector = TypographySelector()
        result = selector.select("technology", "modern")
        assert result.body.weight == 400

    def test_different_industries(self) -> None:
        selector = TypographySelector()
        tech = selector.select("technology", "modern", "Test")
        finance = selector.select("finance", "classic", "Test")
        # Different industries should likely produce different fonts
        assert tech.heading.family != finance.heading.family or tech.body.family != finance.body.family

    def test_professional_prefers_serif(self) -> None:
        selector = TypographySelector()
        result = selector.select("finance", "professional", "Test")
        assert result.heading.category == "serif"

    def test_modern_prefers_sans(self) -> None:
        selector = TypographySelector()
        result = selector.select("technology", "modern", "Test")
        assert result.heading.category == "sans-serif"

    def test_google_fonts_urls_set(self) -> None:
        selector = TypographySelector()
        result = selector.select("technology", "modern", "Test")
        assert "fonts.googleapis.com" in result.heading.google_fonts_url
        assert "fonts.googleapis.com" in result.body.google_fonts_url

    def test_unknown_industry_falls_back(self) -> None:
        selector = TypographySelector()
        result = selector.select("unknown_industry", "modern", "Test")
        assert isinstance(result, BrandTypography)

    def test_deterministic_same_inputs(self) -> None:
        selector = TypographySelector()
        r1 = selector.select("technology", "modern", "SameName")
        r2 = selector.select("technology", "modern", "SameName")
        assert r1.heading.family == r2.heading.family
        assert r1.body.family == r2.body.family
