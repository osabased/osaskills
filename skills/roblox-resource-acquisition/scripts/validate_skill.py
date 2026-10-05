#!/usr/bin/env python3
"""Validate child contract 1, composed guidance and local links; no runtime claim."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import unquote, urlsplit

from _common import load_yaml
from _resource_contract import load_contract, within, url_identity


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    text = text.removeprefix("\ufeff").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed")
    data = load_yaml(text[4:end])
    if not isinstance(data, dict):
        raise ValueError("SKILL.md frontmatter must be a YAML mapping")
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError("frontmatter keys must be strings")
        if key != "metadata" and isinstance(value, (dict, list)):
            raise ValueError(f"frontmatter field {key!r} must be a scalar value")
        if isinstance(value, str):
            data[key] = value.strip()
    return data, text[end + 5:]


def unfenced(text: str) -> str:
    text = re.sub(r"<!--.*?(?:-->|$)", "", text, flags=re.S)
    result = []
    active = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            token = marker[1]
            if active is None:
                active = token
            elif token[0] == active[0] and len(token) >= len(active) and not marker[2].strip():
                active = None
            continue
        if active is None:
            result.append(line)
    return "\n".join(result)


def parse_sections(body: str) -> tuple[dict[str, str], Counter]:
    """Generic Markdown utility for parent/competitor routing, never child schema."""
    text = unfenced(body)
    matches = list(re.finditer(r"^## ([^\n]+)$", text, re.M))
    sections = {}
    counts = Counter(match[1].strip() for match in matches)
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.setdefault(match[1].strip(), text[match.end():end].strip())
    return sections, counts


def anchors(text: str) -> set[str]:
    found = set()
    counts = Counter()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", unfenced(text), re.M):
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).replace("_", "_")
        slug = re.sub(r"\s", "-", slug)
        suffix = "" if counts[slug] == 0 else f"-{counts[slug]}"
        found.add(slug + suffix)
        counts[slug] += 1
    return found


def local_links(root: Path, source: Path, text: str) -> list[tuple[Path, str]]:
    links = []
    for match in re.finditer(r"!?\[[^\]\n]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+['\"][^)]*)?\)", unfenced(text)):
        value = match[1] or match[2]
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme not in {"https", "http", "mailto"}:
                raise ValueError(f"unsupported guidance link scheme: {value}")
            continue
        relative = unquote(parsed.path)
        target = source if not relative else (source.parent / relative).resolve()
        if not target.is_relative_to(root.resolve()) or target == root.resolve():
            raise ValueError(f"local guidance link escapes package: {value}")
        if not target.is_file():
            raise ValueError(f"broken local guidance link in {source.relative_to(root)}: {value}")
        if parsed.fragment:
            if target.suffix != ".md" or unquote(parsed.fragment) not in anchors(target.read_text(encoding="utf-8-sig")):
                raise ValueError(f"missing local guidance anchor in {source.relative_to(root)}: {value}")
        links.append((target, parsed.fragment))
    return links


def validate_skill(root: Path) -> tuple[list[str], list[str]]:
    root = root.resolve()
    errors, warnings = [], []
    try:
        text = (root / "SKILL.md").read_text(encoding="utf-8-sig")
        metadata, body = parse_frontmatter(text)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], warnings
    fields = {"name", "description", "license", "compatibility", "allowed-tools", "metadata"}
    if set(metadata) - fields:
        errors.append("unsupported frontmatter fields: " + ", ".join(sorted(set(metadata) - fields)))
    name = metadata.get("name")
    description = metadata.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("frontmatter name must be lowercase kebab-case")
    elif len(name) > 64:
        errors.append("frontmatter name must be at most 64 characters")
    if name != root.name:
        errors.append("frontmatter name must match the generated skill directory name")
    if not isinstance(description, str) or not description:
        errors.append("frontmatter description must be a nonempty string")
    elif len(description) > 1024:
        errors.append("frontmatter description must be at most 1024 characters")
    for field in ("license", "allowed-tools"):
        if field in metadata and not isinstance(metadata[field], str):
            errors.append(f"frontmatter {field} must be a string")
    if "compatibility" in metadata and (not isinstance(metadata["compatibility"], str) or not 1 <= len(metadata["compatibility"]) <= 500):
        errors.append("frontmatter compatibility must be 1 to 500 characters")
    optional = metadata.get("metadata")
    if optional is not None and (not isinstance(optional, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in optional.items())):
        errors.append("frontmatter metadata keys and values must be strings")
    try:
        contract = load_contract(root)
        declared = {within(root, item["path"]) for item in contract["guidance"]["documents"]}
        reachable = {(root / "SKILL.md").resolve()}
        pending = list(reachable)
        while pending:
            source = pending.pop()
            content = source.read_text(encoding="utf-8-sig")
            if re.search(r"\b(?:TBD|TODO|RESOURCE-SLUG|VERSION/COMMIT/STATE)\b|^\s*[-*]?\s*\.\.\.\s*$", content, re.M):
                errors.append(f"unfinished scaffold in {source.relative_to(root)}")
            for target, _ in local_links(root, source, content):
                if target.suffix == ".md":
                    if target not in declared:
                        errors.append(f"linked guidance must be declared in resource.yaml: {target.relative_to(root)}")
                    if target not in reachable:
                        reachable.add(target)
                        pending.append(target)
        for target in declared - reachable:
            errors.append(f"declared guidance is unreachable from SKILL.md: {target.relative_to(root)}")
        if "resource.yaml" not in unfenced(body):
            errors.append("entrypoint must route to resource.yaml")
        if "child-usage.md" not in unfenced(body):
            errors.append("entrypoint must route to the installed parent's child-usage.md once per task")
        if not re.search(r"^#\s+\S", unfenced(body), re.M):
            errors.append("missing resource name as a level-1 heading")
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        errors.append(str(exc))
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated_skill_directory", type=Path)
    args = parser.parse_args(argv)
    errors, warnings = validate_skill(args.generated_skill_directory)
    for warning in warnings:
        print("WARN: " + warning)
    if errors:
        print("FAIL")
        for error in errors:
            print("- " + error)
        return 1
    print("PASS: structural generated-skill checks passed (resource-child contract 1)")
    print("NOTE: structural checks do not prove instructions, runtime behavior, or host routing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
