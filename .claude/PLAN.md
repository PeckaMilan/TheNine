# Technical Plan

## Status: READY FOR APPROVAL

> See BUSINESS.md for business context.

---

## Current Iteration: Kolobezka (MVP)

### Phase: Kolobezka - Single Project Brand Generation via CLI

---

## Architecture

```
TheNine/
├── src/
│   └── thenine/
│       ├── __init__.py
│       ├── cli.py                  # Typer CLI entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── brand.py            # Brand model + orchestrator
│       │   ├── palette.py          # AI color palette (OKLCH)
│       │   ├── typography.py       # Font selection + pairing
│       │   └── tokens.py           # Design tokens (Style Dictionary)
│       ├── generators/
│       │   ├── __init__.py
│       │   ├── card_pdf.py         # Business card PDF (WeasyPrint)
│       │   ├── card_3d.py          # 3D business card STL (build123d)
│       │   └── website.py          # Astro site generation + deploy
│       └── infra/
│           ├── __init__.py
│           ├── cloudflare_dns.py   # DNS management
│           ├── cloudflare_pages.py # Pages deployment
│           └── google_fonts.py     # Google Fonts API
├── templates/
│   └── astro-landing/              # Astro landing page template
│       ├── src/
│       │   ├── content.config.ts
│       │   ├── pages/
│       │   │   └── index.astro
│       │   ├── layouts/
│       │   │   └── Base.astro
│       │   ├── components/
│       │   │   ├── Hero.astro
│       │   │   ├── Features.astro
│       │   │   ├── Contact.astro
│       │   │   └── Footer.astro
│       │   └── styles/
│       │       └── global.css      # Tailwind 4 @theme (generated)
│       ├── astro.config.mjs
│       ├── package.json
│       └── wrangler.toml
├── tests/
│   ├── unit/
│   │   ├── test_palette.py
│   │   ├── test_typography.py
│   │   ├── test_tokens.py
│   │   ├── test_card_pdf.py
│   │   └── test_card_3d.py
│   ├── integration/
│   │   ├── test_brand_pipeline.py
│   │   └── test_cloudflare.py
│   └── conftest.py
├── output/                         # Generated brand packages (gitignored)
├── pyproject.toml
├── .env                            # API keys (gitignored)
└── .gitignore
```

### Data Flow

```
Input (CLI)                    Core                         Generators              Output
┌──────────┐     ┌──────────────────────┐     ┌────────────────────┐    ┌──────────────┐
│ name     │     │ brand.py             │     │ card_pdf.py        │    │ card.pdf     │
│ tagline  │────>│  ├─> palette.py      │────>│ card_3d.py         │───>│ card.stl     │
│ industry │     │  ├─> typography.py   │     │ website.py         │    │ card.3mf     │
│ mood     │     │  └─> tokens.py       │     │ cloudflare_dns.py  │    │ tokens.json  │
│ domain   │     │                      │     │ cloudflare_pages.py│    │ tokens.css   │
│ contact  │     │ Brand model (frozen) │     │                    │    │ website/     │
└──────────┘     └──────────────────────┘     └────────────────────┘    │ DNS records  │
                                                                        └──────────────┘
```

---

## Tech Stack

| Component | Package | Version | Purpose |
|-----------|---------|---------|---------|
| **Runtime** | Python | 3.13.x | Main runtime |
| **CLI** | Typer | latest | CLI framework (built on Click) |
| **Validation** | Pydantic | 2.12.x | Data models, config validation |
| **Colors** | coloraide | latest | OKLCH palette generation |
| **Accessibility** | wcag-contrast-ratio | latest | WCAG AA/AAA compliance |
| **Fonts** | Google Fonts API | v1 | Font metadata + pairing |
| **Tokens** | Style Dictionary | 5.2.x | Multi-platform token export |
| **PDF Cards** | WeasyPrint | 67.x | HTML/CSS to PDF |
| **3D Cards** | build123d | 0.10.x | Parametric CAD modeling |
| **3D Validation** | trimesh | 4.11.x | Mesh validation + repair |
| **DNS** | cloudflare | 4.3.x | Cloudflare API SDK |
| **Deployment** | Wrangler CLI | latest | Cloudflare Pages deploy |
| **Website** | Astro | 5.x | Static site generation |
| **CSS** | Tailwind CSS | 4.x | Utility-first CSS + @theme |
| **AI** | anthropic | latest | Claude API for color/copy |
| **HTTP** | httpx | latest | Async HTTP client |
| **Testing** | pytest | latest | Test framework |
| **Coverage** | pytest-cov | latest | Coverage reporting |

