"""PDF business card generator using WeasyPrint."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from thenine.core.brand import BrandContact, BrandPalette, BrandTypography

CARD_WIDTH_MM = 85
CARD_HEIGHT_MM = 55

CARD_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<style>
  @page {
    size: {{ width }}mm {{ height }}mm;
    margin: 0;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: "{{ body_font }}", system-ui, sans-serif;
    color: {{ dark_color }};
    background: {{ light_color }};
  }
  .card {
    width: {{ width }}mm;
    height: {{ height }}mm;
    padding: 6mm 7mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
  }
  .card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 3mm;
    height: 100%;
    background: {{ primary_color }};
  }
  .top { padding-left: 5mm; }
  .name {
    font-family: "{{ heading_font }}", system-ui, sans-serif;
    font-size: 12pt;
    font-weight: 700;
    color: {{ dark_color }};
    letter-spacing: 0.02em;
  }
  .title {
    font-size: 8pt;
    color: {{ secondary_color }};
    margin-top: 1mm;
  }
  .bottom {
    padding-left: 5mm;
    font-size: 7pt;
    color: {{ secondary_color }};
    line-height: 1.6;
  }
  .bottom a {
    color: {{ primary_color }};
    text-decoration: none;
  }
  .accent-dot {
    display: inline-block;
    width: 1.5mm;
    height: 1.5mm;
    background: {{ accent_color }};
    border-radius: 50%;
    margin-right: 2mm;
    vertical-align: middle;
  }

  /* Back side */
  .card-back {
    width: {{ width }}mm;
    height: {{ height }}mm;
    display: flex;
    align-items: center;
    justify-content: center;
    background: {{ dark_color }};
    color: {{ light_color }};
    page-break-before: always;
  }
  .card-back .brand-name {
    font-family: "{{ heading_font }}", system-ui, sans-serif;
    font-size: 18pt;
    font-weight: 700;
    letter-spacing: 0.05em;
  }
  .card-back .brand-line {
    width: 12mm;
    height: 0.8mm;
    background: {{ accent_color }};
    margin: 4mm auto 0;
  }
</style>
</head>
<body>
  <!-- Front -->
  <div class="card">
    <div class="top">
      <div class="name">{{ contact_name }}</div>
      {% if contact_title %}<div class="title">{{ contact_title }}</div>{% endif %}
    </div>
    <div class="bottom">
      {% if email %}<div><span class="accent-dot"></span><a href="mailto:{{ email }}">{{ email }}</a></div>{% endif %}
      {% if phone %}<div><span class="accent-dot"></span>{{ phone }}</div>{% endif %}
      {% if website %}<div><span class="accent-dot"></span>{{ website }}</div>{% endif %}
    </div>
  </div>

  <!-- Back -->
  <div class="card-back">
    <div style="text-align: center;">
      <div class="brand-name">{{ brand_name }}</div>
      <div class="brand-line"></div>
    </div>
  </div>
</body>
</html>"""


class PDFCardGenerator:
    """Generates print-ready PDF business cards."""

    def generate(
        self,
        brand_name: str,
        contact: BrandContact,
        palette: BrandPalette,
        typography: BrandTypography,
        output_dir: Path,
    ) -> Path:
        """Generate a PDF business card with front and back sides."""
        html = self._render_html(brand_name, contact, palette, typography)
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / "business-card.pdf"

        from weasyprint import HTML

        HTML(string=html).write_pdf(str(pdf_path))
        return pdf_path

    def _render_html(
        self,
        brand_name: str,
        contact: BrandContact,
        palette: BrandPalette,
        typography: BrandTypography,
    ) -> str:
        template = Template(CARD_HTML_TEMPLATE)
        return template.render(
            width=CARD_WIDTH_MM,
            height=CARD_HEIGHT_MM,
            brand_name=brand_name,
            contact_name=contact.name,
            contact_title=contact.title,
            email=contact.email,
            phone=contact.phone,
            website=contact.website,
            primary_color=palette.primary.hex,
            secondary_color=palette.secondary.hex,
            accent_color=palette.accent.hex,
            light_color=palette.neutral_light.hex,
            dark_color=palette.neutral_dark.hex,
            heading_font=typography.heading.family,
            body_font=typography.body.family,
        )
