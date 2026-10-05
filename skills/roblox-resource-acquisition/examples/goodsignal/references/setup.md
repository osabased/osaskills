# Setup

1. Resolve the project-owned target and installation before using the common path.

Resolve the active project first. This example models a child installed at project/repository scope; an unresolved project does not authorize a user/global fallback. Its owner must select the canonical commit; this example supplies no adoption authority. Preserve the upstream MIT license. For this fixture, place the inspected `src/init.lua` as `ReplicatedStorage.Packages.GoodSignal`, with a project manifest/header naming the exact commit. A package version with the same name is not automatically the same source state. Adapt the fixture's require path to the project's selected installation and rerun checks after that adaptation.
