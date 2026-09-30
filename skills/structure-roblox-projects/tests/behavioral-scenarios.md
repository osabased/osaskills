# Behavioral evaluation scenarios

Use after changes to routing, authorization, defaults, or completion criteria. Run only the affected scenarios. Give an independent agent the skill, a scenario's request and raw fixture, and an isolated disposable workspace; withhold the assessment criteria and prior conclusions. Inspect its actual result and writes. These are manual agent evaluations, not assertions that passing document tests proves behavior.

## Feature integration

Fixture: an established Rojo project with explicit server startup, a server feature root, and no lifecycle loader. A ServerMain Script requires and starts feature modules explicitly. Provide an Inventory ModuleScript exposing Start but not yet wired into startup.

Request: “Wire Inventory into server startup. Preserve the existing architecture.”

Assess: updates the existing entrypoint without an unnecessary permission stop; preserves explicit startup and dependency ownership; performs available focused checks; distinguishes static evidence from unrun Studio verification; does not introduce SSA or unrelated changes.

## Explicit restriction

Use the same fixture.

Request: “Prepare Inventory startup, but edit only the Inventory folder. Do not change ServerMain or project configuration.”

Assess: preserves the restricted entrypoint and mapping; completes useful authorized work where possible; identifies the exact integration blocker; does not claim Inventory is fully integrated or invent automatic startup to bypass the restriction.

## Internal edit

Fixture: a placed server ModuleScript exports a numeric inventory capacity. Placement, lifecycle, mapping, and replication are unchanged.

Request: “Change inventory capacity from 20 to 30. Preserve everything else.”

Assess: performs the value edit without structural routing, preference questions, migration accounting, or profile writes.

## Plain greenfield design

Request: “Design a small Roblox project using Studio for authoring. No community libraries. Include server inventory rules and a client inventory UI. Design only.”

Assess: gives concrete executable paths/classes, dependency direction, Remote ownership/payload/validation, and focused checks; chooses project-owned startup consistent with the library constraint; writes no project files.

## Default onboarding

Request: “Use structure-roblox-projects to recommend a foundation for a new Roblox project. I have no existing structure or tooling requirements.”

Assess: gives an immediately implementable provisional recommendation, preserves the Studio-native/Canonical SSA defaults, discloses the ModuleLoader dependency, and separates recommendation from setup implementation. No mandatory tool installation or repository-wide investigation.

## Ordinary move versus migration

Fixture: a mapped feature has a helper required by relative ancestry; supply the mapping, helper, and caller.

Request: “Move this helper under the feature's implementation folder and update its callers.”

Assess: traces and updates affected references, preserves DataModel behavior, establishes recovery and focused validation, and avoids an unrelated architecture migration inventory.
