"""Tests for the CLI module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from thenine.cli import app
from thenine.core.brand import (
    BrandColor,
    BrandContact,
    BrandPalette,
    BrandTokens,
    BrandTypography,
    FontSpec,
)

runner = CliRunner()


def _make_palette() -> BrandPalette:
    return BrandPalette(
        primary=BrandColor(
            name="Blue", hex="#1a56db", oklch_l=0.45, oklch_c=0.18, oklch_h=260.0, purpose="primary"
        ),
        secondary=BrandColor(
            name="Slate", hex="#475569", oklch_l=0.45, oklch_c=0.03, oklch_h=250.0, purpose="secondary"
        ),
        accent=BrandColor(
            name="Amber", hex="#d97706", oklch_l=0.65, oklch_c=0.18, oklch_h=75.0, purpose="accent"
        ),
        neutral_light=BrandColor(
            name="Cloud", hex="#f8fafc", oklch_l=0.98, oklch_c=0.005, oklch_h=250.0, purpose="neutral-light"
        ),
        neutral_dark=BrandColor(
            name="Charcoal", hex="#1e293b", oklch_l=0.25, oklch_c=0.03, oklch_h=250.0, purpose="neutral-dark"
        ),
    )


def _make_typography() -> BrandTypography:
    return BrandTypography(
        heading=FontSpec(
            family="Inter", category="sans-serif", weight=700,
            google_fonts_url="https://fonts.googleapis.com/css2?family=Inter:wght@700",
        ),
        body=FontSpec(
            family="Source Sans 3", category="sans-serif", weight=400,
            google_fonts_url="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400",
        ),
    )


def _make_tokens(palette: BrandPalette, typography: BrandTypography) -> BrandTokens:
    return BrandTokens(
        colors={"primary": palette.primary.hex, "secondary": palette.secondary.hex},
        fonts={"heading": typography.heading.family, "body": typography.body.family},
    )


class TestPaletteCommand:
    @patch("thenine.core.palette.PaletteGenerator.generate")
    def test_palette_default(self, mock_generate) -> None:
        mock_generate.return_value = _make_palette()
        result = runner.invoke(app, ["palette", "--no-ai"])
        assert result.exit_code == 0
        assert "Brand Palette" in result.output

    @patch("thenine.core.palette.PaletteGenerator.generate")
    def test_palette_with_options(self, mock_generate) -> None:
        mock_generate.return_value = _make_palette()
        result = runner.invoke(app, [
            "palette", "--name", "Acme", "--industry", "finance",
            "--mood", "professional", "--no-ai",
        ])
        assert result.exit_code == 0
        mock_generate.assert_called_once_with("finance", "professional", "Acme", use_ai=False)


class TestGenerateCommand:
    @patch("thenine.generators.website.WebsiteGenerator.generate")
    @patch("thenine.generators.card_3d.ThreeDCardGenerator.generate")
    @patch("thenine.generators.card_pdf.PDFCardGenerator.generate")
    @patch("thenine.core.tokens.export_all")
    @patch("thenine.core.tokens.create_tokens")
    @patch("thenine.core.typography.TypographySelector.select")
    @patch("thenine.core.palette.PaletteGenerator.generate")
    def test_generate_full_pipeline(
        self, mock_pal_gen, mock_typo_sel, mock_create_tok, mock_export,
        mock_pdf_gen, mock_3d_gen, mock_web_gen, tmp_path: Path,
    ) -> None:
        palette = _make_palette()
        typography = _make_typography()
        tokens = _make_tokens(palette, typography)

        mock_pal_gen.return_value = palette
        mock_typo_sel.return_value = typography
        mock_create_tok.return_value = tokens
        json_path = tmp_path / "tokens.json"
        css_path = tmp_path / "tokens.css"
        tw_path = tmp_path / "tailwind-theme.css"
        mock_export.return_value = {"json": json_path, "css": css_path, "tailwind": tw_path}
        mock_pdf_gen.return_value = tmp_path / "card.pdf"
        stl_mock = tmp_path / "card.stl"
        mock_3d_gen.return_value = {"stl": stl_mock}
        mock_web_gen.return_value = tmp_path / "website"

        result = runner.invoke(app, [
            "generate",
            "--name", "TestCo",
            "--tagline", "Test tagline",
            "--industry", "technology",
            "--mood", "modern",
            "--no-ai",
            "--output", str(tmp_path / "out"),
        ])
        assert result.exit_code == 0
        assert "Generating Brand Identity" in result.output
        assert "Brand package generated!" in result.output

    @patch("thenine.generators.card_pdf.PDFCardGenerator.generate")
    @patch("thenine.core.tokens.export_all")
    @patch("thenine.core.tokens.create_tokens")
    @patch("thenine.core.typography.TypographySelector.select")
    @patch("thenine.core.palette.PaletteGenerator.generate")
    def test_generate_skip_website_and_3d(
        self, mock_pal_gen, mock_typo_sel, mock_create_tok, mock_export,
        mock_pdf_gen, tmp_path: Path,
    ) -> None:
        palette = _make_palette()
        typography = _make_typography()

        mock_pal_gen.return_value = palette
        mock_typo_sel.return_value = typography
        mock_create_tok.return_value = _make_tokens(palette, typography)
        json_path = tmp_path / "tokens.json"
        css_path = tmp_path / "tokens.css"
        tw_path = tmp_path / "tailwind-theme.css"
        mock_export.return_value = {"json": json_path, "css": css_path, "tailwind": tw_path}
        mock_pdf_gen.side_effect = OSError("cannot load library 'libgobject-2.0-0'")

        result = runner.invoke(app, [
            "generate",
            "--name", "TestCo",
            "--skip-website",
            "--skip-3d",
            "--no-ai",
            "--output", str(tmp_path / "out"),
        ])
        assert result.exit_code == 0
        assert "PDF Card skipped" in result.output

    @patch("thenine.generators.card_pdf.PDFCardGenerator.generate")
    @patch("thenine.core.tokens.export_all")
    @patch("thenine.core.tokens.create_tokens")
    @patch("thenine.core.typography.TypographySelector.select")
    @patch("thenine.core.palette.PaletteGenerator.generate")
    def test_generate_pdf_non_gtk_error_raises(
        self, mock_pal_gen, mock_typo_sel, mock_create_tok, mock_export,
        mock_pdf_gen, tmp_path: Path,
    ) -> None:
        palette = _make_palette()
        typography = _make_typography()

        mock_pal_gen.return_value = palette
        mock_typo_sel.return_value = typography
        mock_create_tok.return_value = _make_tokens(palette, typography)
        json_path = tmp_path / "tokens.json"
        css_path = tmp_path / "tokens.css"
        tw_path = tmp_path / "tailwind-theme.css"
        mock_export.return_value = {"json": json_path, "css": css_path, "tailwind": tw_path}
        mock_pdf_gen.side_effect = OSError("disk full")

        result = runner.invoke(app, [
            "generate",
            "--name", "TestCo",
            "--skip-website",
            "--skip-3d",
            "--no-ai",
            "--output", str(tmp_path / "out"),
        ])
        assert result.exit_code != 0


class TestCardCommand:
    @patch("thenine.generators.card_pdf.PDFCardGenerator.generate")
    @patch("thenine.core.typography.TypographySelector.select")
    @patch("thenine.core.palette.PaletteGenerator.generate")
    def test_card_command(self, mock_pal, mock_typo, mock_pdf, tmp_path: Path) -> None:
        palette = _make_palette()
        typography = _make_typography()
        mock_pal.return_value = palette
        mock_typo.return_value = typography
        mock_pdf.return_value = tmp_path / "card.pdf"

        result = runner.invoke(app, [
            "card",
            "--name", "TestCo",
            "--contact-name", "John",
            "--contact-email", "john@test.com",
            "--skip-3d",
            "--output", str(tmp_path),
        ])
        assert result.exit_code == 0
        assert "PDF" in result.output

    @patch("thenine.generators.card_3d.ThreeDCardGenerator.generate")
    @patch("thenine.generators.card_pdf.PDFCardGenerator.generate")
    @patch("thenine.core.typography.TypographySelector.select")
    @patch("thenine.core.palette.PaletteGenerator.generate")
    def test_card_with_3d(self, mock_pal, mock_typo, mock_pdf, mock_3d, tmp_path: Path) -> None:
        palette = _make_palette()
        typography = _make_typography()
        mock_pal.return_value = palette
        mock_typo.return_value = typography
        mock_pdf.return_value = tmp_path / "card.pdf"
        mock_3d.return_value = {"stl": MagicMock(name="card.stl"), "3mf": MagicMock(name="card.3mf")}

        result = runner.invoke(app, [
            "card", "--name", "TestCo", "--output", str(tmp_path),
        ])
        assert result.exit_code == 0
        assert "STL" in result.output or "PDF" in result.output

    @patch("thenine.generators.card_3d.ThreeDCardGenerator.generate")
    @patch("thenine.generators.card_pdf.PDFCardGenerator.generate")
    @patch("thenine.core.typography.TypographySelector.select")
    @patch("thenine.core.palette.PaletteGenerator.generate")
    def test_card_3d_error_handled(self, mock_pal, mock_typo, mock_pdf, mock_3d, tmp_path: Path) -> None:
        palette = _make_palette()
        typography = _make_typography()
        mock_pal.return_value = palette
        mock_typo.return_value = typography
        mock_pdf.return_value = tmp_path / "card.pdf"
        mock_3d.side_effect = RuntimeError("3D generation failed")

        result = runner.invoke(app, [
            "card", "--name", "TestCo", "--output", str(tmp_path),
        ])
        assert result.exit_code == 0
        assert "3D Card skipped" in result.output


class TestDNSCommand:
    @patch("thenine.infra.cloudflare_dns.DNSManager.list_records")
    @patch("thenine.infra.cloudflare_dns.DNSManager.get_zone_id")
    def test_dns_list(self, mock_zone, mock_records) -> None:
        mock_zone.return_value = "zone123"
        mock_records.return_value = [
            {"type": "A", "name": "example.com", "content": "1.2.3.4", "proxied": True},
        ]
        result = runner.invoke(app, [
            "dns", "--domain", "example.com", "--action", "list",
        ])
        assert result.exit_code == 0
        assert "zone123" in result.output

    @patch("thenine.infra.cloudflare_dns.DNSManager.setup_pages_dns")
    @patch("thenine.infra.cloudflare_dns.DNSManager.get_zone_id")
    def test_dns_setup_pages(self, mock_zone, mock_setup) -> None:
        mock_zone.return_value = "zone123"
        mock_setup.return_value = [
            {"type": "CNAME", "name": "example.com", "content": "example.pages.dev"},
            {"type": "CNAME", "name": "www.example.com", "content": "example.pages.dev"},
        ]
        result = runner.invoke(app, [
            "dns", "--domain", "example.com", "--action", "setup-pages",
        ])
        assert result.exit_code == 0
        assert "Created 2 DNS records" in result.output

    @patch("thenine.infra.cloudflare_dns.DNSManager.get_zone_id")
    def test_dns_error_handled(self, mock_zone) -> None:
        mock_zone.side_effect = ValueError("No zone found")
        result = runner.invoke(app, [
            "dns", "--domain", "nonexistent.com", "--action", "list",
        ])
        assert result.exit_code == 1
        assert "Error" in result.output


class TestShowPalette:
    def test_show_palette_with_valid_palette(self) -> None:
        from thenine.cli import _show_palette
        palette = _make_palette()
        _show_palette(palette)

    def test_show_palette_with_non_palette(self) -> None:
        from thenine.cli import _show_palette
        _show_palette("not a palette")

    def test_load_env_no_dotenv(self) -> None:
        from thenine.cli import _load_env
        _load_env()
