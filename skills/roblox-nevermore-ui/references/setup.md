# Nevermore setup, imports and loader

## Restore the packages

The project declares exact direct npm pins in `package.json`, locked in `package-lock.json`:

| Package | Version |
| --- | --- |
| `@quenty/blend` | 12.50.1 |
| `@quenty/rx` | 13.34.1 |
| `@quenty/brio` | 14.37.1 |
| `@quenty/loader` | 10.11.2 |

- Restore with the project's own preparation command. The reviewed project used `scripts/prepare.ps1`, which runs `npm ci --ignore-scripts`. Keep dependency scripts disabled unless they have been reviewed.
- Don't edit `node_modules`, and don't regenerate the lock to hide a mismatch.
- The parent's npm check compares each direct declaration, the lock's registry URL and SHA-512 integrity, the installed `package.json` version, and the reviewed Lua source. It doesn't check transitive packages or runtime behavior.

## The shared adapter

The reviewed project used a frozen adapter at `src/shared/Nevermore.luau`, mapped to `ReplicatedStorage.Shared.Nevermore`, that exposes `Blend`, `Rx` and `Brio`:

```luau
local Nevermore = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Nevermore"))
local Blend = Nevermore.Blend
```

This is that project's binding, not a universal path. Read the actual project's guide, Rojo mappings, adapter and startup code before changing it. Requiring the raw `Blend.lua` fails unless the loader has populated its sibling `loader` link.

## Loader entry points (`@quenty/loader` 10.11.2)

| Call | Use |
| --- | --- |
| `loader.bootstrapGame(packagesRoot, options?)` | Game runtime. Populates the package root and replicates client and shared packages. In Studio it takes a fast path unless `options.skipStudioFastPath = true`. |
| `loader.bootstrapPlugin(packagesRoot, options?)` | Edit mode or plugins. |
| `loader.bootstrapStory(storyScript, options?)` | Story files: finds the top `node_modules` above the story and returns a loader for it. |
| `loader.load(packagesOrModuleScript)` | Creates a loader without bootstrapping. |

A loader is callable: `local require = loader; require("Blend")` resolves a package by name. `LoaderUtils` is not the public module.

## Ownership

- Bootstrap exactly once per package root and runtime, in the root owner (in the reviewed game, `ServerScriptService.Nevermore` was set up on the server before Bootstrapper's phases ran, and clients waited for the filtered replicated packages). Components borrow the loader.
- Keep `skipStudioFastPath = true` when Studio must use production-equivalent filtering, so server-only packages don't show up on the client.
- Destroy only a loader your adapter created, once, at the package root's end of life. `Loader:Destroy()` runs its Maid's cleaning and removes the metatable, so it can't be called twice. The global package tracker is shared infrastructure; never reset it as feature cleanup.
- Don't introduce ServiceBag or replace Bootstrapper just to load UI libraries.

Source: [loader 10.11.2 at the reviewed commit](https://github.com/Quenty/NevermoreEngine/blob/7ab0297833aa73c193d8c20dc23332280439af7c/src/loader/src/init.lua).
