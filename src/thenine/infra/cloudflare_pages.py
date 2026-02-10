"""Cloudflare Pages deployment via Wrangler CLI."""

from __future__ import annotations

import subprocess
from pathlib import Path


class PagesDeployer:
    """Deploys static sites to Cloudflare Pages via Wrangler CLI."""

    def __init__(self, project_name: str) -> None:
        self._project_name = project_name

    def deploy(self, dist_dir: Path, branch: str = "production") -> str:
        """Deploy the built site to Cloudflare Pages.

        Returns the deployment URL.
        """
        if not dist_dir.exists():
            raise FileNotFoundError(f"Build directory not found: {dist_dir}")

        cmd = [
            "npx",
            "wrangler",
            "pages",
            "deploy",
            str(dist_dir),
            f"--project-name={self._project_name}",
            f"--branch={branch}",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            shell=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Wrangler deploy failed:\n{result.stderr}")

        # Extract URL from output
        for line in result.stdout.splitlines():
            if "https://" in line and ".pages.dev" in line:
                return line.strip()

        return f"https://{self._project_name}.pages.dev"

    def create_project(self) -> None:
        """Create the Cloudflare Pages project if it doesn't exist."""
        cmd = [
            "npx",
            "wrangler",
            "pages",
            "project",
            "create",
            self._project_name,
            "--production-branch=production",
        ]

        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            shell=True,
        )
