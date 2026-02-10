"""Cloudflare DNS management via official Python SDK."""

from __future__ import annotations

import os
from typing import Any


class DNSManager:
    """Manages DNS records via Cloudflare API."""

    def __init__(self, api_token: str | None = None, account_id: str | None = None) -> None:
        self._api_token = api_token or os.environ.get("CLOUDFLARE_API_TOKEN", "")
        self._account_id = account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            from cloudflare import Cloudflare

            self._client = Cloudflare(api_token=self._api_token)
        return self._client

    def get_zone_id(self, domain: str) -> str:
        """Get the zone ID for a domain."""
        zones = self.client.zones.list(name=domain)
        results = list(zones)
        if not results:
            raise ValueError(f"No zone found for domain: {domain}")
        return results[0].id

    def list_records(self, zone_id: str) -> list[dict[str, Any]]:
        """List all DNS records for a zone."""
        records = self.client.dns.records.list(zone_id=zone_id)
        return [
            {
                "id": r.id,
                "type": r.type,
                "name": r.name,
                "content": r.content,
                "proxied": r.proxied,
                "ttl": r.ttl,
            }
            for r in records
        ]

    def create_record(
        self,
        zone_id: str,
        record_type: str,
        name: str,
        content: str,
        proxied: bool = True,
        ttl: int = 1,
    ) -> dict[str, Any]:
        """Create a DNS record."""
        record = self.client.dns.records.create(
            zone_id=zone_id,
            type=record_type,
            name=name,
            content=content,
            proxied=proxied,
            ttl=ttl,
        )
        return {"id": record.id, "type": record.type, "name": record.name, "content": record.content}

    def setup_pages_dns(self, zone_id: str, domain: str, pages_project: str) -> list[dict[str, Any]]:
        """Set up DNS records for Cloudflare Pages deployment.

        Creates a CNAME record pointing the domain to the Pages project.
        """
        pages_domain = f"{pages_project}.pages.dev"
        records = []

        # Root domain CNAME
        records.append(
            self.create_record(
                zone_id=zone_id,
                record_type="CNAME",
                name=domain,
                content=pages_domain,
                proxied=True,
            )
        )

        # www subdomain CNAME
        records.append(
            self.create_record(
                zone_id=zone_id,
                record_type="CNAME",
                name=f"www.{domain}",
                content=pages_domain,
                proxied=True,
            )
        )

        return records

    def delete_record(self, zone_id: str, record_id: str) -> None:
        """Delete a DNS record."""
        self.client.dns.records.delete(zone_id=zone_id, dns_record_id=record_id)
