"""Shared test fixtures for TheNine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from thenine.core.brand import (
    BrandColor,
    BrandContact,
    BrandInput,
    BrandPalette,
    BrandTypography,
    FontSpec,
)


@pytest.fixture
def sample_brand_input() -> BrandInput:
    return BrandInput(
        name="Acme Corp",
        tagline="Building the future",
        industry="technology",
        mood="modern",
        contact=BrandContact(
            name="John Doe",
            title="CEO",
            email="john@acme.com",
            phone="+1 555 123 4567",
            website="https://acme.com",
        ),
        domain="acme.com",
    )


@pytest.fixture
def sample_palette() -> BrandPalette:
    return BrandPalette(
        primary=BrandColor(
            name="Deep Blue",
            hex="#1a56db",
            oklch_l=0.45,
            oklch_c=0.18,
            oklch_h=260.0,
            purpose="primary",
        ),
        secondary=BrandColor(
            name="Slate",
            hex="#475569",
            oklch_l=0.45,
            oklch_c=0.03,
            oklch_h=250.0,
            purpose="secondary",
        ),
        accent=BrandColor(
            name="Amber",
            hex="#d97706",
            oklch_l=0.65,
            oklch_c=0.18,
            oklch_h=75.0,
            purpose="accent",
        ),
        neutral_light=BrandColor(
            name="Cloud",
            hex="#f8fafc",
            oklch_l=0.98,
            oklch_c=0.005,
            oklch_h=250.0,
            purpose="neutral-light",
        ),
        neutral_dark=BrandColor(
            name="Charcoal",
            hex="#1e293b",
            oklch_l=0.25,
            oklch_c=0.03,
            oklch_h=250.0,
            purpose="neutral-dark",
        ),
    )


@pytest.fixture
def sample_typography() -> BrandTypography:
    return BrandTypography(
        heading=FontSpec(
            family="Inter",
            category="sans-serif",
            weight=700,
            google_fonts_url="https://fonts.googleapis.com/css2?family=Inter:wght@700",
        ),
        body=FontSpec(
            family="Source Sans 3",
            category="sans-serif",
            weight=400,
            google_fonts_url="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400",
        ),
        mono=FontSpec(
            family="JetBrains Mono",
            category="monospace",
            weight=400,
            google_fonts_url="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400",
        ),
    )


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_anthropic_response() -> dict[str, Any]:
    return {
        "colors": [
            {
                "name": "Deep Blue",
                "hex": "#1a56db",
                "purpose": "primary",
                "psychology": "Conveys trust and professionalism",
            },
            {
                "name": "Slate",
                "hex": "#475569",
                "purpose": "secondary",
                "psychology": "Stability and neutrality",
            },
            {
                "name": "Amber",
                "hex": "#d97706",
                "purpose": "accent",
                "psychology": "Energy and attention",
            },
            {
                "name": "Cloud",
                "hex": "#f8fafc",
                "purpose": "neutral-light",
                "psychology": "Clean and spacious",
            },
            {
                "name": "Charcoal",
                "hex": "#1e293b",
                "purpose": "neutral-dark",
                "psychology": "Authority and sophistication",
            },
        ]
    }
