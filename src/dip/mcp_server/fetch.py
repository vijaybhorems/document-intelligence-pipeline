"""Fetch a document from a URL an agent supplied, without becoming an SSRF proxy (SPEC §12.2.5).

The server runs inside Google Cloud, next to a metadata server that hands out its
service account's tokens (``169.254.169.254``). So:

1. ``https`` on port 443 only, no credentials in the URL.
2. Resolve the host, and require **every** address to be public: no loopback,
   private, link-local, multicast or reserved ranges. One bad address rejects all.
3. Connect to the address that was checked, not to the name again. A second DNS
   answer can't swap in an internal address (DNS rebinding). TLS still verifies
   the certificate against the hostname (``sni_hostname``).
4. Follow at most ``MAX_REDIRECTS`` redirects, re-checking each hop from step 1.
5. Stream with a byte cap; the content type is sniffed later, by ``uploads.check``.
"""

import ipaddress
import socket
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import httpx

MAX_REDIRECTS = 3
TIMEOUT_S = 20.0

Resolver = Callable[[str], list[str]]


class FetchError(ValueError):
    """The URL is not allowed or the download failed; the message is safe to show."""


def system_resolver(host: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise FetchError(f"cannot resolve {host}") from exc
    return sorted({str(info[4][0]) for info in infos})


def _public(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped  # ::ffff:10.0.0.1 is 10.0.0.1
    return ip.is_global and not ip.is_multicast


@dataclass(frozen=True)
class Target:
    url: str
    host: str
    address: str


def check_url(url: str, resolve: Resolver = system_resolver) -> Target:
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise FetchError("only https:// URLs are accepted")
    if parts.username or parts.password:
        raise FetchError("URLs with credentials are not accepted")
    if parts.port not in (None, 443):
        raise FetchError("only the default https port (443) is accepted")
    host = parts.hostname
    if not host:
        raise FetchError("URL has no host")
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    addresses = [str(literal)] if literal else resolve(host)
    if not addresses:
        raise FetchError(f"cannot resolve {host}")
    blocked = [a for a in addresses if not _public(a)]
    if blocked:
        raise FetchError(f"{host} resolves to a non-public address; not fetched")
    return Target(url=url, host=host, address=addresses[0])


def fetch(
    url: str,
    max_bytes: int,
    resolve: Resolver = system_resolver,
    transport: httpx.BaseTransport | None = None,
) -> tuple[bytes, str]:
    """Download ``url`` under the rules above. Returns (bytes, filename)."""
    with httpx.Client(transport=transport, timeout=TIMEOUT_S, follow_redirects=False) as client:
        for _ in range(MAX_REDIRECTS + 1):
            target = check_url(url, resolve)
            parts = urlsplit(target.url)
            address = f"[{target.address}]" if ":" in target.address else target.address
            pinned = parts._replace(netloc=address).geturl()
            request = client.build_request(
                "GET",
                pinned,
                headers={"Host": target.host, "User-Agent": "dip-mcp/1"},
                extensions={"sni_hostname": target.host},
            )
            response = client.send(request, stream=True)
            try:
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        raise FetchError("redirect without a Location header")
                    url = urljoin(target.url, location)
                    continue
                if response.status_code != 200:
                    raise FetchError(f"download failed: HTTP {response.status_code}")
                declared = int(response.headers.get("content-length") or 0)
                if declared > max_bytes:
                    raise FetchError(f"document is larger than {max_bytes // 2**20} MB")
                chunks, size = [], 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > max_bytes:
                        raise FetchError(f"document is larger than {max_bytes // 2**20} MB")
                    chunks.append(chunk)
                name = parts.path.rsplit("/", 1)[-1] or "document"
                return b"".join(chunks), name
            except httpx.HTTPError as exc:
                raise FetchError(f"download failed: {type(exc).__name__}") from exc
            finally:
                response.close()
    raise FetchError(f"more than {MAX_REDIRECTS} redirects")
