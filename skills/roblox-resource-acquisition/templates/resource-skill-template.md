---
name: roblox-LIBRARY
description: LIBRARY (OWNER/REPO) for Roblox Luau, pinned VERSION. Use when CONCRETE-TRIGGERS-WITH-API-AND-FILE-NAMES. Not for ONE-SHORT-EXCLUSION.
---

# LIBRARY VERSION

Pinned target: `SELECTOR-VALUE` (source reviewed YYYY-MM-DD). [resource.yaml](resource.yaml) holds the exact identity.

## Check the pin

Before relying on version-specific guidance, read the project's manifest and lock:

- `MANIFEST` declares `MANIFEST-ENTRY`, and `LOCK` resolves it to `LOCK-KEY`.

If they show another version, tell the user, keep the project's pin, use only API you can confirm at that version, and stop where the task depends on behavior that may differ. If the user wants this skill's version instead, upgrade through the `roblox-resource-acquisition` skill. If the project doesn't declare LIBRARY, this skill is advice only. Stop on a blocked use noted in the project's `CLAUDE.md`. Say what you checked; reading the manifest is not a runtime test.

## Core API

| Call | Returns | Notes |
| --- | --- | --- |
| `SOURCE-GROUNDED-CALL` | RESULT | OWNERSHIP-OR-SIDE-NOTE |

## Example

```luau
-- 8–15 lines derived from the reviewed source or the maintained fixture.
```

## Gotchas

- PIN-SPECIFIC-BEHAVIOR (cleanup order, cancellation limits, client/server boundary, security).

## Read further

- READ-WHEN-CONDITION: read [setup](references/setup.md).
- Wrong or missing guidance at this pin: report it with the smallest reproduction and the exact proposed fix. Fix it in the `roblox-resource-acquisition` catalog, not here, because re-cloning overwrites local edits.
