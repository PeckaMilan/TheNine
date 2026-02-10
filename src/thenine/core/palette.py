"""AI-powered color palette generator using OKLCH color space."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

import wcag_contrast_ratio as contrast
from coloraide import Color

from thenine.core.brand import BrandColor, BrandPalette

# Industry -> base hue mapping for deterministic fallback
INDUSTRY_HUES: dict[str, float] = {
    "technology": 250.0,
    "finance": 220.0,
    "health": 150.0,
    "education": 270.0,
    "ecommerce": 30.0,
    "creative": 320.0,
    "food": 50.0,
    "travel": 180.0,
    "real_estate": 40.0,
    "consulting": 210.0,
    "other": 200.0,
}

# Mood -> chroma + lightness adjustments
MOOD_ADJUSTMENTS: dict[str, dict[str, float]] = {
    "modern": {"chroma": 0.14, "lightness_offset": 0.0},
    "classic": {"chroma": 0.10, "lightness_offset": 0.05},
    "playful": {"chroma": 0.20, "lightness_offset": -0.05},
    "professional": {"chroma": 0.12, "lightness_offset": 0.05},
    "bold": {"chroma": 0.22, "lightness_offset": -0.10},
    "minimal": {"chroma": 0.08, "lightness_offset": 0.10},
    "luxury": {"chroma": 0.12, "lightness_offset": -0.05},
    "warm": {"chroma": 0.16, "lightness_offset": 0.0},
    "cool": {"chroma": 0.14, "lightness_offset": 0.05},
    "energetic": {"chroma": 0.20, "lightness_offset": -0.05},
}


class PaletteGenerator:
    """Generates brand color palettes using OKLCH color space."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    def generate(
        self, industry: str, mood: str, name: str = "", use_ai: bool = True
    ) -> BrandPalette:
        """Generate a 5-color brand palette.

        Tries AI generation first, falls back to deterministic algorithm.
        """
        if use_ai and self._api_key:
            try:
                return self._generate_with_ai(industry, mood, name)
            except Exception:
                pass

        return self._generate_deterministic(industry, mood, name)

    def _generate_with_ai(self, industry: str, mood: str, name: str) -> BrandPalette:
        """Generate palette using Claude API."""
        import anthropic

        client = anthropic.Anthropic(api_key=self._api_key)

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Generate a professional 5-color brand palette for:\n"
                        f"Name: {name}\nIndustry: {industry}\nMood: {mood}\n\n"
                        f"Return ONLY valid JSON (no markdown) with this structure:\n"
                        f'{{"colors": [\n'
                        f'  {{"name": "Color Name", "hex": "#RRGGBB", '
                        f'"purpose": "primary/secondary/accent/neutral-light/neutral-dark", '
                        f'"psychology": "Why this color"}}\n'
                        f"]}}\n\n"
                        f"Requirements:\n"
                        f"- 1 primary, 1 secondary, 1 accent, 1 neutral-light, 1 neutral-dark\n"
                        f"- All hex codes must be valid 6-digit hex\n"
                        f"- Primary should work on white bg (WCAG AA contrast)\n"
                        f"- Neutral-light should be very light (near white)\n"
                        f"- Neutral-dark should be very dark (near black)"
                    ),
                }
            ],
        )

        response_text = message.content[0].text
        data = json.loads(response_text)
        return self._parse_ai_response(data)

    def _parse_ai_response(self, data: dict[str, Any]) -> BrandPalette:
        """Parse AI response into BrandPalette."""
        purpose_map: dict[str, BrandColor] = {}

        for color_data in data["colors"]:
            hex_val = color_data["hex"]
            purpose = color_data["purpose"]
            oklch = _hex_to_oklch(hex_val)

            brand_color = BrandColor(
                name=color_data["name"],
                hex=hex_val,
                oklch_l=oklch["l"],
                oklch_c=oklch["c"],
                oklch_h=oklch["h"],
                purpose=purpose,
            )
            purpose_map[purpose] = brand_color

        return BrandPalette(
            primary=purpose_map["primary"],
            secondary=purpose_map["secondary"],
            accent=purpose_map["accent"],
            neutral_light=purpose_map["neutral-light"],
            neutral_dark=purpose_map["neutral-dark"],
        )

    def _generate_deterministic(self, industry: str, mood: str, name: str) -> BrandPalette:
        """Generate palette using deterministic algorithm based on industry + mood."""
        base_hue = INDUSTRY_HUES.get(industry, INDUSTRY_HUES["other"])
        adjustments = MOOD_ADJUSTMENTS.get(mood, MOOD_ADJUSTMENTS["modern"])

        # Add name-based variation to hue (0-30 degree shift)
        name_hash = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
        hue_shift = (name_hash % 30) - 15
        base_hue = (base_hue + hue_shift) % 360

        chroma = adjustments["chroma"]
        l_offset = adjustments["lightness_offset"]

        primary = _create_color(
            "Brand Primary",
            lightness=0.45 + l_offset,
            chroma=chroma,
            hue=base_hue,
            purpose="primary",
        )
        secondary = _create_color(
            "Brand Secondary",
            lightness=0.50 + l_offset,
            chroma=chroma * 0.5,
            hue=(base_hue + 30) % 360,
            purpose="secondary",
        )
        accent = _create_color(
            "Brand Accent",
            lightness=0.65 + l_offset,
            chroma=chroma * 1.3,
            hue=(base_hue + 180) % 360,
            purpose="accent",
        )
        neutral_light = _create_color(
            "Neutral Light",
            lightness=0.97,
            chroma=0.005,
            hue=base_hue,
            purpose="neutral-light",
        )
        neutral_dark = _create_color(
            "Neutral Dark",
            lightness=0.20,
            chroma=0.03,
            hue=base_hue,
            purpose="neutral-dark",
        )

        # Ensure primary passes WCAG AA against white
        primary = _ensure_accessible(primary, against_hex="#ffffff")

        return BrandPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            neutral_light=neutral_light,
            neutral_dark=neutral_dark,
        )


