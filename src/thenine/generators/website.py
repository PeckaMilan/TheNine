"""Website generator - copies Astro template, injects brand data, builds."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from thenine.core.brand import BrandInput, BrandPalette, BrandTokens, BrandTypography

TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates" / "astro-landing"


class WebsiteGenerator:
    """Generates a branded Astro website from the landing page template."""

    def __init__(self, template_dir: Path | None = None) -> None:
        self._template_dir = template_dir or TEMPLATE_DIR

    def generate(
        self,
        brand_input: BrandInput,
        palette: BrandPalette,
        typography: BrandTypography,
        tokens: BrandTokens,
        output_dir: Path,
    ) -> Path:
        """Generate a branded website in the output directory."""
        site_dir = output_dir / "website"

        self._copy_template(site_dir)
        self._inject_site_data(site_dir, brand_input)
        self._inject_theme(site_dir, palette, typography)

        return site_dir

    def build(self, site_dir: Path) -> Path:
        """Run npm install and build the Astro site."""
        self._run_npm(site_dir, ["install"])
        self._run_npm(site_dir, ["run", "build"])
        return site_dir / "dist"

    def _copy_template(self, dest: Path) -> None:
        """Copy the Astro template to the destination, excluding node_modules."""
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree(
            self._template_dir,
            dest,
            ignore=shutil.ignore_patterns("node_modules", "dist", ".astro"),
        )

    def _inject_site_data(self, site_dir: Path, brand_input: BrandInput) -> None:
        """Write site.json with brand data."""
        site_data = {
            "name": brand_input.name,
            "tagline": brand_input.tagline,
            "description": brand_input.description or brand_input.tagline,
            "features": [
                {
                    "title": "Lightning Fast",
                    "description": "Built for performance from the ground up.",
                    "icon": "rocket",
                },
                {
                    "title": "Secure by Default",
                    "description": "Enterprise-grade security in every layer.",
                    "icon": "shield",
                },
                {
                    "title": "Easy to Use",
                    "description": "Intuitive interface that stays out of your way.",
                    "icon": "zap",
                },
            ],
            "contact": {
                "email": brand_input.contact.email,
                "phone": brand_input.contact.phone,
                "address": "",
            },
            "social": {"github": "", "twitter": "", "linkedin": ""},
            "cta": {
                "text": "Get Started",
                "url": f"mailto:{brand_input.contact.email}" if brand_input.contact.email else "#contact",
            },
        }

        data_path = site_dir / "src" / "content" / "data" / "site.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(json.dumps(site_data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _inject_theme(
        self, site_dir: Path, palette: BrandPalette, typography: BrandTypography
    ) -> None:
        """Write Tailwind 4 @theme CSS with brand tokens."""
        heading_url = typography.heading.google_fonts_url
        body_url = typography.body.google_fonts_url

        lines = [
            '@import "tailwindcss";',
            "",
            "@theme {",
            f"  --color-brand-primary: {palette.primary.hex};",
            f"  --color-brand-secondary: {palette.secondary.hex};",
            f"  --color-brand-accent: {palette.accent.hex};",
            f"  --color-brand-light: {palette.neutral_light.hex};",
            f"  --color-brand-dark: {palette.neutral_dark.hex};",
            "",
            f'  --font-heading: "{typography.heading.family}", system-ui, sans-serif;',
            f'  --font-body: "{typography.body.family}", system-ui, sans-serif;',
            "}",
        ]

        css_path = site_dir / "src" / "styles" / "global.css"
        css_path.write_text("\n".join(lines), encoding="utf-8")

    def _run_npm(self, site_dir: Path, args: list[str]) -> None:
        """Run an npm command in the site directory."""
        result = subprocess.run(
            ["npm", *args],
            cwd=str(site_dir),
            capture_output=True,
            text=True,
            timeout=120,
            shell=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"npm {' '.join(args)} failed:\n{result.stderr}")
