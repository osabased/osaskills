"""Compare a project's manifest and lock with a library skill's pin.

Reads pesde.toml/pesde.lock, wally.toml/wally.lock or package.json/package-lock.json, as the
skill's install profile says. Never reads installed packages and never runs anything.
"""
from __future__ import annotations

import json
from pathlib import Path
import tomllib

from _resource_contract import load_contract, url_identity

WALLY_SECTIONS = ("dependencies", "server-dependencies", "dev-dependencies")
ERRORS = (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError)


class Unavailable(ValueError):
    """The comparison can't be made here; this is not evidence of a mismatch."""


def check(child: Path, project: Path) -> dict[str, str]:
    """Return {"status", "reason"}: PASS when the project's manifest and lock match the skill's pin,
    FAIL when they declare something else or are malformed, UNAVAILABLE when they can't be compared."""
    try:
        contract = load_contract(child, check_documents=False)
    except ERRORS as exc:
        return {"status": "UNAVAILABLE", "reason": f"the skill's resource.yaml can't be read: {exc}"}
    try:
        return {"status": "PASS", "reason": compare(contract, project.resolve())}
    except (Unavailable, PermissionError) as exc:
        return {"status": "UNAVAILABLE", "reason": str(exc)}
    except ERRORS as exc:
        return {"status": "FAIL", "reason": str(exc)}


def compare(contract: dict, project: Path) -> str:
    resource, install = contract["resource"], contract["installation"]
    profile = install["profile"]
    if profile == "custom":
        raise Unavailable("the skill checks its pin with its own script; run it as the skill's SKILL.md says")
    if profile == "asset":
        raise Unavailable("the skill pins an installed file outside the project; hash it as the skill's SKILL.md says")
    if not project.is_dir():
        raise Unavailable("the project directory does not exist")
    if profile == "npm":
        manifest, lock = require_files(project, "package.json", "package-lock.json")
        npm_declared(resource, install, json_object(manifest), json_object(lock))
        return "package.json and package-lock.json match the pin"
    if profile == "wally" or (profile == "pesde-wally" and not (project / "pesde.toml").is_file() and (project / "wally.toml").is_file()):
        manifest, lock = require_files(project, "wally.toml", "wally.lock")
        notes = wally_declared(resource, install, toml(manifest), toml(lock))
        return "; ".join(["wally.toml and wally.lock match the pin", *notes])
    manifest, lock = require_files(project, "pesde.toml", "pesde.lock")
    pesde_declared(resource, install, toml(manifest), toml(lock))
    return "pesde.toml and pesde.lock match the pin"


def require_files(project: Path, *names: str) -> list[Path]:
    paths = [project / name for name in names]
    missing = [path.name for path in paths if not path.is_file()]
    if missing:
        raise Unavailable(f"the project has no {' or '.join(missing)}")
    return paths


def same_url(left, right) -> bool:
    return isinstance(left, str) and isinstance(right, str) and url_identity(left) == url_identity(right)


def toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8-sig"))


def json_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} is not a JSON object")
    return value


def npm_declared(resource: dict, install: dict, manifest: dict, lock: dict) -> None:
    if type(lock.get("lockfileVersion")) is not int or lock["lockfileVersion"] not in {2, 3}:
        raise Unavailable(f"package-lock.json is format {lock.get('lockfileVersion')!r}; this check reads formats 2 and 3")
    packages = lock.get("packages")
    if not isinstance(packages, dict) or not isinstance(packages.get(""), dict):
        raise ValueError("package-lock.json has no root package entry")
    root = packages[""]
    for field in ("name", "version"):
        if field in manifest and (lock.get(field) != manifest[field] or root.get(field) != manifest[field]):
            raise ValueError("package.json and package-lock.json name different projects; reinstall to sync the lock")
    specifications = [{**install, "package_id": resource["package_id"], "version": resource["selector"]["value"]}, *install.get("companions", [])]
    for index, specification in enumerate(specifications):
        package, version, section = specification["package_id"], specification["version"], specification["dependency_section"]
        dependencies = manifest.get(section, {})
        locked_dependencies = root.get(section, {})
        if not isinstance(dependencies, dict) or not isinstance(locked_dependencies, dict):
            raise ValueError(f"package.json {section} is not an object")
        matches = [name for name, value in dependencies.items()
                   if name == package or (isinstance(value, str) and value.startswith(f"npm:{package}@"))]
        if not matches:
            if index == 0:
                raise Unavailable(f"package.json doesn't declare {package}; the project doesn't pin it")
            raise ValueError(f"package.json doesn't declare {package} in {section}; the skill pins it at {version} with {resource['package_id']}")
        if len(matches) > 1:
            raise Unavailable(f"package.json declares {package} more than once; compare each with the skill's pin by hand")
        name = matches[0]
        accepted = {f"npm:{package}@{version}"} | ({version} if name == package else set())
        if dependencies[name] not in accepted:
            raise ValueError(f"package.json pins {package} to {dependencies[name]!r}; the skill targets {version}")
        entry = packages.get("node_modules/" + name)
        if locked_dependencies.get(name) != dependencies[name] or not isinstance(entry, dict):
            raise ValueError(f"package-lock.json doesn't match package.json for {package}; reinstall to sync the lock")
        if entry.get("link") or entry.get("version") != version or entry.get("name", package) != package:
            raise ValueError(f"package-lock.json resolves {package} to {entry.get('version')!r}; the skill targets {version}")
        if not same_url(entry.get("resolved"), specification["archive_url"]) or entry.get("integrity") != specification["archive_integrity"]:
            raise ValueError(f"package-lock.json resolves {package}@{version} to a different archive than the one the skill reviewed")


