"""Tests for 3D business card generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from thenine.core.brand import BrandContact
from thenine.generators.card_3d import ThreeDCardGenerator


class TestThreeDCardGenerator:
    def test_generate_creates_stl(self, tmp_output: Path) -> None:
        gen = ThreeDCardGenerator()
        contact = BrandContact(
            name="John Doe",
            title="CEO",
            email="john@acme.com",
        )
        paths = gen.generate("Acme Corp", contact, tmp_output)
        assert "stl" in paths
        assert paths["stl"].exists()
        assert paths["stl"].suffix == ".stl"
        assert paths["stl"].stat().st_size > 0

    def test_validate_stl(self, tmp_output: Path) -> None:
        gen = ThreeDCardGenerator()
        contact = BrandContact(name="John Doe")
        paths = gen.generate("Test Brand", contact, tmp_output)
        validation = gen.validate(paths["stl"])
        assert validation["is_watertight"] is True
        assert validation["is_volume"] is True
        assert validation["volume_mm3"] > 0

    def test_card_dimensions(self, tmp_output: Path) -> None:
        gen = ThreeDCardGenerator()
        contact = BrandContact(name="John Doe")
        paths = gen.generate("Test", contact, tmp_output)
        validation = gen.validate(paths["stl"])
        bounds = validation["bounds_mm"]
        # Card should be approximately 85x55x2.5mm
        width = bounds[1][0] - bounds[0][0]
        height = bounds[1][1] - bounds[0][1]
        thickness = bounds[1][2] - bounds[0][2]
        assert 80 < width < 90
        assert 50 < height < 60
        assert 1.5 < thickness < 4.0

    def test_minimal_contact(self, tmp_output: Path) -> None:
        gen = ThreeDCardGenerator()
        contact = BrandContact(name="")
        paths = gen.generate("Brand", contact, tmp_output)
        assert paths["stl"].exists()
