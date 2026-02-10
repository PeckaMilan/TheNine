"""3D business card generator using build123d."""

from __future__ import annotations

from pathlib import Path

from thenine.core.brand import BrandContact

# Card dimensions in mm
CARD_WIDTH = 85.0
CARD_HEIGHT = 55.0
CARD_THICKNESS = 2.0
CORNER_RADIUS = 2.0
EMBOSS_HEIGHT = 0.5
FONT_NAME = "Arial"


class ThreeDCardGenerator:
    """Generates 3D-printable business cards with embossed text."""

    def generate(
        self,
        brand_name: str,
        contact: BrandContact,
        output_dir: Path,
    ) -> dict[str, Path]:
        """Generate 3D business card in STL and 3MF formats."""
        output_dir.mkdir(parents=True, exist_ok=True)

        part = self._build_card(brand_name, contact)

        stl_path = output_dir / "business-card.stl"
        threemf_path = output_dir / "business-card.3mf"

        from build123d import export_stl

        export_stl(part, str(stl_path))

        self._export_3mf_via_lib3mf(stl_path, threemf_path)

        paths = {"stl": stl_path}
        if threemf_path.exists():
            paths["3mf"] = threemf_path

        return paths

    def _build_card(self, brand_name: str, contact: BrandContact) -> object:
        """Build the 3D card geometry with embossed text."""
        from build123d import (
            Align,
            Box,
            BuildPart,
            BuildSketch,
            Mode,
            Plane,
            RectangleRounded,
            Text,
            extrude,
            fillet,
        )

        with BuildPart() as card:
            # Base card with rounded corners
            with BuildSketch() as base:
                RectangleRounded(CARD_WIDTH, CARD_HEIGHT, CORNER_RADIUS)
            extrude(amount=CARD_THICKNESS)

            # Emboss brand name (top area)
            try:
                with BuildSketch(Plane.XY.offset(CARD_THICKNESS)) as name_sk:
                    Text(
                        brand_name,
                        font_size=10,
                        font=FONT_NAME,
                        align=(Align.CENTER, Align.CENTER),
                    )
                extrude(amount=EMBOSS_HEIGHT)
            except Exception:
                pass

            # Emboss contact name (below brand)
            if contact.name:
                try:
                    with BuildSketch(
                        Plane.XY.offset(CARD_THICKNESS).shift_origin((0, -8, 0))
                    ) as contact_sk:
                        Text(
                            contact.name,
                            font_size=6,
                            font=FONT_NAME,
                            align=(Align.CENTER, Align.CENTER),
                        )
                    extrude(amount=EMBOSS_HEIGHT)
                except Exception:
                    pass

            # Emboss contact title
            if contact.title:
                try:
                    with BuildSketch(
                        Plane.XY.offset(CARD_THICKNESS).shift_origin((0, -14, 0))
                    ) as title_sk:
                        Text(
                            contact.title,
                            font_size=4,
                            font=FONT_NAME,
                            align=(Align.CENTER, Align.CENTER),
                        )
                    extrude(amount=EMBOSS_HEIGHT)
                except Exception:
                    pass

        return card.part

    def _export_3mf_via_lib3mf(self, stl_path: Path, threemf_path: Path) -> Path:
        """Export 3MF using lib3mf (bundled with build123d)."""
        import trimesh
        from lib3mf import Lib3MF

        mesh = trimesh.load(str(stl_path))

        wrapper = Lib3MF.Wrapper()
        model = wrapper.CreateModel()
        mesh_obj = model.AddMeshObject()
        mesh_obj.SetName("business-card")

        vertices = []
        for v in mesh.vertices:
            pos = Lib3MF.Position()
            pos.Coordinates[0] = float(v[0])
            pos.Coordinates[1] = float(v[1])
            pos.Coordinates[2] = float(v[2])
            vertices.append(pos)

        triangles = []
        for f in mesh.faces:
            tri = Lib3MF.Triangle()
            tri.Indices[0] = int(f[0])
            tri.Indices[1] = int(f[1])
            tri.Indices[2] = int(f[2])
            triangles.append(tri)

        mesh_obj.SetGeometry(vertices, triangles)
        model.AddBuildItem(mesh_obj, wrapper.GetIdentityTransform())

        writer = model.QueryWriter("3mf")
        writer.WriteToFile(str(threemf_path))
        return threemf_path

    def validate(self, stl_path: Path) -> dict[str, object]:
        """Validate the generated STL file for printability."""
        import trimesh

        mesh = trimesh.load(str(stl_path))
        return {
            "is_watertight": mesh.is_watertight,
            "is_volume": mesh.is_volume,
            "volume_mm3": round(float(mesh.volume), 2),
            "surface_area_mm2": round(float(mesh.area), 2),
            "bounds_mm": mesh.bounds.tolist(),
        }
