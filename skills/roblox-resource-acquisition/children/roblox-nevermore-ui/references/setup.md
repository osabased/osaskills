# Locked setup and shared imports

Use when installing/restoring the four npm packages or changing the adapter, package mapping, or loader ownership. The [entrypoint](../SKILL.md) owns common use and [resource.yaml](../resource.yaml) declares exact targets.

## Restore and inspect

The shared validators require Python 3.11+ and PyYAML; restore the installed parent's `requirements.txt` with uv when available. npm restoration requires the project's supported Node/npm version and an existing reviewed `package-lock.json`. Preserve exact direct pins for `@quenty/blend` 12.50.1, `@quenty/rx` 13.34.1, `@quenty/brio` 14.37.1 and `@quenty/loader` 10.11.2. Prefer the project's reviewed preparation command. The original topology used `scripts/prepare.ps1` and `npm ci --ignore-scripts`; resolve the actual project's equivalent before running it. Never edit generated `node_modules` or synthesize a new lock to hide a mismatch.

The npm profile checks package-lock format 2/3, each exact direct declaration, canonical registry archive URL/SHA512 integrity, installed package.json identity/version and reviewed Lua source aggregates. Default locations are `PROJECT/package.json`, `PROJECT/package-lock.json` and `PROJECT/node_modules/<resolved-alias>`. Supply `--manifest`, `--lock`, `--alias`, `--package-dir` or `--companion PACKAGE=DIR` only from actual project bindings. Every material companion still needs its matching direct manifest/lock declaration. The checker reads bytes; it runs no npm scripts or package code and does not establish transitive dependency or runtime health.

## Resolve the adapter

The reviewed project topology used a frozen shared adapter at `src/shared/Nevermore.luau`, exposing `Blend`, `Rx` and `Brio`. Its runtime mapping was `ReplicatedStorage.Shared.Nevermore`. If that actual mapping exists, consumers can use:

```luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Nevermore = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Nevermore"))
local Blend = Nevermore.Blend
```

These are project integration bindings, not universal Nevermore paths. Read the affected project's guide, Rojo mappings, adapter and startup code before changing them. Different topology requires affected integration checks.

## Loader lifetime

The root adapter owns bootstrap/population and replication. `loader.bootstrapGame(packages, options)` is the game route; `loader.bootstrapPlugin(packages, options)` is the edit/plugin route. Both operate on an actual package-root Instance. `loader.load(...)` creates a loader without bootstrapping; `LoaderUtils` is not the public loader module. Raw Blend.lua requires its runtime-populated sibling loader link.

Preserve one bootstrap owner for each package root/runtime. In the original game topology the server package root was `ServerScriptService.Nevermore`, the server initialized the adapter before Bootstrapper phases, and clients waited for filtered replicated packages. Preserve `skipStudioFastPath = true` when Studio must use the production filtering path; upstream's default Studio fast path is a different replication route. UI Labs story mounts borrow the adapter's edit-mode loader. Do not introduce ServiceBag or replace Bootstrapper merely to load UI libraries.

Destroy only a loader the adapter creates, once, at its package-root lifetime boundary. In 10.11.2, `Loader:Destroy()` cleans its Maid and removes its metatable, so repeated method calls are not an idempotent destroy contract. Its package-root tracker is shared infrastructure; avoid resetting it as feature cleanup. Read [troubleshooting](troubleshooting.md) for recovery and verification boundaries.

Source: [loader 10.11.2 at the reviewed commit](https://github.com/Quenty/NevermoreEngine/blob/7ab0297833aa73c193d8c20dc23332280439af7c/src/loader/src/init.lua).
