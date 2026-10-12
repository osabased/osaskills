#!/usr/bin/env python3
"""Report tools and libraries that have a newer stable release than this skill last reviewed.

Reads one or more versions.json manifests (default: the one beside this script's skill) and
asks the item's source for its latest stable version: the Wally index, the npm registry, or
GitHub releases (falling back to tags). Use the registry a library actually publishes to;
some projects stop tagging GitHub releases while still publishing packages.
Standard library only. Results are cached for a day so routine use costs one lookup per day.

Exit codes: 0 everything current; 1 at least one item is outdated; 2 no item could be checked.
Set GITHUB_TOKEN or GH_TOKEN to raise GitHub's anonymous rate limit (60 requests an hour).

This file is kept identical in roblox-resource-acquisition and structure-roblox-projects.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")
DEFAULT_MANIFEST = Path(__file__).resolve().parent.parent / "versions.json"
DEFAULT_CACHE = Path(tempfile.gettempdir()) / "osaskills-update-check.json"
TIMEOUT = 15


def parse_version(text: str) -> tuple[tuple[int, int, int], bool] | None:
    """Parse `v1.2.3`, `name@1.2.3` or `1.2` into ((1, 2, 3), is_prerelease)."""
    candidate = str(text).strip().rsplit("@", 1)[-1].rsplit("/", 1)[-1].lstrip("vV")
    match = VERSION.search(candidate)
    if not match or match.start() != 0:
        return None
    major, minor, patch, pre = match.groups()
    return (int(major), int(minor), int(patch or 0)), pre is not None


def newest(tags: list[tuple[str, str]], allow_prerelease: bool) -> tuple[str, str] | None:
    """Pick the highest version among (tag, url) pairs."""
    best = None
    for tag, url in tags:
        parsed = parse_version(tag)
        if parsed is None or (parsed[1] and not allow_prerelease):
            continue
        if best is None or parsed[0] > best[0]:
            best = (parsed[0], tag, url)
    return (best[1], best[2]) if best else None


def fetch_json(url: str):
    headers = {"Accept": "application/json", "User-Agent": "osaskills-update-check"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=TIMEOUT) as response:
        return json.load(response)


def latest_github(repo: str, allow_prerelease: bool, tag_prefix: str = "") -> tuple[str, str]:
    base = f"https://api.github.com/repos/{repo}"
    releases = fetch_json(f"{base}/releases?per_page=50")
    pairs = [
        (release["tag_name"].removeprefix(tag_prefix), release["html_url"])
        for release in releases
        if not release.get("draft") and release["tag_name"].startswith(tag_prefix)
        and (allow_prerelease or not release.get("prerelease"))
    ]
    found = newest(pairs, allow_prerelease)
    if found is None:
        tags = fetch_json(f"{base}/tags?per_page=100")
        pairs = [
            (tag["name"].removeprefix(tag_prefix), f"https://github.com/{repo}/releases/tag/{urllib.parse.quote(tag['name'])}")
            for tag in tags if tag["name"].startswith(tag_prefix)
        ]
        found = newest(pairs, allow_prerelease)
    if found is None:
        raise LookupError(f"no versioned releases or tags in {repo}")
    return found


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "osaskills-update-check"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8")


def latest_wally(package: str, allow_prerelease: bool) -> tuple[str, str]:
    """The Wally index stores one JSON manifest per published version, one per line."""
    scope, name = package.lower().split("/", 1)
    text = fetch_text(f"https://raw.githubusercontent.com/UpliftGames/wally-index/main/{scope}/{name}")
    versions = [json.loads(line)["package"]["version"] for line in text.splitlines() if line.strip()]
    found = newest([(version, f"https://wally.run/package/{scope}/{name}?version={version}") for version in versions], allow_prerelease)
    if found is None:
        raise LookupError(f"no versions for {package} in the Wally index")
    return found


def latest_npm(package: str) -> tuple[str, str]:
    data = fetch_json(f"https://registry.npmjs.org/{urllib.parse.quote(package, safe='@')}/latest")
    return data["version"], f"https://www.npmjs.com/package/{package}/v/{data['version']}"


def lookup(source: dict, allow_prerelease: bool) -> tuple[str, str]:
    if "github" in source:
        return latest_github(source["github"], allow_prerelease, source.get("tag_prefix", ""))
    if "npm" in source:
        return latest_npm(source["npm"])
    if "wally" in source:
        return latest_wally(source["wally"], allow_prerelease)
    raise ValueError(f"unsupported source {source!r}")


def load_cache(path: Path, max_age: float) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    now = time.time()
    return {key: value for key, value in data.items() if isinstance(value, dict) and now - value.get("checked", 0) < max_age}


def save_cache(path: Path, cache: dict) -> None:
    try:
        path.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")
    except OSError:
        pass  # A read-only temp dir only costs a repeat lookup.


def check(manifests: list[Path], cache_path: Path | None, max_age_hours: float) -> list[dict]:
    cache = load_cache(cache_path, max_age_hours * 3600) if cache_path else {}
    entries = []
    for manifest in manifests:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("schema") != 1:
            raise ValueError(f"{manifest}: unsupported versions.json schema")
        for item in data["items"]:
            allow_prerelease = bool(item.get("prerelease", False))
            entries.append((manifest, item, allow_prerelease, json.dumps([item["source"], allow_prerelease], sort_keys=True)))

    def fetch(entry):
        _, item, allow_prerelease, key = entry
        try:
            latest, url = lookup(item["source"], allow_prerelease)
            return key, {"latest": latest, "url": url, "checked": time.time()}
        except (OSError, urllib.error.URLError, ValueError, LookupError, KeyError, TypeError) as exc:
            return key, {"error": str(exc)}

    missing = {entry[3]: entry for entry in entries if entry[3] not in cache}
    with ThreadPoolExecutor(max_workers=8) as pool:
        fetched = dict(pool.map(fetch, missing.values()))
    cache.update({key: value for key, value in fetched.items() if "error" not in value})

    results = []
    for manifest, item, _, key in entries:
        result = {"manifest": str(manifest), "id": item["id"], "name": item["name"], "reviewed": item["reviewed"], "files": item.get("files", [])}
        found = cache.get(key) or fetched.get(key, {})
        if "latest" in found:
            reviewed, current = parse_version(item["reviewed"]), parse_version(found["latest"])
            if reviewed is None or current is None:
                result.update(status="unknown", reason=f"cannot compare {item['reviewed']!r} with {found['latest']!r}")
            else:
                result.update(latest=found["latest"].lstrip("vV"), url=found["url"], status="outdated" if current[0] > reviewed[0] else "current")
        else:
            result.update(status="unknown", reason=found.get("error", "not checked"))
        results.append(result)
    if cache_path:
        save_cache(cache_path, cache)
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("manifests", nargs="*", type=Path, help="versions.json files (default: this skill's)")
    parser.add_argument("--json", action="store_true", help="print one JSON array instead of text")
    parser.add_argument("--no-cache", action="store_true", help="always query upstream")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE, help=f"cache file (default {DEFAULT_CACHE})")
    parser.add_argument("--max-age-hours", type=float, default=24.0)
    args = parser.parse_args(argv)
    results = check(args.manifests or [DEFAULT_MANIFEST], None if args.no_cache else args.cache, args.max_age_hours)
    if args.json:
        print(json.dumps(results, indent=1))
    else:
        for result in results:
            if result["status"] == "outdated":
                print(f"OUTDATED {result['id']}: reviewed {result['reviewed']}, latest {result['latest']} ({result['url']})")
            elif result["status"] == "unknown":
                print(f"UNKNOWN  {result['id']}: {result['reason']}")
            else:
                print(f"current  {result['id']} {result['reviewed']}")
    if results and all(result["status"] == "unknown" for result in results):
        return 2
    return 1 if any(result["status"] == "outdated" for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
