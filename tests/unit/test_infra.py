"""Tests for infrastructure modules (Cloudflare DNS, Pages, Google Fonts)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestDNSManager:
    def test_init_with_token(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        manager = DNSManager(api_token="test-token", account_id="acc-123")
        assert manager._api_token == "test-token"
        assert manager._account_id == "acc-123"

    def test_init_from_env(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        with patch.dict("os.environ", {"CLOUDFLARE_API_TOKEN": "env-token", "CLOUDFLARE_ACCOUNT_ID": "env-acc"}):
            manager = DNSManager()
            assert manager._api_token == "env-token"
            assert manager._account_id == "env-acc"

    def test_client_lazy_init(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        manager = DNSManager(api_token="test")
        assert manager._client is None

        mock_cf = MagicMock()
        with patch.dict("sys.modules", {"cloudflare": MagicMock(Cloudflare=mock_cf)}):
            _ = manager.client
            mock_cf.assert_called_once_with(api_token="test")

    def test_get_zone_id(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        manager = DNSManager(api_token="test")
        mock_zone = MagicMock()
        mock_zone.id = "zone-456"
        mock_client = MagicMock()
        mock_client.zones.list.return_value = [mock_zone]
        manager._client = mock_client

        result = manager.get_zone_id("example.com")
        assert result == "zone-456"
        mock_client.zones.list.assert_called_once_with(name="example.com")

    def test_get_zone_id_not_found(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        manager = DNSManager(api_token="test")
        mock_client = MagicMock()
        mock_client.zones.list.return_value = []
        manager._client = mock_client

        with pytest.raises(ValueError, match="No zone found"):
            manager.get_zone_id("nonexistent.com")

    def test_list_records(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        manager = DNSManager(api_token="test")
        mock_record = MagicMock()
        mock_record.id = "rec-1"
        mock_record.type = "A"
        mock_record.name = "example.com"
        mock_record.content = "1.2.3.4"
        mock_record.proxied = True
        mock_record.ttl = 1

        mock_client = MagicMock()
        mock_client.dns.records.list.return_value = [mock_record]
        manager._client = mock_client

        records = manager.list_records("zone-456")
        assert len(records) == 1
        assert records[0]["type"] == "A"
        assert records[0]["content"] == "1.2.3.4"

    def test_create_record(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        manager = DNSManager(api_token="test")
        mock_result = MagicMock()
        mock_result.id = "rec-new"
        mock_result.type = "CNAME"
        mock_result.name = "www.example.com"
        mock_result.content = "example.pages.dev"

        mock_client = MagicMock()
        mock_client.dns.records.create.return_value = mock_result
        manager._client = mock_client

        record = manager.create_record("zone-456", "CNAME", "www.example.com", "example.pages.dev")
        assert record["id"] == "rec-new"
        assert record["type"] == "CNAME"

    def test_setup_pages_dns(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        manager = DNSManager(api_token="test")
        mock_result = MagicMock()
        mock_result.id = "rec-1"
        mock_result.type = "CNAME"
        mock_result.name = "example.com"
        mock_result.content = "mysite.pages.dev"

        mock_client = MagicMock()
        mock_client.dns.records.create.return_value = mock_result
        manager._client = mock_client

        records = manager.setup_pages_dns("zone-456", "example.com", "mysite")
        assert len(records) == 2
        # Should create root + www records
        calls = mock_client.dns.records.create.call_args_list
        assert len(calls) == 2

    def test_delete_record(self) -> None:
        from thenine.infra.cloudflare_dns import DNSManager

        manager = DNSManager(api_token="test")
        mock_client = MagicMock()
        manager._client = mock_client

        manager.delete_record("zone-456", "rec-1")
        mock_client.dns.records.delete.assert_called_once_with(zone_id="zone-456", dns_record_id="rec-1")


class TestPagesDeployer:
    def test_init(self) -> None:
        from thenine.infra.cloudflare_pages import PagesDeployer

        deployer = PagesDeployer("my-project")
        assert deployer._project_name == "my-project"

    def test_deploy_missing_dist(self, tmp_path: Path) -> None:
        from thenine.infra.cloudflare_pages import PagesDeployer

        deployer = PagesDeployer("my-project")
        with pytest.raises(FileNotFoundError, match="Build directory not found"):
            deployer.deploy(tmp_path / "nonexistent")

    @patch("subprocess.run")
    def test_deploy_success(self, mock_run, tmp_path: Path) -> None:
        from thenine.infra.cloudflare_pages import PagesDeployer

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Deploying...\nhttps://mysite-abc.mysite.pages.dev\nDone!",
            stderr="",
        )

        deployer = PagesDeployer("mysite")
        url = deployer.deploy(dist_dir)
        assert "pages.dev" in url
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_deploy_failure(self, mock_run, tmp_path: Path) -> None:
        from thenine.infra.cloudflare_pages import PagesDeployer

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Authentication failed",
        )

        deployer = PagesDeployer("mysite")
        with pytest.raises(RuntimeError, match="Wrangler deploy failed"):
            deployer.deploy(dist_dir)

    @patch("subprocess.run")
    def test_deploy_no_url_in_output(self, mock_run, tmp_path: Path) -> None:
        from thenine.infra.cloudflare_pages import PagesDeployer

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        mock_run.return_value = MagicMock(returncode=0, stdout="Deployed successfully!", stderr="")

        deployer = PagesDeployer("mysite")
        url = deployer.deploy(dist_dir)
        assert url == "https://mysite.pages.dev"

    @patch("subprocess.run")
    def test_create_project(self, mock_run) -> None:
        from thenine.infra.cloudflare_pages import PagesDeployer

        deployer = PagesDeployer("mysite")
        deployer.create_project()
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "create" in cmd
        assert "mysite" in cmd


class TestGoogleFontsClient:
    def test_init_with_key(self) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        client = GoogleFontsClient(api_key="test-key")
        assert client._api_key == "test-key"

    def test_init_from_env(self) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        with patch.dict("os.environ", {"GOOGLE_FONTS_API_KEY": "env-key"}):
            client = GoogleFontsClient()
            assert client._api_key == "env-key"

    def test_get_font_no_api_key(self) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        client = GoogleFontsClient(api_key="")
        assert client.get_font("Inter") is None

    @patch("httpx.get")
    def test_get_font_success(self, mock_get) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"family": "Inter", "variants": ["regular", "700"]}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        client = GoogleFontsClient(api_key="test-key")
        result = client.get_font("Inter")
        assert result is not None
        assert result["family"] == "Inter"

    @patch("httpx.get")
    def test_get_font_not_found(self, mock_get) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        client = GoogleFontsClient(api_key="test-key")
        result = client.get_font("NonExistentFont")
        assert result is None

    @patch("httpx.get")
    def test_get_font_error(self, mock_get) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        mock_get.side_effect = Exception("Connection error")

        client = GoogleFontsClient(api_key="test-key")
        result = client.get_font("Inter")
        assert result is None

    def test_get_css_url_single_family(self) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        client = GoogleFontsClient(api_key="test")
        url = client.get_css_url([("Inter", [400, 700])])
        assert "family=Inter:wght@400;700" in url
        assert "display=swap" in url

    def test_get_css_url_multiple_families(self) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        client = GoogleFontsClient(api_key="test")
        url = client.get_css_url([
            ("Inter", [400, 700]),
            ("Source Sans 3", [400]),
        ])
        assert "family=Inter:wght@400;700" in url
        assert "family=Source+Sans+3:wght@400" in url
        assert "&" in url

    def test_get_css_url_weights_sorted(self) -> None:
        from thenine.infra.google_fonts import GoogleFontsClient

        client = GoogleFontsClient(api_key="test")
        url = client.get_css_url([("Inter", [700, 400, 300])])
        assert "wght@300;400;700" in url
