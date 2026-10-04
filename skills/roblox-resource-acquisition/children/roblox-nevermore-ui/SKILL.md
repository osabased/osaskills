---
name: roblox-nevermore-ui
description: Use the active project's exact pinned Blend, Rx, Brio, and Nevermore loader for declarative Luau UI, reactive flow, lifetime cleanup, and package imports. Preserve Bootstrapper application startup; exclude framework selection and dependency upgrades.
---

# Nevermore UI

Use this project-local skill in an active Roblox project that declares the exact
pins below. Resolve the supplied project root, then check its manifests, Rojo
mappings and shared import adapter against the reviewed topology described
here before using it. Preserve the project's owned target and startup roles.
Run project commands from that root; resolve scripts and authored source
paths against it rather than this shared skill package. A different adapter
or topology needs affected integration checks before inheriting this guidance.
Read only the references needed for the task; combine them when a feature
crosses library boundaries. Default adoption of this bundled child is project-local.

| Task | Reference |
| --- | --- |
| UI composition, reactive properties, mounts, or UI Labs stories | [Blend](references/blend.md) |
| Observable pipelines, state/event flow, or signal/promise adapters | [Rx](references/rx.md) |
| Value lifetimes, lifetime-owned work, or stale-value handling | [Brio](references/brio.md) |

## Adopted target

| npm package | Version | Role |
| --- | --- | --- |
| @quenty/blend | 12.50.1 | Declarative UI |
| @quenty/rx | 13.34.1 | Observable composition |
| @quenty/brio | 14.37.1 | Value lifetimes |
| @quenty/loader | 10.11.2 | Package resolution/replication |

All four are MIT licensed and source-qualified against NevermoreEngine commit
7ab0297833aa73c193d8c20dc23332280439af7c on 2026-10-03. Preserve package.json's
exact direct pins and package-lock.json. Restore through scripts/prepare.ps1;
npm uses ci with --ignore-scripts. Never edit generated packages. pesde retains
the common stack; Bootstrapper retains Controller/Service init/start ownership.
ServiceBag is outside this project setup.

## Shared imports and placement

src/shared/Nevermore.luau exports a frozen table containing Blend, Rx, and Brio.
Use that adapter, then select the library needed:

```luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Nevermore = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Nevermore"))
local Blend = Nevermore.Blend
```

The adapter owns one loader for its package root's lifetime and destroys it with
that root. Studio edit previews use bootstrapPlugin. Game server startup requires
the adapter before Bootstrapper phases; clients wait for the replicated packages.
ServerScriptService.Nevermore is the server package root. skipStudioFastPath=true
keeps filtered replication in Studio as well as production; clients use the
replicated root and its loader. Privileged modules belong on the server.

Read the adapter before changing imports or adding dependencies. Raw Blend.lua
requires a runtime-populated sibling loader link. Do not start a loader per
component or require LoaderUtils as the loader.

## Shared ownership

- Own Rx/Blend subscriptions explicitly, for example owner:Add(subscription, "Destroy") with Janitor. Establish cleanup ownership before activation and roll back acquired resources when construction fails.
- Janitor does not guarantee cleanup order. Stop producers before destroying their UI consumers when that order matters.
- Keep owned state, subscriptions, and instances reachable for rollback; dispose partial acquisitions and rethrow failures. Dispose mounted views before their owner state.
- Keep feature and view lifetimes separate. Do not destroy the shared package loader or another feature's resources. LemonSignal remains the project's discrete event primitive.

## Verification boundary

These are source-grounded instructions, not maintained executable examples.
Run locked restoration and scripts/check.ps1 after implementation changes.
Static/source/artifact checks establish package identity and mapped source;
engine claims require the affected mount/update/unmount path to run in Studio,
including checking that late emissions cannot reach disposed UI.

## Sources

- [Nevermore source at the adopted commit](https://github.com/Quenty/NevermoreEngine/tree/7ab0297833aa73c193d8c20dc23332280439af7c/src)
- [Loader API](https://quenty.github.io/NevermoreEngine/api/loader/)
