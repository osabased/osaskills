---
name: roblox-LIBRARY
description: LIBRARY (OWNER/REPO) for Roblox Luau, pinned VERSION. Use when CONCRETE-TRIGGERS-WITH-API-AND-FILE-NAMES. Not for ONE-SHORT-EXCLUSION.
---

# LIBRARY VERSION

Pinned target: `SELECTOR-VALUE` (source reviewed YYYY-MM-DD). [resource.yaml](resource.yaml) holds the exact identity.

## Check the pin

If the project pins this library, confirm it matches the target. If the `roblox-resource-acquisition` skill is installed beside this one, run its checks per [child usage](../roblox-resource-acquisition/references/child-usage.md). If the parent, Python, or a project record is unavailable, read the project's manifest/lock directly and say which checks were skipped. Stop only on a `FAIL`, `MISMATCH`, `BLOCKED` or `FAILED` result, an observed mismatch, or an explicit block.

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
