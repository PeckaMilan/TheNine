"""Tests for brand domain models."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from thenine.core.brand import (
    BrandColor,
    BrandContact,
    BrandInput,
    BrandPackage,
    BrandPalette,
    BrandTokens,
    BrandTypography,
    FontSpec,
)


class TestBrandContact:
    def test_valid_contact(self) -> None:
        contact = BrandContact(
            name="John Doe",
            title="CEO",
            email="john@example.com",
            phone="+1 555 123 4567",
            website="https://example.com",
        )
        assert contact.name == "John Doe"
        assert contact.email == "john@example.com"

    def test_minimal_contact(self) -> None:
        contact = BrandContact(name="Jane")
        assert contact.name == "Jane"
        assert contact.email == ""

    def test_empty_name_allowed(self) -> None:
        contact = BrandContact(name="")
        assert contact.name == ""

    def test_invalid_email_fails(self) -> None:
        with pytest.raises(ValidationError):
            BrandContact(name="X", email="notanemail")

    def test_frozen(self) -> None:
        contact = BrandContact(name="John")
        with pytest.raises(ValidationError):
            contact.name = "Jane"  # type: ignore[misc]


class TestBrandInput:
    def test_valid_input(self, sample_brand_input: BrandInput) -> None:
        assert sample_brand_input.name == "Acme Corp"
        assert sample_brand_input.industry == "technology"
        assert sample_brand_input.slug == "acme-corp"

    def test_slug_generation(self) -> None:
        inp = BrandInput(name="My Cool Project")
        assert inp.slug == "my-cool-project"

    def test_domain_lowercased(self) -> None:
        inp = BrandInput(name="Test", domain="EXAMPLE.COM")
        assert inp.domain == "example.com"

    def test_invalid_domain_chars(self) -> None:
        with pytest.raises(ValidationError):
            BrandInput(name="Test", domain="exam ple.com")

    def test_defaults(self) -> None:
        inp = BrandInput(name="Test")
        assert inp.industry == "technology"
        assert inp.mood == "modern"
        assert inp.tagline == ""
        assert inp.domain == ""

    def test_empty_name_fails(self) -> None:
        with pytest.raises(ValidationError):
            BrandInput(name="")

    def test_frozen(self) -> None:
        inp = BrandInput(name="Test")
        with pytest.raises(ValidationError):
            inp.name = "Changed"  # type: ignore[misc]


class TestBrandColor:
    def test_valid_color(self) -> None:
        color = BrandColor(
            name="Blue",
            hex="#1a56db",
            oklch_l=0.45,
            oklch_c=0.18,
            oklch_h=260.0,
            purpose="primary",
        )
        assert color.hex == "#1a56db"
        assert color.oklch_css == "oklch(0.450 0.180 260.0)"

    def test_rgb_property(self) -> None:
        color = BrandColor(
            name="White", hex="#ffffff", oklch_l=1.0, oklch_c=0.0, oklch_h=0.0
        )
        assert color.rgb == (255, 255, 255)

    def test_rgb_black(self) -> None:
        color = BrandColor(
            name="Black", hex="#000000", oklch_l=0.0, oklch_c=0.0, oklch_h=0.0
        )
        assert color.rgb == (0, 0, 0)

    def test_invalid_hex(self) -> None:
        with pytest.raises(ValidationError):
            BrandColor(name="Bad", hex="not-hex", oklch_l=0.5, oklch_c=0.1, oklch_h=180.0)

    def test_hex_without_hash(self) -> None:
        with pytest.raises(ValidationError):
            BrandColor(name="Bad", hex="1a56db", oklch_l=0.5, oklch_c=0.1, oklch_h=180.0)

    def test_oklch_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            BrandColor(name="Bad", hex="#1a56db", oklch_l=1.5, oklch_c=0.1, oklch_h=180.0)


class TestBrandPalette:
    def test_all_colors(self, sample_palette: BrandPalette) -> None:
        colors = sample_palette.all_colors()
        assert len(colors) == 5
        assert colors[0] == sample_palette.primary

    def test_to_hex_dict(self, sample_palette: BrandPalette) -> None:
        hex_dict = sample_palette.to_hex_dict()
        assert hex_dict["primary"] == "#1a56db"
        assert len(hex_dict) == 5

    def test_frozen(self, sample_palette: BrandPalette) -> None:
        with pytest.raises(ValidationError):
            sample_palette.primary = sample_palette.secondary  # type: ignore[misc]


class TestFontSpec:
    def test_valid_font(self) -> None:
        font = FontSpec(family="Inter", category="sans-serif", weight=700)
        assert font.family == "Inter"
        assert font.weight == 700

    def test_defaults(self) -> None:
        font = FontSpec(family="Arial")
        assert font.category == "sans-serif"
        assert font.weight == 400

    def test_invalid_weight(self) -> None:
        with pytest.raises(ValidationError):
            FontSpec(family="Arial", weight=50)

    def test_empty_family_fails(self) -> None:
        with pytest.raises(ValidationError):
            FontSpec(family="")


class TestBrandTypography:
    def test_valid_typography(self, sample_typography: BrandTypography) -> None:
        assert sample_typography.heading.family == "Inter"
        assert sample_typography.body.family == "Source Sans 3"
        assert sample_typography.mono.family == "JetBrains Mono"

    def test_default_mono(self) -> None:
        typo = BrandTypography(
            heading=FontSpec(family="Inter", weight=700),
            body=FontSpec(family="Roboto"),
        )
        assert typo.mono.family == "JetBrains Mono"


class TestBrandTokens:
    def test_with_defaults(self) -> None:
        tokens = BrandTokens(
            colors={"primary": "#1a56db"},
            fonts={"heading": "Inter"},
        )
        assert "xs" in tokens.spacing
        assert "md" in tokens.radii

    def test_custom_spacing(self) -> None:
        tokens = BrandTokens(
            colors={"primary": "#1a56db"},
            fonts={"heading": "Inter"},
            spacing={"custom": "2rem"},
        )
        assert tokens.spacing == {"custom": "2rem"}


class TestBrandPackage:
    def test_output_path(
        self,
        sample_brand_input: BrandInput,
        sample_palette: BrandPalette,
        sample_typography: BrandTypography,
    ) -> None:
        tokens = BrandTokens(
            colors=sample_palette.to_hex_dict(),
            fonts={"heading": sample_typography.heading.family},
        )
        package = BrandPackage(
            input=sample_brand_input,
            palette=sample_palette,
            typography=sample_typography,
            tokens=tokens,
        )
        assert "acme-corp" in str(package.output_path)

    def test_custom_output_dir(
        self,
        sample_brand_input: BrandInput,
        sample_palette: BrandPalette,
        sample_typography: BrandTypography,
    ) -> None:
        tokens = BrandTokens(
            colors=sample_palette.to_hex_dict(),
            fonts={"heading": sample_typography.heading.family},
        )
        package = BrandPackage(
            input=sample_brand_input,
            palette=sample_palette,
            typography=sample_typography,
            tokens=tokens,
            output_dir="/tmp/custom",
        )
        assert package.output_path == Path("/tmp/custom")

    def test_serialization(
        self,
        sample_brand_input: BrandInput,
        sample_palette: BrandPalette,
        sample_typography: BrandTypography,
    ) -> None:
        tokens = BrandTokens(
            colors=sample_palette.to_hex_dict(),
            fonts={"heading": sample_typography.heading.family},
        )
        package = BrandPackage(
            input=sample_brand_input,
            palette=sample_palette,
            typography=sample_typography,
            tokens=tokens,
        )
        data = package.model_dump()
        restored = BrandPackage(**data)
        assert restored.input.name == "Acme Corp"
        assert restored.palette.primary.hex == "#1a56db"