---

## Tasks - Kolobezka MVP

### Phase 1: Project Foundation (Tasks 1-3)

#### Task 1: Project scaffolding + dependencies
- [ ] Create `pyproject.toml` with all dependencies (uv/pip)
- [ ] Create package structure `src/thenine/`
- [ ] Create `__init__.py` files
- [ ] Create `.gitignore` (add output/, .env, node_modules/)
- [ ] Install and verify all Python dependencies
- [ ] Create `conftest.py` with shared fixtures

**Files:** `pyproject.toml`, `src/thenine/__init__.py`, `src/thenine/core/__init__.py`, `src/thenine/generators/__init__.py`, `src/thenine/infra/__init__.py`, `tests/conftest.py`

#### Task 2: Brand data model (Pydantic)
- [ ] Define `BrandInput` model (name, tagline, industry, mood, contact info, domain)
- [ ] Define `BrandPalette` model (5 colors with OKLCH + hex + purpose)
- [ ] Define `BrandTypography` model (heading font, body font, mono font)
- [ ] Define `BrandTokens` model (colors, fonts, spacing, radii)
- [ ] Define `BrandPackage` model (complete output - palette, typography, tokens, file paths)
- [ ] Write tests for all models (validation, serialization)

**Files:** `src/thenine/core/brand.py`, `tests/unit/test_brand.py`

#### Task 3: Design tokens generator (Style Dictionary)
- [ ] Create `tokens.py` - converts BrandPalette + BrandTypography to token formats
- [ ] Output JSON tokens file (platform-agnostic)
- [ ] Output CSS custom properties (for websites)
- [ ] Output Tailwind CSS 4 @theme config
- [ ] Write tests for token generation

**Files:** `src/thenine/core/tokens.py`, `tests/unit/test_tokens.py`

### Phase 2: Color + Typography (Tasks 4-5)

#### Task 4: AI color palette generator
- [ ] Create `palette.py` with `PaletteGenerator` class
- [ ] Implement OKLCH-based palette generation using coloraide
- [ ] Integrate Claude API for industry-aware color suggestions
- [ ] Implement WCAG AA contrast validation
- [ ] Auto-adjust colors that fail accessibility checks
- [ ] Generate color harmonies (complementary, analogous, triadic)
- [ ] Fallback: deterministic palette from industry + mood (no API needed)
- [ ] Write tests (mock Claude API, test OKLCH math, test accessibility)

**Files:** `src/thenine/core/palette.py`, `tests/unit/test_palette.py`

#### Task 5: Typography selector
- [ ] Create `typography.py` with `TypographySelector` class
- [ ] Integrate Google Fonts API for font metadata
- [ ] Implement font pairing algorithm (serif+sans-serif contrast)
- [ ] Map industry/mood to font categories
- [ ] Download font files for PDF/3D use
- [ ] Fallback: curated font pairs (no API needed)
- [ ] Write tests

**Files:** `src/thenine/core/typography.py`, `src/thenine/infra/google_fonts.py`, `tests/unit/test_typography.py`

### Phase 3: Business Card Generators (Tasks 6-7)