def pesde_declared(resource: dict, install: dict, manifest: dict, lock: dict) -> None:
    if lock.get("format") != 2:
        raise Unavailable(f"pesde.lock format {lock.get('format')!r} not supported (expects 2); check the pin by hand")
    environment = manifest.get("target", {}).get("environment")
    if environment not in {"roblox", "lune", "luau"} or lock.get("target") != environment:
        raise ValueError("pesde.toml and pesde.lock name different targets; run pesde install to sync the lock")
    if any(not isinstance(data.get(field), str) or not data[field].strip() for data in (manifest, lock) for field in ("name", "version")):
        raise ValueError("pesde.toml or pesde.lock has no project name and version")
    if any(manifest[field] != lock[field] for field in ("name", "version")):
        raise ValueError("pesde.toml and pesde.lock name different projects; run pesde install to sync the lock")
    profile, section = install["profile"], install["dependency_section"]
    dependencies = manifest.get(section, {})
    if not isinstance(dependencies, dict):
        raise ValueError(f"pesde.toml [{section}] is not a table")
    key = "wally" if profile == "pesde-wally" else "name"
    package = resource["package_id"]
    if profile == "pesde-git":
        matches = [(name, value) for name, value in dependencies.items() if isinstance(value, dict) and same_url(value.get("repo"), resource["canonical_url"])]
    else:
        matches = [(name, value) for name, value in dependencies.items() if isinstance(value, dict) and value.get(key) == package]
    if not matches:
        raise Unavailable(f"pesde.toml [{section}] doesn't declare {package}; the project doesn't pin it")
    if len(matches) > 1:
        raise Unavailable(f"pesde.toml declares {package} more than once; compare each with the skill's pin by hand")
    name, dependency = matches[0]
    selector = resource["selector"]
    if profile == "pesde-git":
        if dependency.get("rev") != selector["value"]:
            raise ValueError(f"pesde.toml pins {name} to rev {dependency.get('rev')!r}; the skill targets {selector['value']}")
    elif dependency.get("version") != "=" + selector["value"]:
        raise ValueError(f"pesde.toml pins {name} to {dependency.get('version')!r}; the skill targets ={selector['value']}")
    target = dependency.get("target", environment)
    if target != install["target"]:
        raise ValueError(f"pesde.toml uses {name} with target {target!r}; the skill targets {install['target']}")
    if profile != "pesde-git":
        indices = manifest.get("wally_indices" if profile == "pesde-wally" else "indices", {})
        if not same_url(indices.get(dependency.get("index", "default")), install["registry"]):
            raise ValueError(f"pesde.toml takes {name} from another index than {install['registry']}")
    graph = lock.get("graph")
    if not isinstance(graph, dict):
        raise ValueError("pesde.lock has no graph table")
    entries = [(graph_key, entry) for graph_key, entry in graph.items()
               if isinstance(entry, dict) and isinstance(entry.get("direct"), list) and entry["direct"] and entry["direct"][0] == name]
    if len(entries) != 1:
        raise ValueError(f"pesde.lock has no single direct entry for {name}; run pesde install to sync the lock")
    graph_key, entry = entries[0]
    expected = dict(dependency)
    if profile != "pesde-git":
        expected[key] = ("wally#" if profile == "pesde-wally" else "") + package
        expected.setdefault("index", "default")
    if entry.get("direct") != [name, expected, "dev" if section == "dev_dependencies" else "standard"]:
        raise ValueError(f"pesde.lock's entry for {name} differs from pesde.toml; run pesde install to sync the lock")
    ref = entry.get("pkg_ref")
    if not isinstance(ref, dict):
        raise ValueError(f"pesde.lock's entry for {name} has no package reference")
    if profile == "pesde-git":
        expected_key = f"{package}@0.0.0-{selector['tree']} {install['target']}"
        found = graph_key.removeprefix("wally#")
        if found != expected_key or ref.get("ref_ty") != "git" or not same_url(ref.get("repo"), resource["canonical_url"]) or ref.get("tree_id") != selector["tree"]:
            raise ValueError(f"pesde.lock resolves {name} to {found}; the skill targets {expected_key}")
        if "new_structure" in install and ref.get("new_structure") != install["new_structure"]:
            raise ValueError(f"pesde.lock's layout for {name} (new_structure) differs from the skill's")
    else:
        expected_key = f"{'wally#' if profile == 'pesde-wally' else ''}{package}@{selector['value']} {install['target']}"
        if graph_key != expected_key or ref.get("ref_ty") != ("wally" if profile == "pesde-wally" else "pesde") or not same_url(ref.get("index_url"), install["registry"]):
            raise ValueError(f"pesde.lock resolves {name} to {graph_key}; the skill targets {expected_key}")
    entries_by_package = {package: entry}
    for companion in install.get("companions", []):
        companion_key = f"wally#{companion['package_id']}@{companion['version']} roblox"
        counterpart = graph.get(companion_key)
        if not isinstance(counterpart, dict) or counterpart.get("pkg_ref", {}).get("ref_ty") != "wally" or not same_url(counterpart.get("pkg_ref", {}).get("index_url"), companion["registry"]):
            raise ValueError(f"pesde.lock has no {companion_key} from {companion['registry']}; the skill targets it with {package}")
        parent = entries_by_package.get(companion["parent_package"])
        if not parent or parent.get("dependencies", {}).get(companion["edge_alias"]) != [companion_key, "standard"]:
            raise ValueError(f"pesde.lock doesn't link {companion['parent_package']} to {companion_key} as {companion['edge_alias']}")
        entries_by_package[companion["package_id"]] = counterpart


