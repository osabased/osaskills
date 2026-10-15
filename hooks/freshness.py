"""SessionStart hook: note outdated skill pins and library skills the project should clone.

The freshness note appears at most once a day, when a tracked tool or library has a newer stable
release than the skills were reviewed against. The clone note appears when the project declares a
cataloged library at its catalog pin without a current clone of that library's skill, or holds a
clone that differs from the catalog. Prints nothing otherwise. Never fails the session: an error
drops only the note it occurred in.
"""
from __future__ import annotations

from functools import partial
import importlib.util
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "roblox-resource-acquisition" / "scripts"
SKILLS = {
    "roblox-resource-acquisition": "references/keeping-current.md",
    "structure-roblox-projects": "references/keeping-current.md",
}
CLONE_REASONS = {
    "missing": "the project declares this library at the catalog pin and has no skill for it",
    "stale": "the clone differs from the catalog (a catalog fix, or a local edit that a refresh overwrites)",
    "other-pin": "the clone targets another pin; the project now declares the catalog pin",
}


def freshness_note() -> str:
    import check_updates

    data_dir = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or check_updates.DEFAULT_CACHE.parent)
    data_dir.mkdir(parents=True, exist_ok=True)
    manifests = [ROOT / "skills" / name / "versions.json" for name in SKILLS]
    results = check_updates.check([m for m in manifests if m.exists()], data_dir / "update-check.json", 24)
    outdated = [r for r in results if r["status"] == "outdated"]
    if not outdated:
        return ""
    lines = ["osaskills freshness check: these Roblox skills were reviewed against older releases than the latest."]
    for r in outdated:
        skill = Path(r["manifest"]).parent.name
        lines.append(f"- {r['name']} ({skill}): reviewed {r['reviewed']}, latest {r['latest']} - {r['url']}")
    lines.append(
        "Only if this session uses one of these skills: mention the relevant item when the task depends on it, "
        "finish the user's task, then update the skill as its keeping-current reference describes "
        f"({', '.join(f'{name}/{path}' for name, path in SKILLS.items())}): one pull request per item, "
        "skipping items that already have an open PR. Never change the user's project pins for this."
    )
    return "\n".join(lines)


def clone_note(project: Path) -> str:
    # _common exits the process when PyYAML is missing, which `except Exception` would not catch.
    if sys.version_info < (3, 11) or importlib.util.find_spec("yaml") is None:
        return ""
    import clone_children

    due = [
        row for row in clone_children.status(project)
        if (row["clone"] == "stale" and row["declared"]["status"] != "FAIL")
        or (row["clone"] in ("missing", "other-pin") and row["declared"]["status"] == "PASS")
    ]
    if not due:
        return ""
    lines = [f"osaskills library skills: these catalog skills are not current in {project / '.claude' / 'skills'}."]
    lines += [f"- {row['child']}: {CLONE_REASONS[row['clone']]}" for row in due]
    lines.append(
        "Only for the ones this session's task uses: clone or refresh them with "
        f'`"{sys.executable}" "{SCRIPTS / "clone_children.py"}" --project "{project}" <names>`, '
        "then read each clone's SKILL.md, since it loads as a skill only from the next session. "
        "Check a stale clone for local edits before refreshing it. Leave the others alone."
    )
    return "\n".join(lines)


def main() -> int:
    sys.path.insert(0, str(SCRIPTS))
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    notes = []
    for write_note in (freshness_note, partial(clone_note, project)):
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
