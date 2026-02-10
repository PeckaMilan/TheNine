"""Google Fonts API integration."""

from __future__ import annotations

import os
from typing import Any

import httpx


class GoogleFontsClient:
    """Client for Google Fonts API."""

    BASE_URL = "https://www.googleapis.com/webfonts/v1/webfonts"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("GOOGLE_FONTS_API_KEY", "")

    def get_font(self, family: str) -> dict[str, Any] | None:
        """Get metadata for a specific font family."""
        if not self._api_key:
            return None

        try:
            response = httpx.get(
                self.BASE_URL,
                params={"key": self._api_key, "family": family},
                timeout=10.0,
            )
            response.raise_for_status()
            items = response.json().get("items", [])
            return items[0] if items else None
        except Exception:
            return None

    def get_css_url(self, families: list[tuple[str, list[int]]]) -> str:
        """Generate a Google Fonts CSS URL for multiple families and weights.

        Args:
            families: List of (family_name, [weights]) tuples.
        """
        parts = []
        for family, weights in families:
            encoded = family.replace(" ", "+")
            weight_str = ";".join(str(w) for w in sorted(weights))
            parts.append(f"family={encoded}:wght@{weight_str}")

        return f"https://fonts.googleapis.com/css2?{'&'.join(parts)}&display=swap"
