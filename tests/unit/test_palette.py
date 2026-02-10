"""Tests for AI color palette generator."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from typing import Any

import pytest
import wcag_contrast_ratio as contrast
from coloraide import Color

from thenine.core.brand import BrandColor, BrandPalette
from thenine.core.palette import (
    PaletteGenerator,
    _create_color,
    _ensure_accessible,
    _hex_to_oklch,
    check_contrast,
)


class TestCreateColor:
    def test_valid_color(self) -> None:
        color = _create_color("Test", lightness=0.5, chroma=0.15, hue=250.0, purpose="primary")
        assert isinstance(color, BrandColor)
        assert color.hex.startswith("#")
        assert len(color.hex) == 7

    def test_clamps_lightness(self) -> None:
        color = _create_color("Test", lightness=1.5, chroma=0.1, hue=180.0, purpose="test")
        assert color.oklch_l <= 1.0

    def test_clamps_chroma(self) -> None:
        color = _create_color("Test", lightness=0.5, chroma=0.8, hue=180.0, purpose="test")
        assert color.oklch_c <= 0.4

    def test_wraps_hue(self) -> None:
        color = _create_color("Test", lightness=0.5, chroma=0.1, hue=400.0, purpose="test")
        assert 0 <= color.oklch_h <= 360


class TestHexToOklch:
    def test_white(self) -> None:
        result = _hex_to_oklch("#ffffff")
        assert result["l"] > 0.9
        assert result["c"] < 0.01

    def test_black(self) -> None:
        result = _hex_to_oklch("#000000")
        assert result["l"] < 0.1

    def test_blue(self) -> None:
        result = _hex_to_oklch("#0000ff")
        assert 200 < result["h"] < 300


class TestEnsureAccessible:
    def test_already_accessible(self) -> None:
        color = _create_color("Dark", lightness=0.3, chroma=0.15, hue=250.0, purpose="primary")
        result = _ensure_accessible(color)
        ratio = check_contrast(result.hex, "#ffffff")
        assert ratio >= 4.5

    def test_adjusts_light_color(self) -> None:
        color = _create_color("Light", lightness=0.8, chroma=0.15, hue=250.0, purpose="primary")
        result = _ensure_accessible(color)
        ratio = check_contrast(result.hex, "#ffffff")
        assert ratio >= 4.5
        assert result.oklch_l < color.oklch_l


class TestCheckContrast:
    def test_black_white(self) -> None:
        ratio = check_contrast("#000000", "#ffffff")
        assert ratio >= 20.0

    def test_same_color(self) -> None:
        ratio = check_contrast("#aaaaaa", "#aaaaaa")
        assert ratio == 1.0

    def test_returns_float(self) -> None:
        ratio = check_contrast("#1a56db", "#ffffff")
        assert isinstance(ratio, float)


class TestPaletteGenerator:
    def test_deterministic_produces_palette(self) -> None:
        gen = PaletteGenerator()
        palette = gen.generate("technology", "modern", "TestProject", use_ai=False)
        assert isinstance(palette, BrandPalette)
        assert len(palette.all_colors()) == 5

    def test_deterministic_different_industries(self) -> None:
        gen = PaletteGenerator()
        tech = gen.generate("technology", "modern", "Test", use_ai=False)
        health = gen.generate("health", "modern", "Test", use_ai=False)
        assert tech.primary.hex != health.primary.hex

    def test_deterministic_different_names(self) -> None:
        gen = PaletteGenerator()
        p1 = gen.generate("technology", "modern", "Alpha", use_ai=False)
        p2 = gen.generate("technology", "modern", "Beta", use_ai=False)
        # Same industry/mood but different names produce different palettes
        assert p1.primary.hex != p2.primary.hex

    def test_primary_is_accessible(self) -> None:
        gen = PaletteGenerator()
        for industry in ["technology", "finance", "health", "creative"]:
            palette = gen.generate(industry, "modern", "Test", use_ai=False)
            ratio = check_contrast(palette.primary.hex, "#ffffff")
            assert ratio >= 4.5, f"{industry} primary failed WCAG AA: {ratio}"

    def test_neutral_light_is_light(self) -> None:
        gen = PaletteGenerator()
        palette = gen.generate("technology", "modern", "Test", use_ai=False)
        assert palette.neutral_light.oklch_l > 0.9

    def test_neutral_dark_is_dark(self) -> None:
        gen = PaletteGenerator()
        palette = gen.generate("technology", "modern", "Test", use_ai=False)
        assert palette.neutral_dark.oklch_l < 0.3

    def test_all_hex_valid(self) -> None:
        gen = PaletteGenerator()
        palette = gen.generate("technology", "modern", "Test", use_ai=False)
        for color in palette.all_colors():
            assert color.hex.startswith("#")
            assert len(color.hex) == 7
            int(color.hex[1:], 16)  # Should not raise

    def test_ai_fallback_on_error(self) -> None:
        gen = PaletteGenerator(api_key="invalid-key")
        palette = gen.generate("technology", "modern", "Test", use_ai=True)
        assert isinstance(palette, BrandPalette)

    def test_parse_ai_response(self, mock_anthropic_response: dict[str, Any]) -> None:
        gen = PaletteGenerator()
        palette = gen._parse_ai_response(mock_anthropic_response)
        assert isinstance(palette, BrandPalette)
        assert palette.primary.name == "Deep Blue"
