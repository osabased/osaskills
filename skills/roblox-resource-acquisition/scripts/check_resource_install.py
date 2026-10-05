#!/usr/bin/env python3
"""Read-only declaration/installed-integrity checks driven by child contract 1.

Profiles are data, never commands. No evidence commands or dependency code run.
Aliases and source locations are project inputs, not canonical resource identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tomllib

from _resource_contract import load_contract, within, url_identity
from guard_skill_update import marker_path


def same_url(left, right):
    return isinstance(left, str) and isinstance(right, str) and url_identity(left) == url_identity(right)


def toml(path: Path) -> dict:
    value = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"TOML root is not a mapping: {path}")
    return value


def json_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be a mapping: " + str(path))
    return value


def npm_declared(resource: dict, install: dict, manifest: dict, lock: dict, alias: str | None) -> dict[str, str]:
    if type(lock.get("lockfileVersion")) is not int or lock["lockfileVersion"] not in {2, 3}:
        raise ValueError("npm profile requires package-lock format 2 or 3")
    packages = lock.get("packages")
    if not isinstance(packages, dict) or not isinstance(packages.get(""), dict):
        raise ValueError("npm lock requires root declarations and package entries")
    root = packages[""]
    for field in ("name", "version"):
        if field in manifest and (lock.get(field) != manifest[field] or root.get(field) != manifest[field]):
            raise ValueError("npm manifest and lock project identities differ")
    specifications = [{**install, "package_id": resource["package_id"], "version": resource["selector"]["value"]}, *install.get("companions", [])]
    bindings = {}
    for index, specification in enumerate(specifications):
        package, version = specification["package_id"], specification["version"]
        section = specification["dependency_section"]
        dependencies = manifest.get(section, {})
        locked_dependencies = root.get(section, {})
        if not isinstance(dependencies, dict) or not isinstance(locked_dependencies, dict):
            raise ValueError("npm dependency section must be a mapping")
        matches = [name for name, value in dependencies.items()
            if (not (index == 0 and alias is not None) or name == alias)
            and ((name == package and value == version) or value == f"npm:{package}@{version}")]
        if len(matches) != 1:
            raise ValueError("expected one exact direct npm binding for " + package)
        name = matches[0]
        within(Path.cwd(), "node_modules/" + name)
        entry = packages.get("node_modules/" + name)
        if locked_dependencies.get(name) != dependencies[name] or not isinstance(entry, dict):
            raise ValueError("npm lock direct declaration differs: " + package)
        if entry.get("link") or entry.get("version") != version or ("name" in entry and entry["name"] != package):
            raise ValueError("npm locked package identity/version differs: " + package)
        if not same_url(entry.get("resolved"), specification["archive_url"]) or entry.get("integrity") != specification["archive_integrity"]:
            raise ValueError("npm locked archive identity/integrity differs: " + package)
        bindings[package] = name
    return bindings


def npm_source(root: Path, package: str, version: str, spec: dict) -> None:
    if not root.is_dir():
        raise ValueError("installed npm source directory is missing: " + package)
    metadata = json_object(root / "package.json")
    if metadata.get("name") != package or metadata.get("version") != version:
        raise ValueError("installed npm manifest identity/version differs: " + package)
    integrity(root, spec)


def declared(resource: dict, install: dict, manifest: dict, lock: dict, alias: str | None) -> str:
    if lock.get("format") != 2:
        raise ValueError("expected pesde lock format 2")
    environment = manifest.get("target", {}).get("environment")
    if environment not in {"roblox", "lune", "luau"} or lock.get("target") != environment:
        raise ValueError("manifest and lock project targets differ or are missing")
    if any(not isinstance(data.get(field), str) or not data[field].strip() for data in (manifest, lock) for field in ("name", "version")):
        raise ValueError("manifest and lock require project identity headers")
    if any(manifest[field] != lock[field] for field in ("name", "version")):
        raise ValueError("manifest and lock project identities differ")
    profile = install["profile"]
    section = install["dependency_section"]
    dependencies = manifest.get(section, {})
    if not isinstance(dependencies, dict):
        raise ValueError("manifest dependency section is not a mapping")
    key = "wally" if profile == "pesde-wally" else "name"
    matches = []
    for name, dependency in dependencies.items():
        if not isinstance(dependency, dict) or (alias is not None and name != alias):
            continue
        identity = same_url(dependency.get("repo"), resource["canonical_url"]) if profile == "pesde-git" else dependency.get(key) == resource["package_id"]
        if identity:
            matches.append((name, dependency))
    if len(matches) != 1:
        raise ValueError("expected one canonical direct dependency; supply --alias when multiple bindings exist")
    name, dependency = matches[0]
    selector = resource["selector"]
    if profile == "pesde-git":
        if dependency.get("rev") != selector["value"]:
            raise ValueError("canonical Git commit differs from the reviewed target")
    elif dependency.get("version") != "=" + selector["value"]:
        raise ValueError("canonical package pin differs from the reviewed version")
    target = dependency.get("target", environment)
    if target != install["target"]:
        raise ValueError("direct dependency target differs from the reviewed profile")
    if profile != "pesde-git":
        indices = manifest.get("wally_indices" if profile == "pesde-wally" else "indices", {})
        if not same_url(indices.get(dependency.get("index", "default")), install["registry"]):
            raise ValueError("manifest registry identity differs")
    graph = lock.get("graph")
    if not isinstance(graph, dict):
        raise ValueError("lock graph must be a mapping")
    entries = [(key, entry) for key, entry in graph.items() if isinstance(entry, dict) and isinstance(entry.get("direct"), list) and entry["direct"] and entry["direct"][0] == name]
    if len(entries) != 1:
        raise ValueError("expected one direct lock counterpart for the resolved alias")
    graph_key, entry = entries[0]
    expected = dict(dependency)
    if profile != "pesde-git":
        expected[key] = ("wally#" if profile == "pesde-wally" else "") + resource["package_id"]
        expected.setdefault("index", "default")
    if entry.get("direct") != [name, expected, "dev" if section == "dev_dependencies" else "standard"]:
        raise ValueError("direct lock declaration differs from the manifest")
    ref = entry.get("pkg_ref")
    if not isinstance(ref, dict):
        raise ValueError("locked package reference is missing")
    if profile == "pesde-git":
        expected_key = resource["package_id"] + "@0.0.0-" + selector["tree"] + " " + install["target"]
        if graph_key.removeprefix("wally#") != expected_key or ref.get("ref_ty") != "git" or not same_url(ref.get("repo"), resource["canonical_url"]) or ref.get("tree_id") != selector["tree"]:
            raise ValueError("canonical Git lock identity/tree differs")
        if "new_structure" in install and ref.get("new_structure") != install["new_structure"]:
            raise ValueError("locked package layout differs from the reviewed profile")
    else:
        expected_key = ("wally#" if profile == "pesde-wally" else "") + resource["package_id"] + "@" + selector["value"] + " " + install["target"]
        if graph_key != expected_key or ref.get("ref_ty") != ("wally" if profile == "pesde-wally" else "pesde") or not same_url(ref.get("index_url"), install["registry"]):
            raise ValueError("locked package/version/registry identity differs")
    package_entries = {resource["package_id"]: entry}
    for companion in install.get("companions", []):
        companion_key = "wally#" + companion["package_id"] + "@" + companion["version"] + " roblox"
        counterpart = graph.get(companion_key)
        if not isinstance(counterpart, dict) or counterpart.get("pkg_ref", {}).get("ref_ty") != "wally" or not same_url(counterpart.get("pkg_ref", {}).get("index_url"), companion["registry"]):
            raise ValueError("missing or mismatched companion " + companion["package_id"])
        parent = package_entries.get(companion["parent_package"])
        if not parent or parent.get("dependencies", {}).get(companion["edge_alias"]) != [companion_key, "standard"]:
            raise ValueError("material companion dependency edge differs: " + companion["package_id"])
        package_entries[companion["package_id"]] = counterpart
    return name


def source_root(project: Path, package: str, selector: dict, supplied: Path | None, target: str) -> Path:
    if supplied is not None:
        resolved = supplied.resolve()
        if not resolved.is_dir():
            raise ValueError("explicit package source directory is missing")
        return resolved
    candidates = set()
    base = project / (target + "_packages") / ".pesde"
    if base.is_dir():
        prefixes = {package.replace("/", "_"), package.replace("/", "+")}
        containers = [item for item in base.iterdir() if item.is_dir() and any(item.name == prefix or item.name.startswith(prefix + "@") for prefix in prefixes)]
        for container in containers:
            for filename in ("wally.toml", "pesde.toml"):
                for path in container.rglob(filename):
                    data = toml(path)
                    metadata = data.get("package", data)
                    if metadata.get("name") != package:
                        continue
                    if selector["kind"] == "commit":
                        if selector["tree"] not in path.as_posix():
                            continue
                    elif metadata.get("version") != selector["value"]:
                        continue
                    candidates.add(path.parent.resolve())
    if len(candidates) != 1:
        raise ValueError("cannot uniquely resolve installed source; provide --package-dir or --companion PACKAGE=DIR from the project's actual mapping")
    return candidates.pop()


def integrity(root: Path, spec: dict) -> None:
    for relative, expected in spec.get("files", {}).items():
        path = within(root, relative)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("installed source digest differs: " + relative)
    if "aggregate" in spec:
        aggregate = spec["aggregate"]
        directory = within(root, aggregate["directory"])
        recursive = aggregate.get("recursive", False)
        files = sorted(directory.rglob("*" + aggregate["suffix"]) if recursive else directory.glob("*" + aggregate["suffix"]),
                       key=lambda path: path.relative_to(directory).as_posix() if recursive else path.name)
        if not files:
            raise ValueError("installed aggregate source is missing")
        payload = "\n".join((path.relative_to(directory).as_posix() if recursive else path.name) + " " +
                           hashlib.sha256(within(root, path.relative_to(root).as_posix()).read_bytes()).hexdigest() for path in files).encode()
        if hashlib.sha256(payload).hexdigest() != aggregate["sha256"]:
            raise ValueError("installed aggregate source digest differs")
    if "version_header" in spec:
        header = spec["version_header"]
        if header["contains"] not in within(root, header["path"]).read_text(encoding="utf-8-sig"):
            raise ValueError("installed source version header differs")
    if "manifest" in spec:
        expected = spec["manifest"]
        path = within(root, expected["path"])
        data = json_object(path) if path.suffix == ".json" else toml(path)
        package = data.get("package", data)
        if package.get("name") != expected["name"] or package.get("version") != expected["version"]:
            raise ValueError("installed source manifest identity/version differs")


def check(skill: Path, project: Path | None, *, declared_only=False, manifest_path=None, lock_path=None, alias=None, package_dir=None, companions=None, asset=None) -> dict:
    for directory in (skill.resolve(), Path(__file__).resolve().parent.parent):
        if marker_path(directory).exists() or marker_path(directory).is_symlink():
            raise ValueError("promotion is pending or interrupted; reconcile the maintenance guard")
    contract = load_contract(skill, check_documents=False)
    if project is None and contract["scope"] == "project":
        raise ValueError("UNKNOWN: project-scoped child requires an explicit resolved project; no global fallback")
    if project is not None:
        project = project.resolve()
        if not project.is_dir():
            raise ValueError("UNKNOWN: project directory does not exist")
    resource, install = contract["resource"], contract["installation"]
    result = {"status": "PASS", "resource": resource["slug"], "selector": resource["selector"]["value"]}
    if install["profile"] == "custom":
        return {**result, "status": "UNAVAILABLE", "reason": "run the child-owned custom checker as documented; this tool never executes contract-supplied commands"}
    if install["profile"] == "asset":
        if asset is None or not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != install["asset_sha256"]:
            raise ValueError("missing or mismatched exact installed asset; provide --asset")
        return {**result, "lane": "asset-integrity", "asset": str(asset.resolve())}
    if project is None:
        raise ValueError("UNKNOWN: package checking needs an explicit project")
    if install["profile"] == "npm":
        manifest_path = manifest_path or project / "package.json"
        lock_path = lock_path or project / "package-lock.json"
        bindings = npm_declared(resource, install, json_object(manifest_path), json_object(lock_path), alias)
        if declared_only:
            return {**result, "lane": "declaration-lock", "alias": bindings[resource["package_id"]]}
        companions = companions or {}
        expected = {item["package_id"] for item in install.get("companions", [])}
        if set(companions) - expected:
            raise ValueError("an explicit companion binding is not part of this reviewed resource")
        resolved_root = package_dir.resolve() if package_dir else within(project / "node_modules", bindings[resource["package_id"]])
        npm_source(resolved_root, resource["package_id"], resource["selector"]["value"], install["integrity"])
        for companion in install.get("companions", []):
            package = companion["package_id"]
            root = companions[package].resolve() if package in companions else within(project / "node_modules", bindings[package])
            npm_source(root, package, companion["version"], companion["integrity"])
        return {**result, "lane": "installed-integrity", "alias": bindings[resource["package_id"]], "package_dir": str(resolved_root)}
    manifest_path = manifest_path or project / "pesde.toml"
    lock_path = lock_path or project / "pesde.lock"
    resolved_alias = declared(resource, install, toml(manifest_path), toml(lock_path), alias)
    if declared_only:
        return {**result, "lane": "declaration-lock", "alias": resolved_alias}
    resolved_root = source_root(project, resource["package_id"], resource["selector"], package_dir, install["target"])
    integrity(resolved_root, install["integrity"])
    companions = companions or {}
    expected_companions = {item["package_id"] for item in install.get("companions", [])}
    if set(companions) - expected_companions:
        raise ValueError("an explicit companion binding is not part of this reviewed resource")
    for companion in install.get("companions", []):
        root = source_root(project, companion["package_id"], {"kind": "version", "value": companion["version"]}, companions.get(companion["package_id"]), "roblox")
        integrity(root, companion["integrity"])
    return {**result, "lane": "installed-integrity", "alias": resolved_alias, "package_dir": str(resolved_root)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--alias")
    parser.add_argument("--declared", action="store_true")
    parser.add_argument("--package-dir", type=Path)
    parser.add_argument("--companion", action="append", default=[], metavar="PACKAGE=DIR")
    parser.add_argument("--asset", type=Path)
    args = parser.parse_args(argv)
    try:
        companions = {}
        for binding in args.companion:
            package, separator, directory = binding.partition("=")
            if not separator or not package or not directory or package in companions:
                raise ValueError("companion bindings require unique PACKAGE=DIR values")
            companions[package] = Path(directory)
        result = check(args.skill, args.project, declared_only=args.declared, manifest_path=args.manifest, lock_path=args.lock, alias=args.alias, package_dir=args.package_dir, companions=companions, asset=args.asset)
    except PermissionError as exc:
        print(json.dumps({"status": "UNAVAILABLE", "reason": f"installed-state read denied: {exc}"}))
        return 2
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError) as exc:
        unknown = str(exc).startswith("UNKNOWN:")
        print(json.dumps({"status": "UNKNOWN" if unknown else "FAIL", "reason": str(exc)}))
        return 2 if unknown else 1
    print(json.dumps(result, sort_keys=True))
    return 2 if result["status"] == "UNAVAILABLE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
