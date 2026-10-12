"""SessionStart hook: note outdated pins in the Roblox skills, quietly and at most once a day.

Prints nothing unless a tracked tool or library has a newer stable release than the skills
were reviewed against. Never fails the session: any error exits 0 without output.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SKILLS = {
    "roblox-resource-acquisition": "references/keeping-current.md",
    "structure-roblox-projects": "references/core/keeping-current.md",
}


def main() -> int:
    sys.path.insert(0, str(ROOT / "skills" / "roblox-resource-acquisition" / "scripts"))
    import check_updates

    data_dir = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or check_updates.DEFAULT_CACHE.parent)
    data_dir.mkdir(parents=True, exist_ok=True)
    manifests = [ROOT / "skills" / name / "versions.json" for name in SKILLS]
    results = check_updates.check([m for m in manifests if m.exists()], data_dir / "update-check.json", 24)
    outdated = [r for r in results if r["status"] == "outdated"]
    if not outdated:
        return 0
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
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - a freshness hint must never break session start
        sys.exit(0)
