"""Read-only metadata and local asset check for official UI Labs plugin 1.6.1."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

URL = "https://github.com/PepeElToro41/ui-labs/releases/download/v1.6.1/Plugin.rbxm"
DIGEST = "c785b1fc2593d633ad3dba51aeb778cee3026393574b99438fa276ad31d5283b"
NAME = "UILabsManagedPlugin.rbxm"

def check(metadata, plugin_dir):
    spec = json.loads(metadata.read_text(encoding="utf-8-sig"))["studioPlugins"]["uiLabs"]
    if not isinstance(spec, dict):
        raise ValueError("UI Labs metadata must be a mapping")
    for field, expected in (("version", "1.6.1"), ("url", URL), ("sha256", DIGEST), ("filename", NAME)):
        if spec.get(field) != expected:
            raise ValueError("UI Labs metadata differs: " + field)
    if hashlib.sha256((plugin_dir / NAME).read_bytes()).hexdigest() != DIGEST:
        raise ValueError("Installed UI Labs official asset digest differs")
    return "plugin 1.6.1; asset SHA256 " + DIGEST

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--plugin-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(args.metadata, args.plugin_dir)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL: " + str(error))
        return 1
    print("PASS: canonical UI Labs " + result)
    return 0

if __name__ == "__main__":
    sys.exit(main())

