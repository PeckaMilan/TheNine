"""Design tokens generator - converts brand palette + typography to multiple formats."""

from __future__ import annotations

import json
from pathlib import Path

from thenine.core.brand import BrandPalette, BrandTokens, BrandTypography


def create_tokens(palette: BrandPalette, typography: BrandTypography) -> BrandTokens:
    """Create a BrandTokens object from palette and typography."""
    colors = _build_color_scale(palette)
    fonts = {
        "heading": typography.heading.family,
        "body": typography.body.family,
        "mono": typography.mono.family,
    }
    return BrandTokens(colors=colors, fonts=fonts)


def _build_color_scale(palette: BrandPalette) -> dict[str, str]:
    """Build a comprehensive color dictionary from the palette."""
    return {
        "primary": palette.primary.hex,
        "primary-oklch": palette.primary.oklch_css,
        "secondary": palette.secondary.hex,
        "secondary-oklch": palette.secondary.oklch_css,
        "accent": palette.accent.hex,
        "accent-oklch": palette.accent.oklch_css,
        "neutral-light": palette.neutral_light.hex,
        "neutral-light-oklch": palette.neutral_light.oklch_css,
        "neutral-dark": palette.neutral_dark.hex,
        "neutral-dark-oklch": palette.neutral_dark.oklch_css,
    }


def export_json(tokens: BrandTokens, output_path: Path) -> Path:
    """Export tokens as JSON file."""
    data = {
        "color": {key: {"value": val} for key, val in tokens.colors.items() if "-oklch" not in key},
        "font": {key: {"value": val} for key, val in tokens.fonts.items()},
        "spacing": {key: {"value": val} for key, val in tokens.spacing.items()},
        "radii": {key: {"value": val} for key, val in tokens.radii.items()},
    }
    file_path = output_path / "tokens.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return file_path


def export_css(tokens: BrandTokens, output_path: Path) -> Path:
    """Export tokens as CSS custom properties."""
    lines = [":root {"]

    lines.append("  /* Colors */")
    for key, val in tokens.colors.items():
        if "-oklch" not in key:
            lines.append(f"  --color-{key}: {val};")

    lines.append("")
    lines.append("  /* Fonts */")
    for key, val in tokens.fonts.items():
        lines.append(f"  --font-{key}: \"{val}\", system-ui, sans-serif;")

    lines.append("")
    lines.append("  /* Spacing */")
    for key, val in tokens.spacing.items():
        lines.append(f"  --spacing-{key}: {val};")

    lines.append("")
    lines.append("  /* Radii */")
    for key, val in tokens.radii.items():
        lines.append(f"  --radius-{key}: {val};")

    lines.append("}")

    file_path = output_path / "tokens.css"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("\n".join(lines), encoding="utf-8")
    return file_path


def export_tailwind_theme(tokens: BrandTokens, output_path: Path) -> Path:
    """Export tokens as Tailwind CSS 4 @theme directive."""
    lines = ['@import "tailwindcss";', "", "@theme {"]

    lines.append("  /* Brand Colors */")
    for key, val in tokens.colors.items():
        if "-oklch" in key:
            css_key = key.replace("-oklch", "")
            lines.append(f"  --color-brand-{css_key}: {val};")
        else:
            lines.append(f"  --color-brand-{key}: {val};")

    lines.append("")
    lines.append("  /* Fonts */")
    for key, val in tokens.fonts.items():
        lines.append(f"  --font-{key}: \"{val}\", system-ui, sans-serif;")

    lines.append("}")

    file_path = output_path / "tailwind-theme.css"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("\n".join(lines), encoding="utf-8")
    return file_path


def export_all(tokens: BrandTokens, output_path: Path) -> dict[str, Path]:
    """Export tokens in all formats."""
    return {
        "json": export_json(tokens, output_path),
        "css": export_css(tokens, output_path),
        "tailwind": export_tailwind_theme(tokens, output_path),
    }
