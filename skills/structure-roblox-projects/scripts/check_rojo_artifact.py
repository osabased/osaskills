#!/usr/bin/env python3
"""Assert structural invariants in a Rojo sourcemap and text place build."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ArtifactView:
    paths: tuple[str, ...]
    classes: Counter[str]


def _join_path(parent: str, name: str) -> str:
    clean_name = name.replace("\\", "/").strip("/")
    return f"{parent}/{clean_name}" if parent and clean_name else clean_name or parent


def _normalize_assertion_path(path: str) -> str:
    return "/".join(part for part in path.replace("\\", "/").split("/") if part)


def read_sourcemap(path: Path) -> ArtifactView:
    with path.open("r", encoding="utf-8") as stream:
        root = json.load(stream)

    paths: list[str] = []
    classes: Counter[str] = Counter()

    def visit(node: object, parent: str, include_path: bool = True) -> None:
        if not isinstance(node, dict):
            raise ValueError("sourcemap nodes must be JSON objects")
        name = node.get("name")
        class_name = node.get("className")
        if not isinstance(name, str) or not isinstance(class_name, str):
            raise ValueError("each sourcemap node must have string name and className fields")

        current = _join_path(parent, name) if include_path else parent
        if include_path:
            paths.append(current)
        classes[class_name] += 1

        children = node.get("children", [])
        if not isinstance(children, list):
            raise ValueError("sourcemap children must be a JSON array")
        for child in children:
            visit(child, current)

    root_is_data_model = isinstance(root, dict) and root.get("className") == "DataModel"
    visit(root, "", include_path=not root_is_data_model)
    return ArtifactView(tuple(paths), classes)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _rbxlx_item_name(item: ET.Element, class_name: str) -> str:
    for child in item:
        if _local_name(child.tag) != "Properties":
            continue
        for prop in child:
            if prop.attrib.get("name") == "Name" and prop.text:
                return prop.text
    return class_name


def read_rbxlx(path: Path) -> ArtifactView:
    root = ET.parse(path).getroot()
    paths: list[str] = []
    classes: Counter[str] = Counter()

    def visit(item: ET.Element, parent: str) -> None:
        class_name = item.attrib.get("class")
        if not class_name:
            raise ValueError("each rbxlx Item must have a class attribute")
        current = _join_path(parent, _rbxlx_item_name(item, class_name))
        paths.append(current)
        classes[class_name] += 1
        for child in item:
            if _local_name(child.tag) == "Item":
                visit(child, current)

    top_items = [child for child in root if _local_name(child.tag) == "Item"]
    if not top_items:
        raise ValueError("rbxlx contains no top-level Item")
    for item in top_items:
        if item.attrib.get("class") == "DataModel":
            classes["DataModel"] += 1
            for child in item:
                if _local_name(child.tag) == "Item":
                    visit(child, "")
        else:
            visit(item, "")
    return ArtifactView(tuple(paths), classes)


def _contains_fragment(paths: Iterable[str], fragment: str) -> bool:
    normalized = fragment.replace("\\", "/").strip("/")
    return any(normalized in path for path in paths)


def check_artifacts(
    artifacts: dict[str, ArtifactView],
    *,
    required_paths: Sequence[str] = (),
    required_fragments: Sequence[str] = (),
    forbidden_fragments: Sequence[str] = (),
    singleton_classes: Sequence[str] = (),
) -> list[str]:
    failures: list[str] = []
    for artifact_name, artifact in artifacts.items():
        for required_path in required_paths:
            normalized_path = _normalize_assertion_path(required_path)
            if normalized_path not in artifact.paths:
                failures.append(
                    f"{artifact_name}: required DataModel-relative path is missing: "
                    f"{normalized_path!r}"
                )
        for fragment in required_fragments:
            if not _contains_fragment(artifact.paths, fragment):
                failures.append(f"{artifact_name}: required path fragment is missing: {fragment!r}")
        for fragment in forbidden_fragments:
            if _contains_fragment(artifact.paths, fragment):
                failures.append(f"{artifact_name}: forbidden path fragment is present: {fragment!r}")
        for class_name in singleton_classes:
            count = artifact.classes[class_name]
            if count != 1:
                failures.append(
                    f"{artifact_name}: expected exactly one {class_name}, found {count}"
                )
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check matching invariants in a Rojo sourcemap and text .rbxlx build."
    )
    parser.add_argument("--sourcemap", required=True, type=Path)
    parser.add_argument("--place", required=True, type=Path, help="Text .rbxlx place build")
    parser.add_argument("--label", default="artifact")
    parser.add_argument(
        "--require-path",
        action="append",
        default=[],
        help=(
            "Exact DataModel-relative path required in both artifacts. A non-DataModel "
            "sourcemap root is retained as the first path segment; repeat as needed"
        ),
    )
    parser.add_argument(
        "--require-path-fragment",
        action="append",
        default=[],
        help="Path fragment that must occur in both artifacts; repeat as needed",
    )
    parser.add_argument(
        "--forbid-path-fragment",
        action="append",
        default=[],
        help="Path fragment that must be absent from both artifacts; repeat as needed",
    )
    parser.add_argument(
        "--singleton-class",
        action="append",
        default=[],
        help="Roblox class that must occur exactly once in both artifacts; repeat as needed",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    invariant_values = (
        args.require_path,
        args.require_path_fragment,
        args.forbid_path_fragment,
        args.singleton_class,
    )
    if not any(invariant_values):
        print(f"{args.label}: at least one artifact invariant is required", file=sys.stderr)
        return 2
    for option_name, values in (
        ("--require-path", args.require_path),
        ("--require-path-fragment", args.require_path_fragment),
        ("--forbid-path-fragment", args.forbid_path_fragment),
        ("--singleton-class", args.singleton_class),
    ):
        for value in values:
            if not value.strip() or (
                option_name != "--singleton-class" and not _normalize_assertion_path(value)
            ):
                print(f"{args.label}: {option_name} cannot be blank", file=sys.stderr)
                return 2
    try:
        artifacts = {
            "sourcemap": read_sourcemap(args.sourcemap),
            "place": read_rbxlx(args.place),
        }
    except (OSError, ValueError, json.JSONDecodeError, ET.ParseError) as error:
        print(f"{args.label}: could not inspect artifacts: {error}", file=sys.stderr)
        return 2

    failures = check_artifacts(
        artifacts,
        required_paths=args.require_path,
        required_fragments=args.require_path_fragment,
        forbidden_fragments=args.forbid_path_fragment,
        singleton_classes=args.singleton_class,
    )
    if failures:
        for failure in failures:
            print(f"{args.label}: {failure}", file=sys.stderr)
        return 1

    print(
        f"{args.label}: OK ({len(artifacts['sourcemap'].paths)} sourcemap instances, "
        f"{len(artifacts['place'].paths)} place instances)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
