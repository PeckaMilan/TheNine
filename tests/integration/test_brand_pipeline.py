"""Integration tests for the full brand generation pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from thenine.core.brand import BrandContact, BrandInput, BrandPalette, BrandTypography
from thenine.core.palette import PaletteGenerator
from thenine.core.tokens import create_tokens, export_all
from thenine.core.typography import TypographySelector
from thenine.generators.website import WebsiteGenerator


class TestBrandPipeline:
    """End-to-end integration tests for brand generation."""

    def test_palette_to_tokens_pipeline(self) -> None:
        palette = PaletteGenerator().generate("technology", "modern", "TestBrand", use_ai=False)
        typography = TypographySelector().select("technology", "modern", "TestBrand")
        tokens = create_tokens(palette, typography)

        assert "primary" in tokens.colors
        assert tokens.fonts["heading"] == typography.heading.family

    def test_full_tokens_export(self, tmp_output: Path) -> None:
        palette = PaletteGenerator().generate("finance", "professional", "FinCorp", use_ai=False)
        typography = TypographySelector().select("finance", "professional", "FinCorp")
        tokens = create_tokens(palette, typography)
        paths = export_all(tokens, tmp_output)

        # Verify JSON
        json_data = json.loads(paths["json"].read_text())
        assert json_data["color"]["primary"]["value"] == palette.primary.hex

        # Verify CSS
        css_content = paths["css"].read_text()
        assert "--color-primary:" in css_content
        assert palette.primary.hex in css_content

        # Verify Tailwind
        tw_content = paths["tailwind"].read_text()
        assert "@theme" in tw_content
        assert palette.primary.hex in tw_content

    def test_website_generator_copies_template(self, tmp_output: Path) -> None:
        brand_input = BrandInput(
            name="Test Corp",
            tagline="Testing is important",
            industry="technology",
            mood="modern",
            contact=BrandContact(name="Test User", email="test@example.com"),
        )
        palette = PaletteGenerator().generate("technology", "modern", "Test Corp", use_ai=False)
        typography = TypographySelector().select("technology", "modern", "Test Corp")
        tokens = create_tokens(palette, typography)

        generator = WebsiteGenerator()
        site_dir = generator.generate(brand_input, palette, typography, tokens, tmp_output)

        assert site_dir.exists()
        assert (site_dir / "package.json").exists()
        assert (site_dir / "astro.config.mjs").exists()

        # Verify site data was injected
        site_json = json.loads((site_dir / "src" / "content" / "data" / "site.json").read_text())
        assert site_json["name"] == "Test Corp"
        assert site_json["tagline"] == "Testing is important"

        # Verify theme was injected
        css = (site_dir / "src" / "styles" / "global.css").read_text()
        assert palette.primary.hex in css
        assert typography.heading.family in css

    def test_multiple_industries_produce_different_results(self) -> None:
        industries = ["technology", "finance", "health", "creative", "food"]
        palettes = {}

        for ind in industries:
            palette = PaletteGenerator().generate(ind, "modern", "Test", use_ai=False)
            palettes[ind] = palette.primary.hex

        # All should be different
        assert len(set(palettes.values())) == len(industries)

    def test_deterministic_reproducibility(self) -> None:
        """Same inputs should always produce the same outputs."""
        for _ in range(3):
            p = PaletteGenerator().generate("technology", "modern", "Acme", use_ai=False)
            t = TypographySelector().select("technology", "modern", "Acme")
            assert p.primary.hex == PaletteGenerator().generate(
                "technology", "modern", "Acme", use_ai=False
            ).primary.hex
            assert t.heading.family == TypographySelector().select(
                "technology", "modern", "Acme"
            ).heading.family
