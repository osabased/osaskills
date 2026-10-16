"""Print one plugin version's library-skill session note for the project in the working directory.

Stands in for the plugin's SessionStart hook, which a project-only run doesn't load. It prints only
the library note: the daily freshness note depends on the network and the day. Usage:
    python session_hook.py <plugin root with skills/ and hooks/>
"""
import importlib.util
import os
from pathlib import Path
import sys

root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("freshness", root / "hooks" / "freshness.py")
freshness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(freshness)
sys.path.insert(0, str(freshness.SCRIPTS))
note = getattr(freshness, "library_note", None) or freshness.clone_note
# The run may execute `python ...` only, so the note's interpreter path is shortened to match.
print(note(Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())).replace(f'"{sys.executable}"', "python"))