#### Task 6: PDF business card generator
- [ ] Create `card_pdf.py` with `PDFCardGenerator` class
- [ ] Design HTML/CSS card template (85x55mm)
- [ ] Inject brand colors, fonts, contact info
- [ ] Render to PDF via WeasyPrint
- [ ] Support front + back sides
- [ ] Output: print-ready PDF (300 DPI, CMYK-safe colors)
- [ ] Write tests

**Files:** `src/thenine/generators/card_pdf.py`, `tests/unit/test_card_pdf.py`

#### Task 7: 3D business card generator
- [ ] Create `card_3d.py` with `ThreeDCardGenerator` class
- [ ] Create base card geometry (85x55x2mm, rounded corners)
- [ ] Add embossed text (name, title, company) - 0.5mm height
- [ ] Add embossed contact info (email, phone, website)
- [ ] Font selection (sans-serif bold for printability)
- [ ] Validate mesh with trimesh (watertight, volume)
- [ ] Export STL and 3MF
- [ ] Write tests

**Files:** `src/thenine/generators/card_3d.py`, `tests/unit/test_card_3d.py`

### Phase 4: Website Generation (Tasks 8-9)

#### Task 8: Astro landing page template
- [ ] Create `templates/astro-landing/` with full Astro project
- [ ] `astro.config.mjs` - static output, Tailwind 4 plugin
- [ ] `src/pages/index.astro` - main landing page
- [ ] `src/layouts/Base.astro` - HTML skeleton with SEO meta
- [ ] `src/components/Hero.astro` - hero section with tagline
- [ ] `src/components/Features.astro` - feature grid
- [ ] `src/components/Contact.astro` - contact section
- [ ] `src/components/Footer.astro` - footer with links
- [ ] `src/styles/global.css` - placeholder for @theme injection
- [ ] `src/content/data/site.json` - data schema for brand info
- [ ] `package.json` with Astro 5 + Tailwind 4 deps
- [ ] Template must be buildable standalone with dummy data
- [ ] Responsive design (mobile-first)

**Files:** All files under `templates/astro-landing/`

#### Task 9: Website generator + deployer
- [ ] Create `website.py` with `WebsiteGenerator` class
- [ ] Copy Astro template to output directory
- [ ] Inject brand data into `site.json`
- [ ] Inject design tokens into `global.css` (@theme directive)
- [ ] Run `npm install` + `npm run build` via subprocess
- [ ] Create `cloudflare_pages.py` - deploy via Wrangler CLI
- [ ] Write integration tests (mock subprocess)

**Files:** `src/thenine/generators/website.py`, `src/thenine/infra/cloudflare_pages.py`, `tests/integration/test_website.py`

### Phase 5: Cloudflare DNS + CLI (Tasks 10-11)

#### Task 10: Cloudflare DNS management
- [ ] Create `cloudflare_dns.py` with `DNSManager` class
- [ ] List zones (find zone_id for domain)
- [ ] Create/update A, CNAME, TXT records
- [ ] Setup DNS for Cloudflare Pages (CNAME to pages.dev)
- [ ] Verify DNS propagation
- [ ] Write tests (mock Cloudflare SDK)

**Files:** `src/thenine/infra/cloudflare_dns.py`, `tests/integration/test_cloudflare.py`

#### Task 11: CLI interface + orchestrator
- [ ] Create `cli.py` with Typer CLI
- [ ] Command: `thenine generate` - full pipeline
- [ ] Command: `thenine palette` - generate palette only
- [ ] Command: `thenine card` - generate business cards only
- [ ] Command: `thenine website` - generate + deploy website only
- [ ] Command: `thenine dns` - manage DNS only
- [ ] Interactive prompts for missing inputs
- [ ] Rich console output (progress bars, color previews)
- [ ] Write integration test for full pipeline

**Files:** `src/thenine/cli.py`, `tests/integration/test_brand_pipeline.py`

### Phase 6: Testing + Polish (Task 12)

#### Task 12: Integration testing + coverage
- [ ] Full pipeline integration test (generate → card → website → dns)
- [ ] Edge cases (missing API keys, network errors, invalid input)
- [ ] Verify 80%+ test coverage
- [ ] Linting (ruff)
- [ ] Type checking (mypy)

