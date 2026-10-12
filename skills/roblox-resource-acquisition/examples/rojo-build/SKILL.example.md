---
name: roblox-rojo-build-contract
description: Rojo (rojo-rbx/rojo) CLI for Roblox, pinned 7.7.0. Use when a project needs a reproducible `rojo build` of default.project.json into an .rbxlx place and a check that the expected Script/LocalScript/ModuleScript instances are present. Not for live Studio sync (`rojo serve`) or proving gameplay runs.
---

# Rojo 7.7.0 build contract

Pinned target: `7.7.0` (source reviewed 2026-09-30). [resource.yaml](resource.example.yaml) holds the exact identity. This authoring example carries no executed upstream or host proof.

## Check the pin

The project's tool lock (for example `tool-lock.json`, `rokit.toml` or `aftman.toml`) should pin Rojo 7.7.0. `scripts/check_build.py` checks the executable's identity, version and hash against that lock before it runs anything; the shared checker reports this custom profile unavailable and never runs it. If the `roblox-resource-acquisition` skill is available (two folders up when this skill sits in its `libraries/` folder, otherwise beside this one), also run its record query per [child usage](../../references/child-usage.md). If the parent, Python or a project record is unavailable, run `rojo --version` and read the lock directly, and say which checks were skipped. Stop only on a `FAIL`, `MISMATCH`, `BLOCKED` or `FAILED` result, an observed mismatch, or an explicit block.

## Core API

| Command | Produces | Notes |
| --- | --- | --- |
| `rojo --version` | version string | Compare with the pinned 7.7.0. |
| `rojo build PROJECT --output PLACE.rbxlx` | XML place | Exit 0 proves the mapping built, not that it contains the intended scripts. |
| `scripts/check_build.py … --expected CONTRACT` | report JSON | Builds into a temp dir, checks script classes/sources, then replaces the output. |
| `scripts/smoke_build.py … --workspace DIR` | report JSON | Generates disposable inputs: one valid mapping, one with the server mapping omitted. |

## Example

```sh
python "$CHILD/scripts/check_build.py" --rojo "$ROJO" \
  --tool-lock "$PROJECT/tool-lock.json" \
  --project "$PROJECT/default.project.json" \
  --expected "$PROJECT/expected-scripts.json" \
  --output "$PROJECT/build/place.rbxlx" \
  --report "$PROJECT/build/report.json"
```

Pass: exit 0 and report status `passed`. An omitted mapping exits 1 and names the missing path (for example `ServerScriptService/Main`); the previous output stays byte-identical.

## Gotchas

- Derive the expected-scripts contract independently of `default.project.json`; a contract copied from a faulty mapping proves nothing.
- The helper owns only its temporary build, the requested output and the report. It never removes project source, tool caches or a running Studio.
- No `rojo serve` process is started; live sync is out of scope.
- Fake-tool tests prove wrapper behavior only. Neither the fake nor the real CLI proves Studio gameplay or strict analysis.

## Read further

- Installing Rojo, the tool lock, or the qualification run: read [setup](references/setup.md).
- A build succeeds but scripts are missing, or another named symptom: read [troubleshooting](references/troubleshooting.md).
