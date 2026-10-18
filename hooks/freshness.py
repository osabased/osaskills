"""SessionStart hook: note pins that differ from the skills, library skills to clone, and pin mismatches.

The pin note compares the tool versions in the project's rokit.toml or aftman.toml with the versions
structure-roblox-projects was reviewed against, locally and without network, and names each tool whose
pin differs. The library note names catalog skills the project should clone or refresh: it declares a
cataloged library at its catalog pin without a current clone, or holds a clone that differs from the
catalog. It also names cloned skills whose pin the project's manifest or lock contradicts. Prints nothing
otherwise. Never fails the session: an error drops only the note it occurred in.
"""
from __future__ import annotations

from functools import partial
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "roblox-resource-acquisition" / "scripts"
VERSIONS = ROOT / "skills" / "structure-roblox-projects" / "versions.json"
TOOL_MANIFESTS = ("rokit.toml", "aftman.toml")
CLONE_REASONS = {
    "missing": "the project declares this library at the catalog pin and has no skill for it",
    "stale": "the clone differs from the catalog (a catalog fix, or a local edit that a refresh overwrites)",
    "other-pin": "the clone targets another pin; the project now declares the catalog pin",
}


def pinned_tools(project: Path) -> dict[str, str]:
    import tomllib

    pins: dict[str, str] = {}
    for name in TOOL_MANIFESTS:
        try:
            tools = tomllib.loads((project / name).read_text(encoding="utf-8")).get("tools", {})
        except (OSError, ValueError):
            continue
        for spec in tools.values():
            if isinstance(spec, str) and "@" in spec:
                repo, version = spec.rsplit("@", 1)
                pins.setdefault(repo.lower(), version)
    return pins


def pin_note(project: Path) -> str:
    if sys.version_info < (3, 11):
        return ""
    import check_updates

    pins = pinned_tools(project)
    lines = []
    for item in json.loads(VERSIONS.read_text(encoding="utf-8"))["items"]:
        pinned = pins.get(item["source"].get("github", "").lower())
        if pinned is None:
            continue
        have, reviewed = check_updates.parse_version(pinned), check_updates.parse_version(item["reviewed"])
        if have is not None and have == reviewed:
            continue
        direction = ""
        if have is not None and reviewed is not None:
            direction = " (newer pin)" if (have[0], not have[1]) > (reviewed[0], not reviewed[1]) else " (older pin)"
        lines.append(f"- {item['name']}: project pins {pinned.split('+')[0]}, skill reviewed {item['reviewed']}{direction}")
    if not lines:
        return ""
    return "\n".join([
        "osaskills tool pins: the project pins different versions than structure-roblox-projects was reviewed against.",
        *lines,
        "Only if this session's task depends on that tool's guidance in structure-roblox-projects: for a newer pin, "
        "check the release notes between the two versions for the claims the task uses and follow the newer behavior; "
        "for an older pin, confirm those claims at the pinned version. Tell the user in one line. "
        "Never change the project's pins to fit the skill. Offer to update the skill only after the task, "
        "as references/keeping-current.md describes.",
    ])


def library_note(project: Path) -> str:
    # _common exits the process when PyYAML is missing, which `except Exception` would not catch.
    if sys.version_info < (3, 11) or importlib.util.find_spec("yaml") is None:
        return ""
    import clone_children

    due, mismatched = [], []
    for row in clone_children.status(project):
        declared, clone = row["declared"]["status"], row["clone"]
        if (clone == "stale" and declared != "FAIL") or (clone in ("missing", "other-pin") and declared == "PASS"):
            due.append(row)
        elif clone in ("current", "stale") and declared == "FAIL":
            mismatched.append((row["child"], row["pin"], row["declared"]["reason"]))
        elif clone == "other-pin" and row["clone_declared"]["status"] == "FAIL":
            mismatched.append((row["child"], row["clone_pin"], row["clone_declared"]["reason"]))
    sections = []
    if due:
        lines = [f"osaskills library skills: these catalog skills are not current in {project / '.claude' / 'skills'}."]
        lines += [f"- {row['child']}: {CLONE_REASONS[row['clone']]}" for row in due]
        lines.append(
            "Only for the ones this session's task uses: clone or refresh them before using the library, with "
            f'`"{sys.executable}" "{SCRIPTS / "clone_children.py"}" --project "{project}" <names>`, '
            "then read each clone's SKILL.md, since it loads as a skill only from the next session. "
            "Don't read the catalog copy in place instead; the clone is what later sessions get. "
            "Check a stale clone for local edits before refreshing it. Leave the others alone."
        )
        sections.append("\n".join(lines))
    if mismatched:
        lines = ["osaskills library skills: the project's manifest or lock doesn't match the version these skills target."]
        lines += [f"- {child} (targets {pin}): {reason}" for child, pin, reason in mismatched]
        lines.append(
            "Only if this session's task uses one of these libraries: tell the user, keep the project's pin, "
            "use only API you can confirm at the project's version, and stop where the task depends on behavior "
            "that may differ. Never change the pin to fit the skill; if the user wants the skill's version, "
            "follow roblox-resource-acquisition's upgrade flow."
        )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def main() -> int:
    sys.path.insert(0, str(SCRIPTS))
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    notes = []
    for write_note in (partial(pin_note, project), partial(library_note, project)):
        try:
            notes.append(write_note())
        except Exception:  # noqa: BLE001 - one failing note must not hide the other or break session start
            pass
    text = "\n\n".join(note for note in notes if note)
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - a freshness hint must never break session start
        sys.exit(0)
