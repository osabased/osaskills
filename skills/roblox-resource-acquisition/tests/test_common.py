"""Unit tests for the shared mechanics in scripts/_common.py."""
from urllib.parse import urlparse

import pytest


# --- YAML loading / duplicate keys -----------------------------------------

def test_duplicate_key_rejected(common):
    with pytest.raises(ValueError, match="duplicate key"):
        common.load_yaml("a: 1\na: 2\n")


def test_resolved_alias_keys_collide(common):
    # `yes` and `true` both resolve to boolean True; the raw-string comparison
    # in the old fallback parser missed this collision.
    with pytest.raises(ValueError, match="duplicate key"):
        common.load_yaml("yes: 1\ntrue: 2\n")


def test_block_scalars_parse(common):
    loaded = common.load_yaml("notes: |\n  line one\n  line two\n")
    assert loaded == {"notes": "line one\nline two\n"}


# --- URL host validation -----------------------------------------------------

@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://devforum.roblox.com/t/x/1", "devforum.roblox.com"),
        ("https://devforum.roblox.com./t/x/1", "devforum.roblox.com"),  # trailing dot
        ("https://EXAMPLE.test/page", "example.test"),
        ("https://[::1]/x", "::1"),
        ("https://münchen.example/x", "xn--mnchen-3ya.example"),
    ],
)
def test_validated_url_host_accepts(common, url, expected):
    assert common.validated_url_host(urlparse(url)) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://exa%6Dple.test/x",  # percent-encoded host
        "https://-bad.example/x",  # leading hyphen label
        "https://host:99999/x",  # out-of-range port
        "https://" + "a" * 300 + ".test/",  # host too long
    ],
)
def test_validated_url_host_rejects(common, url):
    assert common.validated_url_host(urlparse(url)) is None


# --- Version evidence ----------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        "v1.2.3",
        "4.0.0",
        "a3f9c21bd44",  # abbreviated commit hash
        "source state 2024-06-01",  # dated source state
        "tag rc-4-final",
    ],
)
def test_immutable_version_evidence_accepts(common, value):
    assert common.has_immutable_version_evidence(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "latest",
        "main",
        "tag latest",  # explicit ref to a volatile name
        "2099-13-45",  # date-shaped but invalid; masked before the ID check
        "banana-state",  # bare prose, no explicit ref kind
    ],
)
def test_immutable_version_evidence_rejects(common, value):
    assert common.has_immutable_version_evidence(value) is False
