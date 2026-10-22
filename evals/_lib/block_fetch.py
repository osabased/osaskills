"""PreToolUse hook for eval runs: block WebFetch of URLs matching the regex given as the first argument."""
import json, re, sys

url = (json.load(sys.stdin).get("tool_input") or {}).get("url") or ""
if re.search(sys.argv[1], url, re.I):
    print("Fetching this URL is blocked in this environment.", file=sys.stderr)
    sys.exit(2)
