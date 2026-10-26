import httpx
import pytest

from dip.mcp_server.fetch import FetchError, check_url, fetch

PUBLIC = "93.184.215.14"


def resolver(table: dict[str, list[str]]):
    return lambda host: table[host]


@pytest.mark.parametrize(
    ("url", "addresses", "reason"),
    [
        ("http://example.com/a.pdf", [PUBLIC], "only https"),
        ("https://user:pw@example.com/a.pdf", [PUBLIC], "credentials"),
        ("https://example.com:8443/a.pdf", [PUBLIC], "port"),
        ("https://169.254.169.254/computeMetadata/v1/", [], "non-public"),  # metadata server
        ("https://metadata.google.internal/x", ["169.254.169.254"], "non-public"),
        ("https://localhost/a.pdf", ["127.0.0.1"], "non-public"),
        ("https://intranet.corp/a.pdf", ["10.1.2.3"], "non-public"),
        ("https://mixed.example/a.pdf", [PUBLIC, "192.168.1.5"], "non-public"),  # any bad = all bad
        ("https://v6.example/a.pdf", ["::ffff:10.0.0.1"], "non-public"),  # IPv4-mapped
        ("https://[::1]/a.pdf", [], "non-public"),
    ],
)
def test_rejects(url: str, addresses: list[str], reason: str) -> None:
    host = httpx.URL(url).host
    with pytest.raises(FetchError, match=reason):
        check_url(url, resolver({host: addresses}))


def test_connects_to_the_checked_address_with_the_real_hostname() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, content=b"%PDF-1.4 ...")

    data, name = fetch(
        "https://example.com/files/c.pdf",
        1000,
        resolver({"example.com": [PUBLIC]}),
        httpx.MockTransport(handler),
    )
    assert (data, name) == (b"%PDF-1.4 ...", "c.pdf")
    assert seen[0].url.host == PUBLIC  # pinned: no second DNS lookup to rebind
    assert seen[0].headers["host"] == "example.com"
    assert seen[0].extensions["sni_hostname"] == "example.com"  # TLS checks the real name


def test_redirects_are_rechecked_at_every_hop() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "https://internal.example/secret"})

    table = {"example.com": [PUBLIC], "internal.example": ["10.0.0.7"]}
    with pytest.raises(FetchError, match="non-public"):
        fetch("https://example.com/a.pdf", 1000, resolver(table), httpx.MockTransport(handler))


def test_redirect_loops_stop() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(301, headers={"location": "/again"})

    with pytest.raises(FetchError, match="redirects"):
        fetch(
            "https://example.com/a.pdf",
            1000,
            resolver({"example.com": [PUBLIC]}),
            httpx.MockTransport(handler),
        )


def test_size_cap_holds_even_when_the_server_lies_about_length() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-length": "10"}, content=b"x" * 5000)

    with pytest.raises(FetchError, match="larger"):
        fetch(
            "https://example.com/a.pdf",
            1000,
            resolver({"example.com": [PUBLIC]}),
            httpx.MockTransport(handler),
        )
