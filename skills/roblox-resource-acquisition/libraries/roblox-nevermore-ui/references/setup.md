# Nevermore setup, imports and loader

## Restore the packages

The project declares exact direct npm pins in `package.json`, locked in `package-lock.json`:

| Package | Version |
| --- | --- |
| `@quenty/blend` | 12.50.2 |
| `@quenty/rx` | 13.34.2 |
| `@quenty/brio` | 14.37.2 |
| `@quenty/loader` | 10.11.3 |

- Restore with the project's own preparation command. The reviewed project used `scripts/prepare.ps1`, which runs `npm ci --ignore-scripts`. Keep dependency scripts disabled unless they have been reviewed.
- Don't edit `node_modules`, and don't regenerate the lock to hide a mismatch.
- The pin check (this skill's `## Check the pin`, or `roblox-resource-acquisition`'s `--status`) compares each direct declaration with the lock's entry, registry URL and SHA-512 integrity. It doesn't read installed packages, transitive packages or runtime behavior.

## The shared adapter

The reviewed project used a frozen adapter at `src/shared/Nevermore.luau`, mapped to `ReplicatedStorage.Shared.Nevermore`, that exposes `Blend`, `Rx` and `Brio`:

```luau
local Nevermore = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Nevermore"))
local Blend = Nevermore.Blend
```

This is that project's binding, not a universal path. Read the actual project's guide, Rojo mappings, adapter and startup code before changing it. Requiring the raw `Blend.lua` fails unless the loader has populated its sibling `loader` link.

## Loader entry points (`@quenty/loader` 10.11.3)

| Call | Use |
| --- | --- |
| `loader.bootstrapGame(packagesRoot, options?)` | Game runtime. Populates the package root and replicates client and shared packages. In Studio it takes a fast path unless `options.skipStudioFastPath = true`. |
| `loader.bootstrapPlugin(packagesRoot, options?)` | Edit mode or plugins. |
| `loader.bootstrapStory(storyScript, options?)` | Story files: finds the top `node_modules` above the story and returns a loader for it. Since 10.11.3 it skips link population when every folder under the root already has its loader link, so repeat calls no longer pin a new set of link creators. Each call still registers the root with the loader module's package tracker. |
| `loader.load(packagesOrModuleScript)` | Creates a loader without bootstrapping. |

A loader is callable: `local require = loader; require("Blend")` resolves a package by name. `LoaderUtils` is not the public module.

## Ownership

- Bootstrap exactly once per package root and runtime, in the root owner (in the reviewed game, `ServerScriptService.Nevermore` was set up on the server before Bootstrapper's phases ran, and clients waited for the filtered replicated packages). Components borrow the loader.
- Keep `skipStudioFastPath = true` when Studio must use production-equivalent filtering, so server-only packages don't show up on the client.
- Destroy only a loader your adapter created, once, at the package root's end of life. `Loader:Destroy()` runs its Maid's cleaning and removes the metatable, so it can't be called twice. The global package tracker is shared infrastructure; never reset it as feature cleanup.
- Don't introduce ServiceBag or replace Bootstrapper just to load UI libraries.

Story hot-reload memory: before 10.11.3, every `bootstrapStory` call left a full set of loader-link creators alive (about 6 MB per call on a root with ~1,500 links). 10.11.3 fixes that half. If the story host re-runs the loader module on each reload, each fresh module instance still adds its own package tracker for the same root, which also grows (upstream [#832](https://github.com/Quenty/NevermoreEngine/pull/832)). For long hot-reload sessions, prefer a shared edit-mode adapter that bootstraps once and that stories borrow.

Source: [loader 10.11.3 at the reviewed commit](https://github.com/Quenty/NevermoreEngine/blob/3286fd397c9c42e7f29c8a881ac7dde12887e783/src/loader/src/init.lua).