def _create_color(
    name: str, lightness: float, chroma: float, hue: float, purpose: str
) -> BrandColor:
    """Create a BrandColor from OKLCH values."""
    lightness = max(0.0, min(1.0, lightness))
    chroma = max(0.0, min(0.4, chroma))
    hue = hue % 360

    color = Color("oklch", [lightness, chroma, hue])
    srgb = color.convert("srgb").fit("srgb")
    hex_val = srgb.to_string(hex=True)

    return BrandColor(
        name=name,
        hex=hex_val,
        oklch_l=round(lightness, 3),
        oklch_c=round(chroma, 3),
        oklch_h=round(hue, 1),
        purpose=purpose,
    )


def _hex_to_oklch(hex_val: str) -> dict[str, float]:
    """Convert hex color to OKLCH values."""
    color = Color(hex_val).convert("oklch")
    return {
        "l": round(max(0.0, min(1.0, color["lightness"])), 3),
        "c": round(max(0.0, min(0.5, color["chroma"])), 3),
        "h": round(color["hue"] % 360, 1) if color["hue"] == color["hue"] else 0.0,
    }


def _ensure_accessible(color: BrandColor, against_hex: str = "#ffffff") -> BrandColor:
    """Ensure a color meets WCAG AA contrast against the given background."""
    fg = Color(color.hex).convert("srgb")
    bg = Color(against_hex).convert("srgb")

    fg_rgb = (fg["red"], fg["green"], fg["blue"])
    bg_rgb = (bg["red"], bg["green"], bg["blue"])

    ratio = contrast.rgb(fg_rgb, bg_rgb)

    if contrast.passes_AA(ratio):
        return color

    # Darken until accessible
    new_l = color.oklch_l
    while new_l > 0.1:
        new_l -= 0.02
        candidate = _create_color(color.name, new_l, color.oklch_c, color.oklch_h, color.purpose)

        fg = Color(candidate.hex).convert("srgb")
        fg_rgb = (fg["red"], fg["green"], fg["blue"])
        ratio = contrast.rgb(fg_rgb, bg_rgb)

        if contrast.passes_AA(ratio):
            return candidate

    return color


def check_contrast(hex1: str, hex2: str) -> float:
    """Check contrast ratio between two hex colors."""
    c1 = Color(hex1).convert("srgb")
    c2 = Color(hex2).convert("srgb")

    rgb1 = (c1["red"], c1["green"], c1["blue"])
    rgb2 = (c2["red"], c2["green"], c2["blue"])

    return contrast.rgb(rgb1, rgb2)
