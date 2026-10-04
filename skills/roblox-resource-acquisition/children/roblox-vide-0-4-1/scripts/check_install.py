"""Read-only identity and installed-source check for canonical Vide 0.4.1."""
import argparse
import hashlib
import re
import sys
import tomllib
from pathlib import Path

REPO = "https://github.com/centau/vide"
COMMIT = "5ed4c01940e6bd578fb83253cfbeda0a6c05177c"
TREE = "8890f5044158a71592249e2d91646715b98ca4aa"
DIGEST = "73ac80a420cb550e9ae20d3f8115d5684409dbba7c3b11db2c7ee666d87fcf65"

def check(manifest, lock, package_dir=None):
    declaration = tomllib.loads(manifest.read_text(encoding="utf-8-sig"))["dependencies"]["vide"]
    if declaration != {"repo": REPO, "rev": COMMIT}:
        raise ValueError("Vide declaration differs from the reviewed canonical commit")
    entries = tomllib.loads(lock.read_text(encoding="utf-8-sig"))["graph"]
    if not isinstance(entries, dict):
        raise ValueError("Lock graph must be a mapping")
    entry = entries["centau/vide@0.0.0-" + TREE + " roblox"]
    if not isinstance(entry, dict):
        raise ValueError("Vide lock entry must be a mapping")
    if entry.get("direct") != ["vide", {"repo": REPO, "rev": COMMIT}, "standard"]:
        raise ValueError("Vide direct lock entry differs")
    ref = entry["pkg_ref"]
    if not isinstance(ref, dict):
        raise ValueError("Vide Git package reference must be a mapping")
    if ref.get("ref_ty") != "git" or ref.get("repo") != REPO or ref.get("tree_id") != TREE:
        raise ValueError("Vide canonical Git lock tree differs")
    if package_dir is None:
        return "declared commit/tree"
    source = package_dir / "src"
    files = sorted(source.glob("*.luau"), key=lambda item: item.name)
    if not files:
        raise ValueError("Installed Vide source is missing")
    payload = "\n".join(item.name + " " + hashlib.sha256(item.read_bytes()).hexdigest() for item in files).encode()
    if hashlib.sha256(payload).hexdigest() != DIGEST:
        raise ValueError("Installed Vide source digest differs")
    header = (source / "lib.luau").read_text(encoding="utf-8")
    for field, expected in (("major", 0), ("minor", 4), ("patch", 1)):
        match = re.search(r"\b" + field + r"\s*=\s*(\d+)", header)
        if not match or int(match[1]) != expected:
            raise ValueError("Installed Vide runtime version differs")
    return "installed commit/tree, runtime 0.4.1 and source digest " + DIGEST

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--declared", action="store_true")
    modes.add_argument("--package-dir", type=Path)
    args = parser.parse_args()
    try:
        result = check(args.manifest, args.lock, args.package_dir)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL: " + str(error))
        return 1
    print("PASS: canonical Vide " + COMMIT + "; " + result)
    return 0

if __name__ == "__main__":
    sys.exit(main())

