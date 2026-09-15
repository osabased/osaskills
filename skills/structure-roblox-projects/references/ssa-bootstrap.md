# Canonical SSA bootstrap and infrastructure

Use this reference for canonical SSA infrastructure work: creating the greenfield bootstrap, changing startup/discovery behavior, integrating or upgrading the loader, explicitly migrating toward canonical SSA, or changing loader-wide behavior. Ordinary feature work should use [`ssa.md`](ssa.md) without loading this file.

## Canonical loader

Canonical greenfield SSA uses:

```text
Repository: ActualFire-Games/module-loader
Package: crusherfire/module-loader@3.0.4
Commit: b427a3e03fe9368a26e344b5e37f7466fe2ca878
License: MIT
```

Keep loader identity, acquisition, and version mechanics in this infrastructure path rather than the ordinary feature path.

## Minimal bootstrap

The canonical bootstrap is one server entrypoint and one client entrypoint calling the upstream loader directly:

```text
ServerMain
  require canonical ModuleLoader
  ModuleLoader.Start(Server)

ClientMain
  require canonical ModuleLoader
  ModuleLoader.Start(Client)
```

Represent this through the target project's actual source-of-truth workflow. Do not insert an SSA runtime wrapper between the entrypoints and the selected loader.

Ordinary feature agents do not call `ModuleLoader.Start(...)`; bootstrap owns loader startup.

## Discovery

Canonical discovery keeps the upstream default:

```text
FolderSearchDepth = 1
```

Direct-child `ModuleScript`s beneath canonical `Server/` and `Client/` are lifecycle feature roots. Nested implementation modules belong under the owning feature root.

Conform the DataModel/filesystem to this discovery contract rather than expanding search depth to accommodate ordinary helpers.

## Loader-wide options

Advanced loader capabilities are infrastructure decisions. The canonical ordinary configuration does not rely on:

- `LoaderPriority`;
- parallel loading;
- CollectionService discovery;
- relocation;
- custom predicates or `StartCustom`;
- `ClientWaitForServer`;
- `ClientWaitForPersistentLoaded`.

These capabilities are not universally forbidden. Changing them means reassessing startup, dependency, discovery, or validation consequences at the infrastructure/design level rather than treating them as a feature-local tweak.

## Failure behavior

The upstream loader catches lifecycle failures and reports warnings rather than propagating one global fail-fast startup failure.

Consequences include:

- `ServerLoaded` does not prove every server lifecycle method succeeded;
- `ClientLoaded` does not prove every client lifecycle method succeeded;
- an `Init` failure does not automatically prevent that module's `Start` from being attempted;
- loader load/init/start warnings are validation failures.

If the project requires different failure semantics, reassess the canonical no-wrapper/no-fork decision instead of silently assuming the loader already provides them.

## Source-of-truth integration

Keep this layer routing-oriented:

- **Studio-native:** use the exact upstream `v3.0.4` release model when that fits the project.
- **Wally:** use `crusherfire/module-loader@3.0.4` when the project already uses or intentionally selects Wally.
- **Rojo:** represent the canonical DataModel faithfully and use [`rojo.md`](rojo.md) for mapping details.
- **Script Sync:** use [`script-sync.md`](script-sync.md) for source-of-truth and synchronization behavior.

Do not introduce Wally solely to acquire the loader.

For actual third-party acquisition and integration procedure, use the existing `roblox-resource-acquisition` workflow. The resource is already selected; acquisition should not restart loader comparison unless material new evidence invalidates that selection.

## Infrastructure validation

For bootstrap, loader integration, discovery, or loader-wide changes:

```text
relevant static/type/lint/build/mapping checks
→ Studio server/client startup
→ expected lifecycle roots are discovered exactly once where applicable
→ no loader load/init/start failure warnings
→ validate changed bootstrap/integration behavior
```

When source-of-truth mapping changes, also apply the active specialist reference's validation requirements.

Bootstrap/infrastructure work is complete when a fresh infrastructure agent can create or modify canonical SSA without pushing acquisition, loader configuration, or loader-version reasoning back into ordinary feature work.
