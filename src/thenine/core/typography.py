"""Typography selector - font pairing based on industry and mood."""

from __future__ import annotations

import hashlib
import os
from typing import Any

import httpx

from thenine.core.brand import BrandTypography, FontSpec

# Curated font pairings: (heading, body) tuples
CURATED_PAIRINGS: dict[str, list[tuple[str, str]]] = {
    "technology": [
        ("Inter", "Source Sans 3"),
        ("Space Grotesk", "IBM Plex Sans"),
        ("Outfit", "Nunito Sans"),
    ],
    "finance": [
        ("Playfair Display", "Source Sans 3"),
        ("Libre Baskerville", "Open Sans"),
        ("Cormorant Garamond", "Lato"),
    ],
    "health": [
        ("Nunito", "Open Sans"),
        ("Poppins", "Roboto"),
        ("Raleway", "Source Sans 3"),
    ],
    "education": [
        ("Merriweather", "Source Sans 3"),
        ("Lora", "Open Sans"),
        ("PT Serif", "PT Sans"),
    ],
    "ecommerce": [
        ("Montserrat", "Open Sans"),
        ("Poppins", "Roboto"),
        ("DM Sans", "Inter"),
    ],
    "creative": [
        ("Space Grotesk", "DM Sans"),
        ("Sora", "Inter"),
        ("Clash Display", "Satoshi"),
    ],
    "food": [
        ("Playfair Display", "Lato"),
        ("Josefin Sans", "Open Sans"),
        ("Cormorant Garamond", "Montserrat"),
    ],
    "travel": [
        ("Abril Fatface", "Open Sans"),
        ("Oswald", "Lato"),
        ("Raleway", "Roboto"),
    ],
    "real_estate": [
        ("Playfair Display", "Lato"),
        ("Libre Baskerville", "Montserrat"),
        ("Cormorant Garamond", "Open Sans"),
    ],
    "consulting": [
        ("Inter", "Source Sans 3"),
        ("Libre Baskerville", "Open Sans"),
        ("DM Sans", "IBM Plex Sans"),
    ],
}

# Mood -> font style preferences
MOOD_FONT_STYLE: dict[str, str] = {
    "modern": "sans-serif",
    "classic": "serif",
    "playful": "sans-serif",
    "professional": "serif",
    "bold": "sans-serif",
    "minimal": "sans-serif",
    "luxury": "serif",
    "warm": "serif",
    "cool": "sans-serif",
    "energetic": "sans-serif",
}

MONO_FONTS = ["JetBrains Mono", "Fira Code", "Source Code Pro"]


class TypographySelector:
    """Selects and pairs fonts based on industry and mood."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("GOOGLE_FONTS_API_KEY", "")

    def select(self, industry: str, mood: str, name: str = "") -> BrandTypography:
        """Select a font pairing for the brand."""
        heading_family, body_family = self._pick_pairing(industry, mood, name)

        heading_category = _infer_category(heading_family)
        body_category = _infer_category(body_family)

        heading = FontSpec(
            family=heading_family,
            category=heading_category,
            weight=700,
            google_fonts_url=_google_fonts_url(heading_family, 700),
        )
        body = FontSpec(
            family=body_family,
            category=body_category,
            weight=400,
            google_fonts_url=_google_fonts_url(body_family, 400),
        )
        mono = FontSpec(
            family="JetBrains Mono",
            category="monospace",
            weight=400,
            google_fonts_url=_google_fonts_url("JetBrains Mono", 400),
        )

        return BrandTypography(heading=heading, body=body, mono=mono)

    def _pick_pairing(self, industry: str, mood: str, name: str) -> tuple[str, str]:
        """Pick a heading/body font pairing."""
        pairings = CURATED_PAIRINGS.get(industry, CURATED_PAIRINGS["technology"])

        # Use name hash to deterministically pick from available pairings
        name_hash = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

        # Filter by mood preference (serif/sans-serif for heading)
        preferred_style = MOOD_FONT_STYLE.get(mood, "sans-serif")
        matching = [
            (h, b) for h, b in pairings if _infer_category(h) == preferred_style
        ]

        candidates = matching if matching else pairings
        idx = name_hash % len(candidates)
        return candidates[idx]

    def fetch_font_metadata(self, family: str) -> dict[str, Any] | None:
        """Fetch font metadata from Google Fonts API."""
        if not self._api_key:
            return None

        try:
            url = "https://www.googleapis.com/webfonts/v1/webfonts"
            params = {"key": self._api_key, "family": family}
            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            return items[0] if items else None
        except Exception:
            return None


def _infer_category(family: str) -> str:
    """Infer font category from family name."""
    serif_fonts = {
        "Playfair Display", "Libre Baskerville", "Cormorant Garamond",
        "Merriweather", "Lora", "PT Serif", "Abril Fatface",
    }
    if family in serif_fonts:
        return "serif"
    if family in {"JetBrains Mono", "Fira Code", "Source Code Pro"}:
        return "monospace"
    return "sans-serif"


def _google_fonts_url(family: str, weight: int) -> str:
    """Generate Google Fonts CSS URL."""
    encoded = family.replace(" ", "+")
    return f"https://fonts.googleapis.com/css2?family={encoded}:wght@{weight}&display=swap"
