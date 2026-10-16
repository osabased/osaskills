"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
GUARDS = [
    ("src/client/UI", "*.luau", re.compile(r"Instance\.new"), "build UI Instances with Vide's create"),
]


def main() -> int:
    failures = []
    for folder, pattern, banned, reason in GUARDS:
        for path in sorted((ROOT / folder).rglob(pattern)):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if banned.search(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: {reason}")
    for failure in failures:
        print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
