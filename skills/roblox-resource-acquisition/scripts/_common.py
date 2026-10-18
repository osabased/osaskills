#!/usr/bin/env python3
"""Shared mechanics for the roblox-resource-acquisition scripts.

YAML loading with duplicate-key rejection, URL host validation and
version-evidence detection. Policy decisions and error wording stay in the
individual scripts.

PyYAML is a hard requirement. A single parser everywhere guarantees that the
same resource.yaml or SKILL.md frontmatter receives the same verdict in every
environment; the previous optional-PyYAML fallback parser could disagree with
PyYAML on inputs such as empty scalars, octal-like integers, and duplicate
keys, letting a file pass validation in one environment and fail in another.
"""
from __future__ import annotations

import ipaddress
import os
import re
import sys
from datetime import date
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised via subprocess in tests
    script = os.path.basename(sys.argv[0]) or "<name>.py"
    print(
        f"ERROR: PyYAML is required to run {script}. "
        "Install it with: uv pip install -r requirements.txt (in the skill folder, beside scripts/) "
        "in the selected environment, or run: "
        f'uv run --no-project --python ">=3.11" --with pyyaml python scripts/{script}',
        file=sys.stderr,
    )
    sys.exit(2)


class UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys instead of silently
    keeping the last one. Keys are compared after resolution, so aliases of
    the same value (e.g. ``yes`` and ``true``) collide as duplicates."""


def _construct_unique_mapping(loader: Any, node: Any, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_yaml(text: str) -> Any:
    """Parse YAML with duplicate-key rejection; raise ValueError on failure."""
    try:
        return yaml.load(text, Loader=UniqueKeyLoader)
    except Exception as exc:
        raise ValueError(f"invalid YAML: {exc}") from exc


SENSITIVE_QUERY_RE = re.compile(
    r"(?:"
    r"(?:^|[_-])(?:access[_-]?key|api[_-]?key|auth(?:orization)?|credential|password|passwd|secret|signature|sig|token)(?:$|[_-])"
    r"|(?:api|access|auth|client|private|refresh|session|bearer)[_-]?(?:token|key|secret|credential)(?:$|[_-])"
    r"|secret[_-]?key(?:$|[_-])"
    r")",
    re.I,
)

IMMUTABLE_VERSION_ID_RE = re.compile(
    r"(?:"
    r"\bv\d+(?:(?:[._-]\d+)+(?:[-+][0-9A-Za-z.-]+)?)?\b"
    r"|\b\d+(?:[._-]\d+)+(?:[-+][0-9A-Za-z.-]+)?\b"
    r"|\b[0-9a-f]{7,64}\b"
    r")",
    re.I,
)

EXPLICIT_IMMUTABLE_REF_RE = re.compile(
    r"\b(?:tag|release|version|commit|revision|rev|build|asset version)\b"
    r"\s*(?:[:=#@]|is\b)?\s*([A-Za-z0-9][A-Za-z0-9._/-]{0,127})\b",
    re.I,
)

SOURCE_STATE_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def validated_url_host(parsed: Any) -> str | None:
    """Return a normalized hostname when URL authority syntax is valid."""
    try:
        host = parsed.hostname
        # Accessing .port validates its numeric/range syntax.
        _ = parsed.port
    except ValueError:
        return None
    if not host or re.search(r"[\s\x00-\x1f\x7f]", host) or "%" in host:
        return None
    host = host.rstrip(".")
    if not host:
        return None
    if ":" in host:
        try:
            ipaddress.ip_address(host)
        except ValueError:
            return None
        return host.lower()
    try:
        ascii_host = host.encode("idna").decode("ascii")
    except UnicodeError:
        return None
    if len(ascii_host) > 253:
        return None
    labels = ascii_host.split(".")
    if any(
        not label
        or len(label) > 63
        or label.startswith("-")
        or label.endswith("-")
        or not re.fullmatch(r"[A-Za-z0-9-]+", label)
        for label in labels
    ):
        return None
    return ascii_host.lower()


def has_immutable_version_evidence(value: str) -> bool:
    """Accept an immutable-looking ID, named reference, or valid dated source state."""
    for raw_date in SOURCE_STATE_DATE_RE.findall(value):
        try:
            source_date = date.fromisoformat(raw_date)
        except ValueError:
            continue
        if source_date <= date.today():
            return True

    # Date-shaped tokens can resemble numeric release IDs. Mask them before
    # checking version identifiers so malformed/future dates cannot satisfy a
    # release-number branch by accident.
    without_dates = SOURCE_STATE_DATE_RE.sub(" ", value)
    if IMMUTABLE_VERSION_ID_RE.search(without_dates):
        return True

    explicit = EXPLICIT_IMMUTABLE_REF_RE.search(without_dates)
    if not explicit:
        return False
    identifier = explicit.group(1).strip().lower()
    return identifier not in {
        "latest", "current", "stable", "head", "main", "master", "trunk",
        "nightly", "rolling", "dev", "development", "unknown", "tbd", "none",
        "not", "unavailable", "unspecified", "n/a", "na", "not-available",
        "not_available", "not-applicable", "not_applicable",
    }

