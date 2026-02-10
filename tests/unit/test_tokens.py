"""Tests for design tokens generator."""

from __future__ import annotations

import json
from pathlib import Path

from thenine.core.brand import BrandPalette, BrandTypography
from thenine.core.tokens import (
    create_tokens,
    export_all,
    export_css,
    export_json,
    export_tailwind_theme,
)


class TestCreateTokens:
    def test_creates_tokens(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        assert "primary" in tokens.colors
        assert "heading" in tokens.fonts
        assert tokens.fonts["heading"] == "Inter"

    def test_all_colors_present(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        for key in ["primary", "secondary", "accent", "neutral-light", "neutral-dark"]:
            assert key in tokens.colors

    def test_oklch_values_included(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        assert "primary-oklch" in tokens.colors
        assert "oklch(" in tokens.colors["primary-oklch"]


class TestExportJson:
    def test_creates_file(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography, tmp_output: Path
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        path = export_json(tokens, tmp_output)
        assert path.exists()
        assert path.suffix == ".json"

    def test_valid_json(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography, tmp_output: Path
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        path = export_json(tokens, tmp_output)
        data = json.loads(path.read_text())
        assert "color" in data
        assert "font" in data
        assert "spacing" in data

    def test_color_values(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography, tmp_output: Path
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        path = export_json(tokens, tmp_output)
        data = json.loads(path.read_text())
        assert data["color"]["primary"]["value"] == sample_palette.primary.hex


class TestExportCss:
    def test_creates_file(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography, tmp_output: Path
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        path = export_css(tokens, tmp_output)
        assert path.exists()
        assert path.suffix == ".css"

    def test_contains_custom_properties(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography, tmp_output: Path
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        path = export_css(tokens, tmp_output)
        content = path.read_text()
        assert "--color-primary:" in content
        assert "--font-heading:" in content
        assert "--spacing-md:" in content
        assert ":root {" in content


class TestExportTailwind:
    def test_creates_file(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography, tmp_output: Path
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        path = export_tailwind_theme(tokens, tmp_output)
        assert path.exists()

    def test_contains_theme_directive(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography, tmp_output: Path
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        path = export_tailwind_theme(tokens, tmp_output)
        content = path.read_text()
        assert "@theme {" in content
        assert "@import" in content
        assert "--color-brand-primary:" in content
        assert "--font-heading:" in content


class TestExportAll:
    def test_exports_all_formats(
        self, sample_palette: BrandPalette, sample_typography: BrandTypography, tmp_output: Path
    ) -> None:
        tokens = create_tokens(sample_palette, sample_typography)
        paths = export_all(tokens, tmp_output)
        assert "json" in paths
        assert "css" in paths
        assert "tailwind" in paths
        for p in paths.values():
            assert p.exists()
