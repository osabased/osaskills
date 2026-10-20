"""PreToolUse hook for eval runs: block WebFetch of the public repo that holds this eval's answer key."""
import json, re, sys

url = (json.load(sys.stdin).get("tool_input") or {}).get("url") or ""
if re.search(r"osabased", url, re.I):
    print("Fetching this URL is blocked in this environment.", file=sys.stderr)
    sys.exit(2)
