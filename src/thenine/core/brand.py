"""Brand domain models - immutable Pydantic models for the brand identity pipeline."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


class Industry(str, Enum):
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTH = "health"
    EDUCATION = "education"
    ECOMMERCE = "ecommerce"
    CREATIVE = "creative"
    FOOD = "food"
    TRAVEL = "travel"
    REAL_ESTATE = "real_estate"
    CONSULTING = "consulting"
    OTHER = "other"


class Mood(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    PLAYFUL = "playful"
    PROFESSIONAL = "professional"
    BOLD = "bold"
    MINIMAL = "minimal"
    LUXURY = "luxury"
    WARM = "warm"
    COOL = "cool"
    ENERGETIC = "energetic"


class BrandContact(BaseModel, frozen=True):
    """Contact information for the brand owner."""

    name: str = Field(max_length=100)
    title: str = Field(default="", max_length=100)
    email: str = Field(default="")
    phone: str = Field(default="", max_length=30)
    website: str = Field(default="")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class BrandInput(BaseModel, frozen=True):
    """Input data for brand generation."""

    name: str = Field(min_length=1, max_length=100, description="Project/company name")
    tagline: str = Field(default="", max_length=200, description="Short tagline or slogan")
    industry: str = Field(default="technology", description="Industry category")
    mood: str = Field(default="modern", description="Desired mood/tone")
    contact: BrandContact = Field(default_factory=lambda: BrandContact(name=""))
    domain: str = Field(default="", max_length=253, description="Domain name (e.g. acme.com)")
    description: str = Field(default="", max_length=1000, description="Brief project description")

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if v and not all(c.isalnum() or c in ".-" for c in v):
            raise ValueError("Domain contains invalid characters")
        return v.lower()

    @property
    def slug(self) -> str:
        return self.name.lower().replace(" ", "-").replace("_", "-")


class BrandColor(BaseModel, frozen=True):
    """A single color in the brand palette with OKLCH values."""

    name: str = Field(min_length=1, max_length=50)
    hex: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    oklch_l: float = Field(ge=0.0, le=1.0, description="OKLCH lightness")
    oklch_c: float = Field(ge=0.0, le=0.5, description="OKLCH chroma")
    oklch_h: float = Field(ge=0.0, le=360.0, description="OKLCH hue")
    purpose: str = Field(default="", description="Color role (primary, secondary, accent, etc.)")

    @property
    def oklch_css(self) -> str:
        return f"oklch({self.oklch_l:.3f} {self.oklch_c:.3f} {self.oklch_h:.1f})"

    @property
    def rgb(self) -> tuple[int, int, int]:
        h = self.hex.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class BrandPalette(BaseModel, frozen=True):
    """Complete 5-color brand palette."""

    primary: BrandColor
    secondary: BrandColor
    accent: BrandColor
    neutral_light: BrandColor
    neutral_dark: BrandColor

    def all_colors(self) -> list[BrandColor]:
        return [self.primary, self.secondary, self.accent, self.neutral_light, self.neutral_dark]

    def to_hex_dict(self) -> dict[str, str]:
        return {
            "primary": self.primary.hex,
            "secondary": self.secondary.hex,
            "accent": self.accent.hex,
            "neutral-light": self.neutral_light.hex,
            "neutral-dark": self.neutral_dark.hex,
        }


class FontSpec(BaseModel, frozen=True):
    """Specification for a single font."""

    family: str = Field(min_length=1, max_length=100)
    category: str = Field(default="sans-serif")
    weight: int = Field(default=400, ge=100, le=900)
    google_fonts_url: str = Field(default="")


class BrandTypography(BaseModel, frozen=True):
    """Typography system with heading, body, and mono fonts."""

    heading: FontSpec
    body: FontSpec
    mono: FontSpec = Field(
        default_factory=lambda: FontSpec(family="JetBrains Mono", category="monospace", weight=400)
    )


class BrandTokens(BaseModel, frozen=True):
    """Design tokens derived from palette and typography."""

    colors: dict[str, str] = Field(description="Color name -> hex value")
    fonts: dict[str, str] = Field(description="Font role -> font family")
    spacing: dict[str, str] = Field(
        default_factory=lambda: {
            "xs": "0.25rem",
            "sm": "0.5rem",
            "md": "1rem",
            "lg": "1.5rem",
            "xl": "2rem",
            "2xl": "3rem",
            "3xl": "4rem",
            "section": "6rem",
        }
    )
    radii: dict[str, str] = Field(
        default_factory=lambda: {
            "sm": "0.25rem",
            "md": "0.5rem",
            "lg": "1rem",
            "xl": "1.5rem",
            "full": "9999px",
        }
    )


class BrandPackage(BaseModel, frozen=True):
    """Complete brand package output."""

    input: BrandInput
    palette: BrandPalette
    typography: BrandTypography
    tokens: BrandTokens
    output_dir: str = Field(default="")

    @property
    def output_path(self) -> Path:
        return Path(self.output_dir) if self.output_dir else Path("output") / self.input.slug
