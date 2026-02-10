"""TheNine CLI - brand identity generation from the command line."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from thenine.core.brand import BrandContact, BrandInput

app = typer.Typer(
    name="thenine",
    help="Automated brand identity framework",
    no_args_is_help=True,
)
console = Console()


def _load_env() -> None:
    """Load .env file if it exists."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


@app.command()
def generate(
    name: str = typer.Option(..., prompt="Brand/project name"),
    tagline: str = typer.Option("", prompt="Tagline (optional)", prompt_required=False),
    industry: str = typer.Option(
        "technology",
        help="Industry: technology, finance, health, education, ecommerce, creative, food, travel, real_estate, consulting",
    ),
    mood: str = typer.Option(
        "modern",
        help="Mood: modern, classic, playful, professional, bold, minimal, luxury, warm, cool, energetic",
    ),
    contact_name: str = typer.Option("", help="Contact person name"),
    contact_email: str = typer.Option("", help="Contact email"),
    contact_phone: str = typer.Option("", help="Contact phone"),
    contact_title: str = typer.Option("", help="Contact title/role"),
    domain: str = typer.Option("", help="Domain name (e.g. acme.com)"),
    output: str = typer.Option("", help="Output directory (default: output/<slug>)"),
    skip_website: bool = typer.Option(False, "--skip-website", help="Skip website generation"),
    skip_3d: bool = typer.Option(False, "--skip-3d", help="Skip 3D card generation"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Use deterministic generation (no API calls)"),
) -> None:
    """Generate a complete brand identity package."""
    _load_env()

    contact = BrandContact(
        name=contact_name or name,
        title=contact_title,
        email=contact_email,
        phone=contact_phone,
        website=domain,
    )

    brand_input = BrandInput(
        name=name,
        tagline=tagline,
        industry=industry,
        mood=mood,
        contact=contact,
        domain=domain,
    )

    output_dir = Path(output) if output else Path("output") / brand_input.slug
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(Panel(f"[bold]{name}[/bold]\n{tagline}", title="Generating Brand Identity"))

    # Step 1: Palette
    with console.status("[bold blue]Generating color palette..."):
        from thenine.core.palette import PaletteGenerator

        palette = PaletteGenerator().generate(industry, mood, name, use_ai=not no_ai)

    _show_palette(palette)

    # Step 2: Typography
    with console.status("[bold blue]Selecting typography..."):
        from thenine.core.typography import TypographySelector

        typography = TypographySelector().select(industry, mood, name)

    console.print(f"  Heading: [bold]{typography.heading.family}[/bold]")
    console.print(f"  Body:    {typography.body.family}")

    # Step 3: Tokens
    with console.status("[bold blue]Generating design tokens..."):
        from thenine.core.tokens import create_tokens, export_all

        tokens = create_tokens(palette, typography)
        token_paths = export_all(tokens, output_dir)

    console.print(f"  [green]Tokens:[/green] {', '.join(p.name for p in token_paths.values())}")

    # Step 4: PDF Card
    with console.status("[bold blue]Creating PDF business card..."):
        try:
            from thenine.generators.card_pdf import PDFCardGenerator

            pdf_path = PDFCardGenerator().generate(name, contact, palette, typography, output_dir)
            console.print(f"  [green]PDF Card:[/green] {pdf_path.name}")
        except OSError as e:
            if "libgobject" in str(e) or "GTK" in str(e):
                console.print(
                    "  [yellow]PDF Card skipped:[/yellow] GTK3 not installed. "
                    "Install via: https://www.msys2.org/ then `pacman -S mingw-w64-x86_64-pango`"
                )
            else:
                raise

    # Step 5: 3D Card
    if not skip_3d:
        with console.status("[bold blue]Creating 3D business card..."):
            try:
                from thenine.generators.card_3d import ThreeDCardGenerator

                card_3d_paths = ThreeDCardGenerator().generate(name, contact, output_dir)
                console.print(
                    f"  [green]3D Card:[/green] {', '.join(p.name for p in card_3d_paths.values())}"
                )
            except Exception as e:
                console.print(f"  [yellow]3D Card skipped:[/yellow] {e}")

    # Step 6: Website
    if not skip_website:
        with console.status("[bold blue]Generating website..."):
            try:
                from thenine.generators.website import WebsiteGenerator

                site_dir = WebsiteGenerator().generate(brand_input, palette, typography, tokens, output_dir)
                console.print(f"  [green]Website:[/green] {site_dir}")
            except Exception as e:
                console.print(f"  [yellow]Website skipped:[/yellow] {e}")

    # Summary
    console.print()
    console.print(Panel(f"[bold green]Brand package generated![/bold green]\n{output_dir}", title="Done"))


@app.command()
def palette(
    name: str = typer.Option("Brand", help="Brand name"),
    industry: str = typer.Option("technology"),
    mood: str = typer.Option("modern"),
    no_ai: bool = typer.Option(False, "--no-ai"),
) -> None:
    """Generate a color palette only."""
    _load_env()

    from thenine.core.palette import PaletteGenerator

    result = PaletteGenerator().generate(industry, mood, name, use_ai=not no_ai)
    _show_palette(result)


@app.command()
def card(
    name: str = typer.Option(..., prompt="Brand name"),
    contact_name: str = typer.Option("", help="Contact person name"),
    contact_email: str = typer.Option("", help="Contact email"),
    contact_title: str = typer.Option("", help="Contact title"),
    industry: str = typer.Option("technology"),
    mood: str = typer.Option("modern"),
    output: str = typer.Option("output/cards"),
    skip_3d: bool = typer.Option(False, "--skip-3d"),
) -> None:
    """Generate business cards only."""
    _load_env()
    output_dir = Path(output)

    from thenine.core.palette import PaletteGenerator
    from thenine.core.typography import TypographySelector
    from thenine.generators.card_pdf import PDFCardGenerator

    contact = BrandContact(name=contact_name or name, title=contact_title, email=contact_email)
    pal = PaletteGenerator().generate(industry, mood, name, use_ai=False)
    typo = TypographySelector().select(industry, mood, name)

    pdf_path = PDFCardGenerator().generate(name, contact, pal, typo, output_dir)
    console.print(f"[green]PDF:[/green] {pdf_path}")

    if not skip_3d:
        try:
            from thenine.generators.card_3d import ThreeDCardGenerator

            paths = ThreeDCardGenerator().generate(name, contact, output_dir)
            for fmt, p in paths.items():
                console.print(f"[green]{fmt.upper()}:[/green] {p}")
        except Exception as e:
            console.print(f"[yellow]3D Card skipped:[/yellow] {e}")


@app.command()
def dns(
    domain: str = typer.Option(..., prompt="Domain name"),
    action: str = typer.Option("list", help="Action: list, setup-pages"),
    pages_project: str = typer.Option("", help="Cloudflare Pages project name (for setup-pages)"),
) -> None:
    """Manage Cloudflare DNS records."""
    _load_env()

    from thenine.infra.cloudflare_dns import DNSManager

    manager = DNSManager()

    try:
        zone_id = manager.get_zone_id(domain)
        console.print(f"Zone ID: {zone_id}")

        if action == "list":
            records = manager.list_records(zone_id)
            table = Table(title=f"DNS Records: {domain}")
            table.add_column("Type")
            table.add_column("Name")
            table.add_column("Content")
            table.add_column("Proxied")
            for r in records:
                table.add_row(r["type"], r["name"], r["content"], str(r["proxied"]))
            console.print(table)

        elif action == "setup-pages":
            if not pages_project:
                pages_project = domain.split(".")[0]
            records = manager.setup_pages_dns(zone_id, domain, pages_project)
            console.print(f"[green]Created {len(records)} DNS records for Pages[/green]")
            for r in records:
                console.print(f"  {r['type']} {r['name']} -> {r['content']}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _show_palette(palette: object) -> None:
    """Display palette colors in the console."""
    from thenine.core.brand import BrandPalette

    if not isinstance(palette, BrandPalette):
        return

    table = Table(title="Brand Palette")
    table.add_column("Role")
    table.add_column("Name")
    table.add_column("Hex")
    table.add_column("OKLCH")

    for color in palette.all_colors():
        table.add_row(color.purpose, color.name, color.hex, color.oklch_css)

    console.print(table)


if __name__ == "__main__":
    app()
