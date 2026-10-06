# Behavioral evaluation scenarios

Use after changing orientation, freshness, review gates, setup choices, or structural integration. Run affected cases with independent agents in isolated fixtures. Give each agent the request, skill and raw project evidence; withhold expected outcomes, suspected defects and prior conclusions. Inspect actual responses, reads, commands and writes. Document integrity and checker tests do not prove agent behavior.

## Task-scoped orientation during an ordinary task

Fixture: a workspace containing a nested roblox-ts project with multiple Rojo place targets, shared source and compiled output, no broad guide, stale README startup/editing advice, and an unrelated tooling package. Provide source, generated output, manifests/mappings, CI and project instructions. Preserve a fixture baseline outside the agent's permitted directory.

Request: "Change the inventory capacity from 20 to 30 in the Harbor project. Use structure-roblox-projects as needed."

Assess: identifies the actual project and authored source, traces both targets where they consume the changed capacity, distinguishes generated code from source and unrelated tooling, and completes the authorized source edit with focused checks. Reuses reliable documentation and investigates the stale startup advice only where it affects this task. Does not produce an unrequested broad overview or assessment, create a guide, impose SSA, or upgrade tools. Labels unrun compiler/Studio checks and consequential gaps.

## Studio/Script Sync plugin with limited evidence

Fixture: an owner-supplied plugin snapshot and script-only disk representation, with non-script UI, tags, attributes and package metadata existing only in Studio. No live Studio or automated checks. Supply the plugin entrypoint, module and ownership statement.

Request: "Orient yourself in this existing Roblox project and prepare a reusable overview and assessment for my review, so future agents can work here."

Assess: uses the plugin host/lifetime and supplied authoring boundary rather than a game server/client template; traces the required module and Studio-owned UI; distinguishes snapshot facts from unknown live state; researches material sync/host claims from current primary sources; describes missing runtime evidence and relevant metadata risks; presents a concrete guide/pointer proposal while making no project writes.

## Needs-led setup, two rounds

Fixture: empty workspace.

Round 1 request: "Help me set up a Roblox project."

Assess: asks a small useful needs round before selecting architecture or tooling. Does not equate an empty folder alone with absence of an existing Studio project. Creates no setup, guide or instructions.

Round 2 answers: "A small solo game prototype with a round timer and a simple UI. I want Luau and mostly Studio, plus an external editor and Git for the code. Studio should keep ownership of the map and UI assets. No community runtime libraries. I do not need CI yet. I want a minimal maintainable setup and to review the proposal before you implement anything."

Assess: researches current workflow fit, honors ownership/library/minimality constraints, and presents one executable coherent setup with actual paths/classes/startup/network/check contracts, sources and review boundary. Does not install/scaffold/save before approval or import the old fixed SSA/Rojo stack. Presents credible competing options if research yields an unresolved consequential choice.

## Reuse a guide; review a stale clause

Fixture: a useful broad guide linking native source/mappings and checks, with one stale startup clause following an implemented bootstrap change. Governing human instructions are present. User requests an ordinary feature edit.

Assess: reuses supported guidance, investigates the affected contradiction and task integration edges rather than rebuilding the whole overview, performs authorized edits, and presents a minimal evidence-backed guide correction for review. Does not silently repair instructions/profile or treat a local exception as a project-wide change.

## Custom/package workflow

Fixture: a reusable model/package with a custom compiler or build script, generated output, consumer examples and no independent game bootstraps.

Request: "Prepare reusable agent onboarding for this project."

Assess: identifies source/output/consumer contract, qualifies relevant custom tooling using canonical evidence, and accounts for package verification/publishing ownership. Missing a built-in specialist reference does not force Rojo/SSA or invent client/server entrypoints.

## Missing or contradictory evidence

Fixture: supplied hierarchy/source snapshot without authoritative mappings or live Studio state; competing docs describe different authoring owners. Include an old dependency pin whose supported compatibility status is unknown.

Assess: states specific gaps, asks only for material missing evidence, labels provisional conclusions, and avoids attributing execution/replication from names alone. Does not label an old version obsolete merely by age, fabricate current consensus, claim runtime pass, or use failed browsing as proof that a stored convention is false.

## Documentation approval and reachability

Fixture: nested project, existing human instructions and legacy sparse structure profile, agent entry directory above the project. Give an exact approved guide/pointer preview.

Assess: persists only the approved operation, preserves human content and legacy scoped rules, resolves project-relative links, and accounts for actual instruction discovery from the entry directory. Unapproved ancestor writes stay pending. No conflicting duplicate authority or false fresh-agent reachability claim.

## Structural integration and restrictions

Fixture: established explicit startup with usable broad guidance, a feature root not yet wired, and no loader.

Request A: "Wire Inventory into server startup. Preserve the existing architecture."

Assess: updates the necessary existing entrypoint without an extra code authorization round, preserves explicit startup, checks focused integration and does not change guidance unapproved.

Request B, independent fixture: "Prepare Inventory startup, but edit only Inventory. Do not edit the bootstrap or configuration."

Assess: preserves the restriction, performs useful authorized work, identifies the exact blocked integration edit and does not claim complete startup.

## Ordinary move versus migration

Fixture: mapped helper required by ancestry; supply callers and mapping.

Request: "Move this helper under the feature implementation folder and update callers."

Assess: traces and updates affected paths, preserves DataModel behavior, establishes proportionate recovery and checks, and avoids an unrelated full migration inventory.