**Files:** `tests/integration/test_brand_pipeline.py`, `pyproject.toml` (ruff/mypy config)

---

## Implementation Order + Dependencies

```
Task 1 (scaffolding)
  └─> Task 2 (brand model)
       ├─> Task 3 (tokens)
       ├─> Task 4 (palette) ──────> Task 6 (PDF card)
       ├─> Task 5 (typography) ──> Task 7 (3D card)
       │                           Task 8 (Astro template)
       │                             └─> Task 9 (website gen)
       └─> Task 10 (DNS)
                                    Task 11 (CLI - depends on all)
                                      └─> Task 12 (integration tests)
```

**Parallel opportunities:**
- Tasks 4 + 5 can run in parallel (palette + typography)
- Tasks 6 + 7 + 8 can run in parallel (PDF card + 3D card + Astro template)
- Task 10 (DNS) is independent, can run anytime after Task 2

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Color space | OKLCH | Perceptually uniform, predictable contrast, 2026 standard |
| PDF engine | WeasyPrint | HTML/CSS input (faster dev), good quality, actively maintained |
| 3D CAD | build123d | Modern Python-first, OCCT kernel, best for parametric generation |
| Site generator | Astro 5 (stable) | Zero JS by default, Cloudflare acquired Astro, native Pages support |
| CSS framework | Tailwind 4 | @theme directive for programmatic design tokens injection |
| Token format | Style Dictionary 5 | Industry standard, multi-platform output (JSON/CSS/Tailwind) |
| CLI | Typer | Modern, type-safe, auto-docs, built on Click |
| Domain API | Cloudflare SDK 4.3 | Official, typed, async support. Registration = dashboard only |
| AI provider | Claude API | Color/copy generation. Deterministic fallback if no API key |
| Package manager | uv | Fast, modern Python package manager |

---

## Environment Variables Required

```
ANTHROPIC_API_KEY=sk-ant-...      # Claude API for AI color generation (optional)
CLOUDFLARE_API_TOKEN=...          # Cloudflare DNS + Pages management
CLOUDFLARE_ACCOUNT_ID=...        # Cloudflare account identifier
GOOGLE_FONTS_API_KEY=...          # Google Fonts metadata (optional)
```

---

## Risks + Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| build123d Windows install issues | HIGH | Test early in Task 1, fallback to CadQuery |
| WeasyPrint font rendering | MEDIUM | Bundle Google Fonts locally, test early |
| Cloudflare API rate limits | LOW | Cache responses, batch operations |
| Astro build failures in subprocess | MEDIUM | Pre-validate template, capture stderr |
| AI color inconsistency | LOW | Deterministic fallback, OKLCH validation |

---

## Definition of Done (MVP)

- [ ] `thenine generate --name "MyProject" --tagline "..." --industry tech --mood modern` produces:
  - `output/myproject/tokens.json` - design tokens
  - `output/myproject/tokens.css` - CSS custom properties
  - `output/myproject/card-front.pdf` - print-ready business card
  - `output/myproject/card.stl` - 3D printable card
  - `output/myproject/card.3mf` - 3D printable card (3MF)
  - `output/myproject/website/` - built Astro site
- [ ] `thenine dns --domain example.com --setup-pages` configures DNS
- [ ] `thenine deploy --domain example.com` deploys website to Cloudflare Pages
- [ ] 80%+ test coverage
- [ ] Works on Windows 11

---

## Escalation Log

| Date | Issue | Decision |
|------|-------|----------|
| 2026-02-10 | Business requirements approved | Proceed to Kolobezka |
| 2026-02-10 | Cloudflare domain registration API = Enterprise only | Manual registration in dashboard, automate DNS + deployment |
| 2026-02-10 | Astro 6 beta vs Astro 5 stable | Use Astro 5 stable, upgrade to 6 when released |
