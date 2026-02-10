# Business Requirements

## Status: DISCOVERY

> This document is created collaboratively by Human + Claude + Gemini

---

## Vision

**TheNine** is an automated brand identity framework that generates complete, production-ready brand packages for projects and companies. From a single input (project name + description), it produces:

- Unified design system (colors, typography, design tokens)
- Professional website (landing page or multi-page)
- Domain management (DNS, SSL via Cloudflare)
- Business cards (print-ready PDF + 3D-printable STL/3MF for embossed cards)
- Brand guidelines document

Built first for the founder's own portfolio of projects, then offered as a SaaS product.

## Problem Statement

Founders and developers with multiple projects/companies lack consistent brand identity. Creating websites, business cards, and design systems for each project is:

- **Time-consuming** - hours of design work per project
- **Expensive** - designers charge $500-5000+ per brand package
- **Inconsistent** - each project gets different quality
- **Unmaintained** - once created, branding assets drift

No existing tool combines domain management + website generation + print materials + 3D-printable cards in one automated pipeline.

## Target Users

1. **Primary (MVP):** The founder - 5-15 existing projects needing brand identity
2. **Secondary (SaaS):** Solo developers, indie hackers, small agencies managing multiple brands
3. **Tertiary (Growth):** Agencies, startup studios, accelerators

## Success Criteria

- [ ] Generate complete brand package for 1 project in < 5 minutes
- [ ] Deploy live website to custom domain automatically
- [ ] Produce print-ready business card PDF
- [ ] Generate 3D-printable embossed business card STL
- [ ] All outputs follow a consistent design system
- [ ] Framework handles 10+ projects without manual intervention

## Constraints

- **Platform:** Python backend (FastAPI), Astro for website generation
- **Infrastructure:** Cloudflare (domains, DNS, Pages deployment)
- **Domain registration:** Manual via Cloudflare dashboard (API is Enterprise-only), DNS management automated via API
- **3D printing:** PLA material, FDM printer, embossed/relief cards
- **Budget:** Minimal - leverage free tiers (Cloudflare Pages free, at-cost domains)

## Out of Scope

- Logo generation (AI logos are low quality - use placeholder or manual logo)
- Social media management
- Email marketing integration
- E-commerce / payment processing (for MVP)
- Mobile app
- Video/animation branding

---

## Competitive Analysis

| Feature | Looka | Tailor Brands | uBrand | **TheNine** |
|---------|-------|--------------|--------|-------------|
| Logo generation | Yes | Yes | Yes | No (manual) |
| Color palette | Yes | Yes | Yes | **Yes (AI)** |
| Typography | Yes | Yes | Yes | **Yes (AI)** |
| Website generation | Basic | Basic | No | **Full (Astro)** |
| Domain management | No | No | No | **Yes (Cloudflare)** |
| Business cards (PDF) | Yes | Yes | Yes | **Yes** |
| 3D-printable cards | No | No | No | **Yes** |
| Design tokens export | No | No | No | **Yes (JSON/CSS/Tailwind)** |
| Self-hosted/API | No | No | No | **Yes** |
| Multi-project mgmt | No | No | Limited | **Yes** |

**Key differentiators:**
1. Domain management + DNS automation
2. 3D-printable business cards
3. Developer-friendly design tokens export
4. API-first, self-hostable
5. Multi-project management from single dashboard

---

## Revenue Model

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | 1 project, basic brand package |
| Pro | $29/month | 10 projects, custom domains, full exports |
| Agency | $99/month | Unlimited projects, white-label, API access |
| Enterprise | $299/month | Custom AI training, priority support |

---

## Iterations (Agile Roadmap)

### Kolobezka (MVP)
*Minimum viable - single project brand generation*

- [ ] Project input form (name, description, industry, mood)
- [ ] AI color palette generation (5-color harmonious palette)
- [ ] AI typography selection (heading + body font pairing)
- [ ] Design tokens output (JSON, CSS variables, Tailwind config)
- [ ] Business card generator (print-ready PDF, 85x55mm)
- [ ] 3D business card generator (embossed STL/3MF, build123d)
- [ ] Basic landing page generation (Astro template)
- [ ] Cloudflare DNS management (add/update records via API)
- [ ] Cloudflare Pages deployment (Wrangler CLI)
- [ ] CLI interface for running the pipeline

### Kolo
*Web UI, multi-project management*

- [ ] FastAPI backend with REST API
- [ ] Web dashboard (project list, brand overview)
- [ ] Multiple Astro templates (landing, multi-page, portfolio)
- [ ] Brand guidelines PDF generation
- [ ] Project comparison view
- [ ] Template customization (colors, layout variants)

### Motorka
*AI-powered improvements, quality*

- [ ] AI-powered brand positioning wizard (questionnaire)
- [ ] Smart font pairing based on industry research
- [ ] Accessibility checker (WCAG contrast ratios)
- [ ] SEO optimization for generated sites
- [ ] QR code integration on business cards
- [ ] Multi-material 3D card support (dual-color)

### Auto
*SaaS-ready, multi-tenant*

- [ ] User authentication (Firebase Auth)
- [ ] Multi-tenant architecture
- [ ] Billing integration (Stripe)
- [ ] Custom domain management per user
- [ ] White-label option for agencies
- [ ] Usage analytics dashboard

### Letadlo
*Enterprise, API marketplace*

- [ ] Public API with documentation
- [ ] Webhook integrations
- [ ] Custom AI model training per brand
- [ ] A/B testing for brand variations
- [ ] Enterprise SSO
- [ ] Brand evolution tracking (version history)

---

## Tech Stack (Proposed)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Backend | Python / FastAPI | Async, modern, great ecosystem |
| Website gen | Astro 5 | Zero JS, fast, Cloudflare Pages native |
| Design tokens | Style Dictionary | Industry standard, multi-platform |
| 3D modeling | build123d | Modern Python CAD, OCCT-powered |
| 3D validation | trimesh | Mesh repair, printability checks |
| PDF generation | ReportLab or WeasyPrint | Business cards, brand guidelines |
| Domain/DNS | Cloudflare Python SDK (v4.3+) | Official, typed, async |
| Deployment | Wrangler CLI | Cloudflare Pages deployment |
| Database | SQLite (MVP) → PostgreSQL (SaaS) | Simple start, scale later |

---

## Sign-off

- [x] Human approved
- [x] Ready for technical planning
