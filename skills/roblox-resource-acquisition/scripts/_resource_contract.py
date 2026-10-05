"""Static, versioned child specifications. Project records own live state and proof."""
from __future__ import annotations

from datetime import date
import base64
from pathlib import Path
import re
from typing import Any
from urllib.parse import parse_qsl, urlparse

from _common import load_yaml, validated_url_host, SENSITIVE_QUERY_RE, has_immutable_version_evidence

SCHEMA_VERSION = 1
PARENT_CONTRACT_VERSION = 1
PARENT_NAME = "roblox-resource-acquisition"
CORE_ROLES = {"routing", "common-use", "ownership", "security", "verification", "maintenance"}
ALL_ROLES = CORE_ROLES | {"setup", "troubleshooting", "recipes", "lifecycle", "api"}
PROFILES = {"pesde-wally", "pesde-registry", "pesde-git", "npm", "asset", "custom"}
HEX256 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NPM_PACKAGE = re.compile(r"(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*")
EXACT_RELEASE = re.compile(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?")


def url_identity(value: str) -> tuple[str, str, int | None, str, str]:
    if not isinstance(value, str) or any(char.isspace() for char in value):
        raise ValueError("source URLs must be strings without whitespace")
    parsed = urlparse(value.strip())
    host = validated_url_host(parsed)
    if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("source URLs require HTTPS, a valid host, and no credentials or fragment")
    if any(SENSITIVE_QUERY_RE.search(key) for key, _ in parse_qsl(parsed.query)):
        raise ValueError("source URL must not contain secret-like query parameters")
    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return parsed.scheme, host, parsed.port, path, parsed.query


def within(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("package path must be a nonempty relative path")
    if "\\" in relative or relative.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", relative):
        raise ValueError(f"package path must be portable and relative: {relative}")
    parts = Path(relative).parts
    if ".." in parts:
        raise ValueError(f"package path escapes its root: {relative}")
    result = (root / relative).resolve()
    if not result.is_relative_to(root.resolve()) or result == root.resolve():
        raise ValueError(f"package path escapes its root: {relative}")
    return result


def mapping(value: Any, fields: set[str], required: set[str], label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    unknown = set(value) - fields
    missing = required - set(value)
    if unknown or missing:
        raise ValueError(f"{label}: unknown fields {sorted(map(str, unknown))}; missing fields {sorted(missing)}")
    return value


def string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value.strip()


def strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a nonempty list")
    result = [string(item, label) for item in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    return result


def choice(value: Any, options: set[str], label: str) -> str:
    if not isinstance(value, str) or value not in options:
        raise ValueError(f"{label} must be one of {', '.join(sorted(options))}")
    return value


def validate_integrity(value: Any, label: str) -> None:
    spec = mapping(value, {"files", "aggregate", "version_header", "manifest"}, set(), label)
    if not spec:
        raise ValueError(f"{label} needs at least one integrity expectation")
    files = spec.get("files", {})
    if not isinstance(files, dict):
        raise ValueError(f"{label}.files must be a mapping")
    for path, digest in files.items():
        within(Path.cwd(), path)
        if not isinstance(digest, str) or not HEX256.fullmatch(digest):
            raise ValueError(f"{label}.files requires SHA256 digests")
    if "aggregate" in spec:
        aggregate = mapping(spec["aggregate"], {"directory", "suffix", "sha256", "recursive"}, {"directory", "suffix", "sha256"}, label + ".aggregate")
        within(Path.cwd(), aggregate["directory"])
        if aggregate["suffix"] not in {".lua", ".luau"} or not HEX256.fullmatch(str(aggregate["sha256"])):
            raise ValueError(f"{label}.aggregate requires a source suffix and SHA256")
        if "recursive" in aggregate and type(aggregate["recursive"]) is not bool:
            raise ValueError(f"{label}.aggregate.recursive must be boolean")
    if "version_header" in spec:
        header = mapping(spec["version_header"], {"path", "contains"}, {"path", "contains"}, label + ".version_header")
        within(Path.cwd(), header["path"])
        string(header["contains"], label + ".version_header.contains")
    if "manifest" in spec:
        manifest = mapping(spec["manifest"], {"path", "name", "version"}, {"path", "name", "version"}, label + ".manifest")
        within(Path.cwd(), manifest["path"])
        string(manifest["name"], label + ".manifest.name")
        string(manifest["version"], label + ".manifest.version")


def validate_npm_package(value: dict, registry: str, label: str) -> None:
    if not NPM_PACKAGE.fullmatch(string(value.get("package_id"), label + ".package_id")):
        raise ValueError(label + " requires a canonical npm package identity")
    if not EXACT_RELEASE.fullmatch(string(value.get("version"), label + ".version")):
        raise ValueError(label + " requires an exact npm release")
    choice(value.get("dependency_section"), {"dependencies", "devDependencies"}, label + ".dependency_section")
    source = url_identity(string(value.get("archive_url"), label + ".archive_url"))
    origin = url_identity(registry)
    if source[:3] != origin[:3] or not source[3].startswith(origin[3] + "/") or source[4]:
        raise ValueError(label + " archive must belong to the declared registry")
    integrity = string(value.get("archive_integrity"), label + ".archive_integrity")
    if not integrity.startswith("sha512-"):
        raise ValueError(label + " archive_integrity requires a SHA512 SRI digest")
    try:
        digest = base64.b64decode(integrity.removeprefix("sha512-"), validate=True)
    except ValueError as exc:
        raise ValueError(label + " archive_integrity is malformed") from exc
    if len(digest) != 64:
        raise ValueError(label + " archive_integrity requires a SHA512 SRI digest")
    validate_integrity(value.get("integrity"), label + ".integrity")


def load_contract(root: Path, *, check_documents: bool = True) -> dict[str, Any]:
    path = root / "resource.yaml"
    if not path.is_file():
        raise ValueError("resource.yaml is required; regenerate the child using resource-child contract 1")
    data = load_yaml(path.read_text(encoding="utf-8-sig"))
    required = {"schema_version", "parent_contract", "scope", "resource", "routing", "guidance", "reconciliation", "installation"}
    mapping(data, required, required, "resource.yaml")
    if type(data["schema_version"]) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported resource.yaml schema_version; regenerate the child")
    parent = mapping(data["parent_contract"], {"name", "version"}, {"name", "version"}, "parent_contract")
    if parent["name"] != PARENT_NAME or type(parent["version"]) is not int or parent["version"] != PARENT_CONTRACT_VERSION:
        raise ValueError("unsupported shared parent contract; regenerate with the installed parent")
    choice(data["scope"], {"project", "user"}, "scope")
    resource = mapping(data["resource"], {"slug", "name", "canonical_url", "package_id", "selector", "source_review_date", "devforum_url"}, {"slug", "name", "canonical_url", "package_id", "selector", "source_review_date", "devforum_url"}, "resource")
    if not SLUG.fullmatch(string(resource["slug"], "resource.slug")):
        raise ValueError("resource.slug must be lowercase kebab-case")
    string(resource["name"], "resource.name")
    url_identity(string(resource["canonical_url"], "resource.canonical_url"))
    if resource["package_id"] is not None:
        string(resource["package_id"], "resource.package_id")
    if resource["devforum_url"] is not None:
        parsed = urlparse(string(resource["devforum_url"], "resource.devforum_url"))
        url_identity(resource["devforum_url"])
        if parsed.hostname != "devforum.roblox.com" or not re.fullmatch(r"/t/(?:[^/]+/)?\d+(?:/\d+)?/?", parsed.path):
            raise ValueError("resource.devforum_url must identify an exact DevForum topic")
    reviewed = string(resource["source_review_date"], "resource.source_review_date")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed):
        raise ValueError("resource.source_review_date must be YYYY-MM-DD")
    try:
        date.fromisoformat(reviewed)
    except ValueError as exc:
        raise ValueError("resource.source_review_date is not a calendar date") from exc
    selector = mapping(resource["selector"], {"kind", "value", "tree", "release_commit"}, {"kind", "value"}, "resource.selector")
    value = string(selector["value"], "resource.selector.value")
    choice(selector["kind"], {"version", "commit", "source-state"}, "resource.selector.kind")
    if not has_immutable_version_evidence(value):
        raise ValueError("resource.selector must identify a reviewed immutable version/commit or dated source-state")
    if selector["kind"] == "commit" and not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise ValueError("commit selectors require a full immutable commit")
    for field in ("tree", "release_commit"):
        if field in selector and not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", str(selector[field])):
            raise ValueError(f"resource.selector.{field} must be a full hash")
    routing = mapping(data["routing"], {"use_when", "avoid_when"}, {"use_when", "avoid_when"}, "routing")
    strings(routing["use_when"], "routing.use_when")
    strings(routing["avoid_when"], "routing.avoid_when")
    guidance = mapping(data["guidance"], {"claim_scope", "shared_usage", "documents", "executable_fixture"}, {"claim_scope", "shared_usage", "documents", "executable_fixture"}, "guidance")
    choice(guidance["claim_scope"], {"advice-only", "executable-integration"}, "guidance.claim_scope")
    if guidance["shared_usage"] != "references/child-usage.md":
        raise ValueError("guidance.shared_usage must route to the installed parent's child-usage contract")
    if guidance["claim_scope"] == "advice-only" and guidance["executable_fixture"] is not None:
        raise ValueError("advice-only children do not carry an executable integration fixture")
    if guidance["claim_scope"] == "executable-integration":
        fixture = within(root, guidance["executable_fixture"])
        if check_documents and not fixture.is_file():
            raise ValueError("executable-integration requires an existing maintained fixture")
    documents = guidance["documents"]
    if not isinstance(documents, list) or not documents:
        raise ValueError("guidance.documents must declare the entrypoint and conditional references")
    seen = set()
    coverage = set()
    core = set()
    for document in documents:
        document = mapping(document, {"path", "roles", "when"}, {"path", "roles", "when"}, "guidance.documents[]")
        relative = string(document["path"], "guidance.documents[].path")
        target = within(root, relative)
        if relative in seen or target.suffix != ".md" or (check_documents and not target.is_file()):
            raise ValueError(f"guidance document is missing, duplicated, or not Markdown: {relative}")
        if check_documents and not target.read_text(encoding="utf-8-sig").strip():
            raise ValueError(f"guidance document is empty: {relative}")
        seen.add(relative)
        roles = set(strings(document["roles"], "guidance.documents[].roles"))
        if roles - ALL_ROLES:
            raise ValueError(f"unknown guidance roles: {sorted(roles - ALL_ROLES)}")
        string(document["when"], "guidance.documents[].when")
        coverage.update(roles)
        if relative == "SKILL.md":
            core.update(roles)
    if not CORE_ROLES <= core or not {"setup", "troubleshooting"} <= coverage:
        raise ValueError("entrypoint must cover routing/use/ownership/security/verification/maintenance; setup and troubleshooting must be reachable")
    reconciliation = mapping(data["reconciliation"], {"policy", "reason", "record", "learnings", "no_project_record", "no_project_learnings"}, {"policy", "reason", "record", "learnings"}, "reconciliation")
    choice(reconciliation["policy"], {"required", "conditional", "not-applicable"}, "reconciliation.policy")
    string(reconciliation["reason"], "reconciliation.reason")
    for field in ("record", "learnings"):
        within(root, string(reconciliation[field], "reconciliation." + field))
    if data["scope"] == "project" and any(field in reconciliation for field in ("no_project_record", "no_project_learnings")):
        raise ValueError("project-scoped children cannot fall back to global records/learnings")
    if data["scope"] == "user":
        for field in ("no_project_record", "no_project_learnings"):
            value = string(reconciliation.get(field), "reconciliation." + field)
            if not value.startswith("~/.roblox-resources/") or ".." in Path(value).parts:
                raise ValueError("user-scope no-project evidence must resolve under ~/.roblox-resources")
    install = mapping(data["installation"], {"profile", "dependency_section", "registry", "target", "new_structure", "integrity", "companions", "asset_sha256", "custom_checker", "archive_url", "archive_integrity"}, {"profile"}, "installation")
    profile = choice(install["profile"], PROFILES, "installation.profile")
    fields = {
        "pesde-wally": {"dependency_section", "registry", "target", "integrity", "companions"},
        "pesde-registry": {"dependency_section", "registry", "target", "integrity"},
        "pesde-git": {"dependency_section", "target", "new_structure", "integrity"},
        "npm": {"dependency_section", "registry", "integrity", "companions", "archive_url", "archive_integrity"},
        "asset": {"asset_sha256"},
        "custom": {"custom_checker"},
    }[profile] | {"profile"}
    if set(install) - fields:
        raise ValueError(f"installation contains fields unsupported by {profile}: {sorted(set(install) - fields)}")
    if profile.startswith("pesde-"):
        if resource["package_id"] is None:
            raise ValueError("pesde profiles require package_id, dependency_section and target")
        choice(install.get("dependency_section"), {"dependencies", "dev_dependencies"}, "installation.dependency_section")
        choice(install.get("target"), {"roblox", "lune", "luau"}, "installation.target")
        if profile != "pesde-git":
            url_identity(string(install.get("registry"), "installation.registry"))
            if selector["kind"] != "version":
                raise ValueError("registry package profiles require an exact version selector")
        elif selector["kind"] != "commit" or "tree" not in selector:
            raise ValueError("pesde-git requires immutable commit and lock tree")
        if "new_structure" in install and type(install["new_structure"]) is not bool:
            raise ValueError("installation.new_structure must be boolean")
        validate_integrity(install.get("integrity"), "installation.integrity")
        companions = install.get("companions", [])
        if not isinstance(companions, list):
            raise ValueError("installation.companions must be a list")
        packages = {resource["package_id"]}
        for companion in companions:
            companion = mapping(companion, {"package_id", "version", "registry", "integrity", "parent_package", "edge_alias"}, {"package_id", "version", "registry", "integrity", "parent_package", "edge_alias"}, "installation.companions[]")
            for field in ("package_id", "version", "parent_package", "edge_alias"):
                string(companion[field], "installation.companions[]." + field)
            if companion["package_id"] in packages:
                raise ValueError("companion package identity is duplicated")
            if companion["parent_package"] not in packages:
                raise ValueError("companions must follow their declared material parent dependency")
            if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", companion["version"]):
                raise ValueError("companion version must be an exact release")
            packages.add(companion["package_id"])
            url_identity(companion["registry"])
            validate_integrity(companion["integrity"], "installation.companions[].integrity")
    elif profile == "npm":
        if selector["kind"] != "version":
            raise ValueError("npm profiles require an exact version selector")
        registry = string(install.get("registry"), "installation.registry")
        url_identity(registry)
        validate_npm_package({**install, "package_id": resource["package_id"], "version": selector["value"]}, registry, "installation")
        companions = install.get("companions", [])
        if not isinstance(companions, list):
            raise ValueError("installation.companions must be a list")
        packages = {resource["package_id"]}
        fields = {"package_id", "version", "dependency_section", "archive_url", "archive_integrity", "integrity"}
        for companion in companions:
            mapping(companion, fields, fields, "installation.companions[]")
            validate_npm_package(companion, registry, "installation.companions[]")
            if companion["package_id"] in packages:
                raise ValueError("companion package identity is duplicated")
            packages.add(companion["package_id"])
    elif profile == "asset":
        if not HEX256.fullmatch(str(install.get("asset_sha256", ""))):
            raise ValueError("asset profile requires the reviewed asset SHA256")
    else:
        checker = within(root, install.get("custom_checker"))
        if (check_documents and not checker.is_file()) or not str(install["custom_checker"]).startswith("scripts/"):
            raise ValueError("custom profile requires an existing child-owned scripts/ checker")
    return data


def child_identity(root: Path) -> dict[str, Any]:
    contract = load_contract(root, check_documents=False)
    resource = contract["resource"]
    return {"slug": resource["slug"], "canonical_url": resource["canonical_url"], "package_id": resource["package_id"], "devforum_url": resource["devforum_url"], "version": resource["selector"]["value"]}