def wally_requirement(value: object) -> tuple[str, str]:
    if not isinstance(value, str) or "@" not in value:
        raise ValueError("a Wally dependency must be a \"scope/name@requirement\" string")
    package, _, requirement = value.strip().rpartition("@")
    return package.lower(), requirement.strip()


def wally_declared(resource: dict, install: dict, manifest: dict, lock: dict) -> list[str]:
    """Bind wally.toml and wally.lock to the pin. Returns notes, such as a range requirement the lock resolves."""
    package_id = resource["package_id"].lower()
    version = resource["selector"]["value"]
    header = manifest.get("package")
    if not isinstance(header, dict) or not isinstance(header.get("name"), str):
        raise ValueError("wally.toml has no [package] name")
    if "registry" in install and header.get("registry") is not None and not same_url(header.get("registry"), install["registry"]):
        raise ValueError(f"wally.toml uses another registry than {install['registry']}")
    sections = (install["dependency_section"],) if install["profile"] == "wally" else WALLY_SECTIONS
    matches = []
    for section in sections:
        dependencies = manifest.get(section, {})
        if not isinstance(dependencies, dict):
            raise ValueError(f"wally.toml [{section}] is not a table")
        matches += [(name, value) for name, value in dependencies.items() if isinstance(value, str) and wally_requirement(value)[0] == package_id]
    if not matches:
        raise Unavailable(f"wally.toml doesn't declare {resource['package_id']}; the project doesn't pin it")
    if len(matches) > 1:
        raise Unavailable(f"wally.toml declares {resource['package_id']} more than once; compare each with the skill's pin by hand")
    name, value = matches[0]
    notes = []
    requirement = wally_requirement(value)[1]
    if requirement.startswith("="):
        if requirement.removeprefix("=").strip() != version:
            raise ValueError(f"wally.toml pins {resource['package_id']} to {requirement}; the skill targets ={version}")
    else:
        notes.append(f"wally.toml requires {requirement!r}, a range; wally.lock decides the version")
    packages = lock.get("package")
    if not isinstance(packages, list):
        raise ValueError("wally.lock has no [[package]] entries")
    entries = {}
    for entry in packages:
        if isinstance(entry, dict) and isinstance(entry.get("name"), str):
            entries.setdefault(entry["name"].lower(), []).append(entry)
    roots = entries.get(header["name"].lower(), [])
    if len(roots) != 1:
        raise ValueError("wally.lock doesn't have exactly one entry for the project package; run wally install")
    locked = [item for item in roots[0].get("dependencies", []) if isinstance(item, list) and len(item) == 2 and item[0] == name]
    if len(locked) != 1:
        raise ValueError(f"wally.lock has no direct entry for {name}; run wally install")
    locked_package, _, locked_version = str(locked[0][1]).rpartition("@")
    if locked_package.lower() != package_id:
        raise ValueError(f"wally.lock binds {name} to {locked_package}, not {resource['package_id']}")
    if locked_version != version:
        raise ValueError(f"wally.lock resolves {resource['package_id']} to {locked_version}; the skill targets {version}")
    if not any(entry.get("version") == version for entry in entries.get(package_id, [])):
        raise ValueError(f"wally.lock has no package entry for {resource['package_id']}@{version}; run wally install")
    for companion in install.get("companions", []):
        companion_id = companion["package_id"].lower()
        if not any(entry.get("version") == companion["version"] for entry in entries.get(companion_id, [])):
            raise ValueError(f"wally.lock has no {companion['package_id']}@{companion['version']}; the skill targets it with {resource['package_id']}")
        edge = [companion["edge_alias"], f"{companion['package_id']}@{companion['version']}".lower()]
        parents = entries.get(companion["parent_package"].lower(), [])
        if not any(any(isinstance(item, list) and [item[0], str(item[1]).lower()] == edge for item in parent.get("dependencies", [])) for parent in parents):
            raise ValueError(f"wally.lock doesn't link {companion['parent_package']} to {companion['package_id']}@{companion['version']} as {companion['edge_alias']}")
    return notes
