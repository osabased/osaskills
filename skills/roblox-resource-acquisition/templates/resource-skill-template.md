---
name: roblox-LIBRARY
description: LIBRARY (OWNER/REPO) for Roblox Luau, pinned VERSION. Use when CONCRETE-TRIGGERS-WITH-API-AND-FILE-NAMES. Not for ONE-SHORT-EXCLUSION.
---

# LIBRARY VERSION

Pinned target: `SELECTOR-VALUE` (source reviewed YYYY-MM-DD). [resource.yaml](resource.yaml) holds the exact identity.

## Check the pin

If the project pins this library, confirm it matches the target. If the `roblox-resource-acquisition` skill is available (two folders up when this skill sits in its `libraries/` folder, otherwise beside this one), run its checks per [child usage](../../references/child-usage.md). If the parent or Python is unavailable, read the project's manifest/lock directly and say which checks were skipped. On a `FAIL` result or an observed mismatch, tell the user and keep the project's pin; continue with API you can confirm at the project's version, and stop only where the task depends on version-specific behavior. Stop on a blocked use noted in the project's `CLAUDE.md`.

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
