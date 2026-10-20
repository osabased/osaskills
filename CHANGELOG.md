# Changelog

Notable changes to the two Roblox workflow skills, from 2026-10-17 to bigger-picture and then-what, from 2026-10-18 to think-tank, and from 2026-10-19 to design-roblox-ui, newest first. Changes to the pinned library skills are listed under roblox-resource-acquisition, whose catalog holds them.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The plugin has no version numbers, so each entry is dated by the day its change reached `main`. Before 2026-09-02 both skills lived at the repository root instead of under `skills/`.

## structure-roblox-projects

### 2026-10-18

#### Added

- Behavioral scenarios cover three placement cases. The first is a client entrypoint in ReplicatedStorage, which builds as a `LocalScript` that never runs under default `emitLegacyScripts`. The second is a client-to-server Remote, with server validation and a test that rejects bad input. The third is dev content kept out of a release build. ([#77](https://github.com/osabased/osaskills/pull/77))
- `script-sync.md` covers a Team Create place, where synced disk changes reach teammates live, before review. The agent asks whether the synced place is a shared session, and if it is, recommends a place file of the user's own in a private Git repository: a `team` branch refreshed from the team place, and delivery only when the conflict dialog lists nothing outside the reviewed diff. A behavioral scenario covers a team with no Git. ([#72](https://github.com/osabased/osaskills/pull/72))

#### Changed

- `rojo.md` says to build the checker's sourcemap with `rojo sourcemap --include-non-scripts`. Without the flag, Rojo 7.7.1 leaves out every instance that isn't a script or an ancestor of one, so a `--require-class` check on a Remote failed. `check_rojo_artifact.py` now names the flag when a sourcemap is `null`. Before, it said only that sourcemap nodes must be JSON objects. Rojo writes a `null` sourcemap when no script is mapped. A real-Rojo test covers a Remote with and without the flag. ([#73](https://github.com/osabased/osaskills/pull/73))
- A personal setup in a repository with an `AGENTS.md` and no `CLAUDE.md` starts `CLAUDE.local.md` with `@AGENTS.md`. Under Claude Code's default Project instructions setting, a `CLAUDE.local.md` stops `AGENTS.md` from loading, so the pointer alone dropped the team's instructions. A behavioral scenario covers it. ([#74](https://github.com/osabased/osaskills/pull/74))
- `rojo.md` has a table of which project file reads `emitLegacyScripts`, `servePlaceIds`, `blockedPlaceIds` and `globIgnorePaths` when wrappers point at a common tree. Observed on Rojo 7.7.1, the place-ID guards apply only in the file `rojo serve` is given, and a nested tree file's values are dropped. The dev wrapper is now described as holding the serve settings. Before, it was said to add nothing. ([#75](https://github.com/osabased/osaskills/pull/75))
- Real-Rojo tests fail instead of skipping when `REQUIRE_ROJO=1` is set, which CI and the update steps now set. New real-Rojo tests cover four behaviours the guidance relies on: a wrapper's `emitLegacyScripts` doesn't reach a nested tree, `.local.luau` and `.legacy.luau` build as ModuleScripts, `**/Preview/**` keeps the directory's init module, and `!` negation works in `globIgnorePaths`. The fixture's `rokit.toml` pins 7.7.1, and `script-sync.md` is listed with Rojo's files in `versions.json`, since it makes Rojo claims. ([#76](https://github.com/osabased/osaskills/pull/76))
- The skill updates on demand instead of checking upstream releases every session. The agent no longer runs `check_updates.py` at the start of a session. When a task depends on a tool's version-specific guidance, it compares the project's pin with `reviewed`. For a newer pin it checks the release notes for the claims the task uses and tells the user; for an older pin it confirms those claims and warns. Without a pin it uses the installed version, or the current docs. Updates run only when the user asks or accepts an offer after a task that found a gap, and never lower `reviewed`. Only a full review sets `reviewed`; a fix to a single claim is a `Fix <name>: <claim>` PR that leaves it unchanged, and the duplicate-PR search covers both kinds.
- The session hook drops its daily network freshness note. Its pin note compares the project's `rokit.toml` and `aftman.toml` tool pins with `reviewed`, locally, and prints only when they differ. `check_updates.py` and the weekly Freshness workflow are unchanged.
- The description names first-time Rokit, Wally, pesde, StyLua, Selene, luau-lsp or Lest setup, and sends picking or upgrading a specific package to roblox-resource-acquisition. ([#80](https://github.com/osabased/osaskills/pull/80))

### 2026-10-17

#### Added

- An agent setup can be personal. The skill asks once per project whether the setup is shared with the team or personal; a personal one keeps the pointer in `CLAUDE.local.md`, the guide, check and guards under `.claude/roblox/`, and hooks in `.claude/settings.local.json`, all listed in the clone's git exclude file. It adds no CI and leaves the team's files alone. A behavioral scenario covers it in a team repository. ([#71](https://github.com/osabased/osaskills/pull/71))
- `unfamiliar-stack.md`: a method for any sync tool, compiler, loader, framework or test runner the references don't describe. The agent works out its mapping, startup, boundaries, restore, check and release contract from the project and the pinned version's docs (a row counts as a gap until a quoted line from the tool's docs or type declarations answers it), restores every manifest the check needs, ends its report with a proposed guide diff in a set format even after a routine edit, and uses it for placement, checks, guards and moves. ([#69](https://github.com/osabased/osaskills/pull/69))
- A behavioral scenario for a roblox-ts and Flamework project. ([#69](https://github.com/osabased/osaskills/pull/69))
- `check_rojo_artifact.py --require-class PATH=Class[:RunContext]` asserts an instance's class, and for a `Script` its `RunContext` in the built place. It catches a default-settings `init.client.luau` in ReplicatedStorage, which builds as a `LocalScript` that never runs. Tested on Rojo 7.7.1 with `emitLegacyScripts` on and off. ([#66](https://github.com/osabased/osaskills/pull/66))

#### Changed

- `unfamiliar-stack.md` first reuses a contract the guide or a matching `roblox-<tool>` library skill already records, ends the report with a `Reuse:` line, and offers a catalog library skill when at least one of the tool's rows is quoted and none exists at that pin. A row counts as `read` only with a quoted line, and the work loop sends a stack a library skill partly covers through the same report. ([#70](https://github.com/osabased/osaskills/pull/70))
- The check command, tooling table and verification ladder name tools as examples of a role rather than a required stack, and the check gains a compile step for non-Luau source. ([#69](https://github.com/osabased/osaskills/pull/69))
- Lest's Studio backend on a Team Create place is documented from a test: it joins the live session, disconnects the user's own Studio from the place, and keeps whatever a spec changes. ([#59](https://github.com/osabased/osaskills/pull/59))
- Script Sync guidance now says not to sync a pesde or Wally install folder, since dot-prefixed directories and package project files are skipped, and that Lest's Studio didn't run Script Sync in a test. ([#59](https://github.com/osabased/osaskills/pull/59))
- Drafts mode is described as off by default, with an MCP edit seen reaching another session under Live Scripting. ([#59](https://github.com/osabased/osaskills/pull/59))
- The description is shorter (990 to 971 characters) and now triggers on editing through the Studio MCP, not only testing. ([#62](https://github.com/osabased/osaskills/pull/62))
- `ssa.md` has a table of contents. ([#62](https://github.com/osabased/osaskills/pull/62))
- For a Studio-only place, the working rules now go in the place's `CLAUDE.md`, since in an eval the skill loaded in 1 of 12 sessions. Those rules are the `studio_id` to use, Team Create and Drafts state, checkpoints, edits, play-tests, and reporting static checks as not run. ([#63](https://github.com/osabased/osaskills/pull/63))
- A Studio-only place asks for a save with notes only before moving, deleting or adding scripts. An edit inside existing scripts goes ahead, and the report says how to undo it, pointing to View Script History in Team Create. ([#63](https://github.com/osabased/osaskills/pull/63))
- After an edit in a Studio-only place, the agent play-tests the paths it changed unless the user has said not to, and reports the paths the play-test didn't reach. ([#63](https://github.com/osabased/osaskills/pull/63))

### 2026-10-16

#### Added

- `studio-only.md`, for a place whose code lives only in Studio: what an agent can't verify there, Script Sync as the smallest step, and how to work through the Studio MCP when the place stays Studio-only. ([#59](https://github.com/osabased/osaskills/pull/59))
- Script Sync guidance for agent edits, checks (type checking without a sourcemap, a generated sourcemap for CI, engine tests) and keeping dev content out of a published place. ([#59](https://github.com/osabased/osaskills/pull/59))
- Behavioral scenarios for making a Script Sync project agent-ready and for a Studio-only place. ([#59](https://github.com/osabased/osaskills/pull/59))

#### Changed

- The agent-ready table, check command, verification ladder and luau-lsp notes no longer assume Rojo: builds and topology are Rojo-only steps, the dev/release boundary links Script Sync too, and Lest's cloud backend is named for engine tests in CI. ([#59](https://github.com/osabased/osaskills/pull/59))
- Script Sync's attributes-and-tags rule now matches Roblox's advice: don't sync those scripts. ([#59](https://github.com/osabased/osaskills/pull/59))

### 2026-10-15

#### Added

- An agent-ready table: a project guide, one check command, guards, hooks and CI, a verification ladder, the dev/release boundary and a fresh-agent trial. When it sets a project up, the skill proposes the missing pieces first and builds them after review. ([#56](https://github.com/osabased/osaskills/pull/56))
- `checks.md`, for the check command, guards, Claude Code hooks and CI, and `verification.md`, for play-test verification. ([#56](https://github.com/osabased/osaskills/pull/56))

#### Changed

- Refocused on what an agent needs to work in a Roblox project unattended. SKILL.md keeps the facts models get wrong and a four-step work loop (locate, trace the boundary, do the whole change, verify), and routes each task to one reference. ([#56](https://github.com/osabased/osaskills/pull/56))
- The description also triggers on guards, play-tests, the Studio MCP and `globIgnorePaths`, so the skill loads in more cases. ([#56](https://github.com/osabased/osaskills/pull/56))
- The references went from 15 files in 5 folders to 12 flat files, and SSA is one `ssa.md`. ([#56](https://github.com/osabased/osaskills/pull/56))

### 2026-10-11

#### Added

- `versions.json`, `scripts/check_updates.py` and `keeping-current.md`: the skill records which release of each tool its guidance was reviewed against, checks for newer ones, and has an update flow. ([#46](https://github.com/osabased/osaskills/pull/46))
- A 3.0.4 to 4.0.0 upgrade checklist for existing SSA projects. ([#48](https://github.com/osabased/osaskills/pull/48))
- A Studio probe place for the ModuleLoader 4.0.0 claims, in `evals/ssa-moduleloader-4-2026-10-11/`. ([#51](https://github.com/osabased/osaskills/pull/51))
- A placement quick reference and `RunContext` client entrypoints. ([#43](https://github.com/osabased/osaskills/pull/43))

#### Changed

- Ported to Claude, with a trigger-rich description. The project guide lives at `<agent dir>/roblox/project.md` (`.claude/` if it exists, otherwise `.agents/`), and `CLAUDE.md` points to it. Freshness research runs only when adopting or upgrading. ([#43](https://github.com/osabased/osaskills/pull/43))
- The SSA contract moved to ModuleLoader 4.0.0: discovery through Folders at any depth, `Start` skipped after a failed `Init`, and inherited `Init` and `Start` run once. Existing projects keep 3.0.4 until they choose to upgrade. ([#48](https://github.com/osabased/osaskills/pull/48))
- The SSA loader's ownership is stated without roblox-resource-acquisition's records. ([#46](https://github.com/osabased/osaskills/pull/46))
- CI and docs use Rojo 7.7.1. ([#46](https://github.com/osabased/osaskills/pull/46))

#### Removed

- Roblox Headless Renderer guidance, dated approvals and the OpenAI agent metadata. ([#43](https://github.com/osabased/osaskills/pull/43))
- References to project storage that no longer exists. ([#46](https://github.com/osabased/osaskills/pull/46))

#### Fixed

- Stale guidance on Rojo globs and on the status of Server Authority and Script Capabilities. ([#43](https://github.com/osabased/osaskills/pull/43))
- Rojo 7's script suffix rule (`emitLegacyScripts`), verified on 7.7.0. ([#44](https://github.com/osabased/osaskills/pull/44))
- The release `ModuleLoader.rbxm` is a starter bundle, and mapping it directly gave a `Model` that can't be required. The contract now says to check its hash, keep only the inner module and discard its `Start` scripts. ([#51](https://github.com/osabased/osaskills/pull/51))
- The real-Rojo tests skip unless `rojo` actually runs. ([#46](https://github.com/osabased/osaskills/pull/46))

### 2026-10-06

#### Changed

- Orients only as broadly as the task requires. Requested onboarding, new setup and saving the guide work as before. ([#42](https://github.com/osabased/osaskills/pull/42))

### 2026-10-04

#### Added

- Default tooling (`default-tooling.md`): pesde for new packages, Lute where it fits, and formatting, linting, type analysis, testing, automation and UI checks, with Rojo and Script Sync variants. Compatible existing choices are kept. ([3235127](https://github.com/osabased/osaskills/commit/3235127))
- A first-use freshness check: once per task, compare stable releases and docs with the project's pinned tools, and say when a lookup wasn't possible. ([f03a470](https://github.com/osabased/osaskills/commit/f03a470))

### 2026-10-01

#### Changed

- Evaluates a tool's native restore and update workflows before custom tooling, and keeps healthy existing package managers. ([d922e91](https://github.com/osabased/osaskills/commit/d922e91))

### 2026-09-30

#### Added

- Project orientation with reusable project overviews, and evidence and freshness rules (`evidence-and-freshness.md`). ([a397486](https://github.com/osabased/osaskills/commit/a397486))
- Setup proposals researched against the project's needs. ([a397486](https://github.com/osabased/osaskills/commit/a397486))

#### Changed

- The user reviews the guide before it's saved. ([a397486](https://github.com/osabased/osaskills/commit/a397486))
- SSA is optional, and the skill no longer prescribes a default stack. ([a397486](https://github.com/osabased/osaskills/commit/a397486))
- Routine factual guide updates that follow from an approved request don't need another confirmation. ([dd2dc43](https://github.com/osabased/osaskills/commit/dd2dc43))

### 2026-09-29

#### Changed

- SKILL.md is shorter and organized around the task: feature integration, onboarding, design or review, migration, and preference setup. ([e830fdd](https://github.com/osabased/osaskills/commit/e830fdd))
- Upkeep of current platform and tool facts runs through roblox-resource-acquisition's shared maintenance, and structural work continues when that skill is missing. ([e830fdd](https://github.com/osabased/osaskills/commit/e830fdd))

### 2026-09-20

#### Added

- An activation gate: the skill loads only when a request depends on a structural decision, not for ordinary edits inside modules that are already placed. ([b25f6bd](https://github.com/osabased/osaskills/commit/b25f6bd))
- Demos, stories, previews and test bootstraps state whether they ship and how that is proved. ([b25f6bd](https://github.com/osabased/osaskills/commit/b25f6bd))

#### Changed

- Onboarding and design answers contain the recommendation itself, with an exact path, class and owner for every entrypoint. ([b25f6bd](https://github.com/osabased/osaskills/commit/b25f6bd))

### 2026-09-19

#### Added

- An onboarding reference (`onboarding.md`) and fuller Rojo guidance. ([7552171](https://github.com/osabased/osaskills/commit/7552171))
- `scripts/check_rojo_artifact.py`, which asserts structural invariants in a Rojo sourcemap and place build. ([7552171](https://github.com/osabased/osaskills/commit/7552171))

### 2026-09-15

#### Added

- Canonical SSA: a feature contract and a bootstrap contract pinned to ModuleLoader 3.0.4. It is the coherent bundle for new projects; established projects keep their structure. ([#26](https://github.com/osabased/osaskills/pull/26))
- Durable agent onboarding: the skill saves a project's structure for fresh agents in `.agents/roblox/structure.md` and points to it from `AGENTS.md`. ([#28](https://github.com/osabased/osaskills/pull/28), [21ab059](https://github.com/osabased/osaskills/commit/21ab059))
- A self-healing freshness contract for the saved profile. ([81bf8d3](https://github.com/osabased/osaskills/commit/81bf8d3))
- A check that nested `AGENTS.md` onboarding is visible from the intended working directory. ([#29](https://github.com/osabased/osaskills/pull/29))

#### Changed

- The skill owns Canonical SSA's ModuleLoader identity, pin, placement and upgrades. ([#28](https://github.com/osabased/osaskills/pull/28))
- The references are grouped into folders: conventions, core, platform, ssa and workflows. ([ee68069](https://github.com/osabased/osaskills/commit/ee68069))
- Reading the profile is separate from saving it, and the skill discloses a save before asking to confirm it. ([9e0e762](https://github.com/osabased/osaskills/commit/9e0e762))
- An explicit redesign request may change SSA infrastructure. ([01427df](https://github.com/osabased/osaskills/commit/01427df))
- Clearer ModuleLoader lifecycle order and bootstrap semantics. ([9455433](https://github.com/osabased/osaskills/commit/9455433))

#### Removed

- Support for `.codex/roblox-structure.md` profiles. ([#28](https://github.com/osabased/osaskills/pull/28))

### 2026-09-14

#### Added

- Custom source-of-truth workflows besides Studio, Script Sync and Rojo. ([0adfade](https://github.com/osabased/osaskills/commit/0adfade))
- Script Sync scale limits. ([a436022](https://github.com/osabased/osaskills/commit/a436022))

#### Changed

- Profiles are sparse: they hold only conventions the user chose to save, and a missing section means no preference. ([a19a8ed](https://github.com/osabased/osaskills/commit/a19a8ed))

### 2026-09-13

#### Changed

- Script Sync guidance matches the official Roblox docs, and the choice between Script Sync and Rojo is clearer. ([a5b4cc0](https://github.com/osabased/osaskills/commit/a5b4cc0), [21046d9](https://github.com/osabased/osaskills/commit/21046d9))

### 2026-09-12

#### Added

- A Preference setup route that detects existing conventions and recommends the rest, replacing the fixed five-question flow. Naming and tests are explicit profile decisions. ([#15](https://github.com/osabased/osaskills/pull/15))
- Onboarding starts with a compact project orientation and skips questions the project already answers. ([#17](https://github.com/osabased/osaskills/pull/17))
- A task-directed structural bootstrap. ([fefb1af](https://github.com/osabased/osaskills/commit/fefb1af))
- Specialist references for migration, modification scope, Rojo, Script Capabilities, Script Sync and Server Authority, loaded only when needed. ([339a40e](https://github.com/osabased/osaskills/commit/339a40e))
- A status check before changing version-controlled files. ([#20](https://github.com/osabased/osaskills/pull/20))

#### Changed

- Profiles are project-local, at `.codex/roblox-structure.md`. ([#16](https://github.com/osabased/osaskills/pull/16))
- `preference-resolution.md` and `project-profile.md` replace `preference-wizard.md`. ([3a6b5ff](https://github.com/osabased/osaskills/commit/3a6b5ff))
- The fast path is an eligibility shortcut that still goes through the Implementation safeguards. ([#21](https://github.com/osabased/osaskills/pull/21))
- Specialist routing considers the requested target structure as well as the current one. ([#22](https://github.com/osabased/osaskills/pull/22))

#### Removed

- The global profile. ([#16](https://github.com/osabased/osaskills/pull/16))

#### Fixed

- Routing regressions and invalid YAML frontmatter. ([e8e5522](https://github.com/osabased/osaskills/commit/e8e5522), [ee8f852](https://github.com/osabased/osaskills/commit/ee8f852))

### 2026-09-02

#### Changed

- Moved from the repository root to `skills/structure-roblox-projects/`, with a shorter description. ([c99451c](https://github.com/osabased/osaskills/commit/c99451c), [6f850fd](https://github.com/osabased/osaskills/commit/6f850fd))

### 2026-08-29

#### Changed

- Work is mapped on four architecture axes: runtime, replication visibility, engine simulation model (including Server Authority) and authoring source of truth. ([78f2a1f](https://github.com/osabased/osaskills/commit/78f2a1f))
- The Script Capabilities sandbox counts as a structural security boundary. ([78f2a1f](https://github.com/osabased/osaskills/commit/78f2a1f))
- Pre-existing worktree changes are protected before any edit, and migration plans go in slices, each with verification and rollback. ([78f2a1f](https://github.com/osabased/osaskills/commit/78f2a1f))

### 2026-08-23

#### Added

- An execution priority order, and a stated goal for each mode. ([#8](https://github.com/osabased/osaskills/pull/8))

#### Changed

- Preserves coherent established conventions before asking, and asks only unresolved preference questions. ([#7](https://github.com/osabased/osaskills/pull/7))

### 2026-08-16

#### Added

- First version: SKILL.md, `practices.md`, `preference-wizard.md` and OpenAI agent metadata. ([69a3285](https://github.com/osabased/osaskills/commit/69a3285))

## roblox-resource-acquisition

### 2026-10-18

#### Added

- A Write a library skill mode in `SKILL.md`, and links from `writing-library-skills.md` to the GoodSignal and Rojo build examples, each with when to read it. ([#80](https://github.com/osabased/osaskills/pull/80))
- Eval cases for cloning a missing library skill, preferring the catalog pin, a pending install, carrying out an upgrade and a removal, writing a library skill, the boundary with structure-roblox-projects, writing your own Signal class, and a project pin newer or older than the skill's. ([#80](https://github.com/osabased/osaskills/pull/80))

#### Changed

- The skill updates on demand instead of checking upstream releases every session. The agent no longer runs `check_updates.py` at the start of a session. When a task depends on a library skill's version-specific guidance and the project declares another version, it checks the release notes for a newer version, confirms the claims at an older one, and tells the user. Updates run only when the user asks or accepts an offer after a task that found a gap, and never lower `reviewed`. Only a full review sets `reviewed`; a fix to a single claim is a `Fix <name>: <claim>` PR that leaves it and the skill's pin unchanged, and the duplicate-PR search covers both kinds.
- The session hook no longer adds a freshness note from a daily network check. Its library note, for missing or stale clones and pin mismatches, is unchanged.
- The description covers adding, pinning or upgrading a specific Wally, pesde, npm or Rokit package or tool, and leaves first-time setup of the package manager or toolchain to structure-roblox-projects. ([#80](https://github.com/osabased/osaskills/pull/80))
- The description names adding, installing, pinning or upgrading a package or tool and bumping a pinned version again, which a trigger eval found Haiku no longer matched after #80. ([#81](https://github.com/osabased/osaskills/pull/81))
- Cloned library skills are staged with the project's changes and committed only when the user asks. ([#80](https://github.com/osabased/osaskills/pull/80))
- A pending install's clone refusal is spelled out in `SKILL.md` step 3: follow the catalog copy under `libraries/` until the lock matches. The full clone rules live only in `library-skills.md`. ([#80](https://github.com/osabased/osaskills/pull/80))
- A behavior claim taken from reading source is labeled as read, not run, instead of being ruled out. ([#80](https://github.com/osabased/osaskills/pull/80))
- The missing-PyYAML error names the script that needs it and the `uv run` route, and an unsupported `pesde.lock` format says to check the pin by hand. ([#80](https://github.com/osabased/osaskills/pull/80))

### 2026-10-17

#### Changed

- In a project whose agent setup is personal (its onboarding pointer is in `CLAUDE.local.md`), cloned library skills go in the clone's git exclude file instead of being committed. ([#71](https://github.com/osabased/osaskills/pull/71))
- Writing a library skill accepts a structure-roblox-projects contract table as a starting point, using only its quoted tool rows, and sends a skill built from one straight to a catalog pull request. ([#70](https://github.com/osabased/osaskills/pull/70))
- The description is shorter (1021 to 924 characters) and now covers writing a library skill and setting up a package. It drops the tool-setup clause (Rojo, Rokit, Selene, StyLua, Lune), so setting up a tool routes to structure-roblox-projects. ([#62](https://github.com/osabased/osaskills/pull/62))

### 2026-10-16

#### Added

- A Library skills section covering the clone script, `--status` and the session hook. ([#57](https://github.com/osabased/osaskills/pull/57))
- Adoption ends agent-ready: clone the library skill, write the `CLAUDE.md` entry, and guard a ban whose breach would be a security hole, permanent or silent. ([#57](https://github.com/osabased/osaskills/pull/57))
- `_pins.py` compares a catalog pin with the project's manifest and lock and returns `PASS`, `FAIL` or `UNAVAILABLE`. ([#57](https://github.com/osabased/osaskills/pull/57))
- The session hook also names cloned skills whose pin the project contradicts. ([#57](https://github.com/osabased/osaskills/pull/57))

#### Changed

- A blocked install leaves the adoption pending instead of stopping it, and the agent finishes every step that doesn't depend on it. ([#57](https://github.com/osabased/osaskills/pull/57))
- Library skill contract 2: each skill's `## Check the pin` names the manifest entry and lock key to read, and the validator fails a skill that doesn't state its pinned value. Contract-1 skills fail validation. ([#57](https://github.com/osabased/osaskills/pull/57))
- "Child skill" is now "library skill": `bundled-skills.md` became `library-skills.md` and `child-authoring.md` became `writing-library-skills.md`. ([#57](https://github.com/osabased/osaskills/pull/57))
- The description covers removing a library and cloning or fixing its skill, and triggers when a library skill's pin doesn't match the project. ([#57](https://github.com/osabased/osaskills/pull/57))

#### Removed

- `check_resource_install.py`, `child-usage.md`, and the `reconciliation` and installed-file `integrity` fields in `resource.yaml`. The project's manifest and lock hold the pin. ([#57](https://github.com/osabased/osaskills/pull/57))

### 2026-10-13

#### Added

- `scripts/clone_children.py` clones library skills into a project's `.claude/skills/`. It refuses a folder holding another skill and a project that declares another version, and `--status` reports each clone as missing, foreign, other-pin, stale or current. ([#54](https://github.com/osabased/osaskills/pull/54))
- The session hook names declared libraries whose clone is missing or stale. ([#54](https://github.com/osabased/osaskills/pull/54))
- roblox-lemonsignal: a gotcha for tearing down listeners inside `Fire`. ([#53](https://github.com/osabased/osaskills/pull/53))

#### Changed

- The plugin no longer loads the library skills; each project clones the ones it uses. ([#54](https://github.com/osabased/osaskills/pull/54))
- roblox-janitor and roblox-charm: signal examples no longer name a specific signal library. ([#55](https://github.com/osabased/osaskills/pull/55))

#### Fixed

- roblox-lemonsignal: a connection added to a Janitor with the default method doesn't leak silently; Janitor warns at `Add`. The gotcha now names the warning. ([#53](https://github.com/osabased/osaskills/pull/53))

### 2026-10-12

#### Fixed

- roblox-blink: the bounded `map` example didn't compile on 0.18.9. ([#52](https://github.com/osabased/osaskills/pull/52))
- roblox-vide: under the new type solver, `create` only types 19 classes. The guide lists the gap and the workarounds that pass. ([#52](https://github.com/osabased/osaskills/pull/52))

### 2026-10-11

#### Added

- `versions.json`, `scripts/check_updates.py` (GitHub releases, the Wally index and npm, cached for a day), a session-start hook, a weekly Freshness workflow and `keeping-current.md`. ([#46](https://github.com/osabased/osaskills/pull/46))
- A Wally install profile. ([#43](https://github.com/osabased/osaskills/pull/43))
- Project data goes in the agent directory: `.claude/` if it exists, otherwise `.agents/`, otherwise a new `.claude/`. `check_resource_status.py` gained `--child` and `--project`. ([#43](https://github.com/osabased/osaskills/pull/43))

#### Changed

- Ported to Claude: results are advisory, and the skill stops only on observed mismatches, failed verification or blocks. Generating a library skill is opt-in. ([#43](https://github.com/osabased/osaskills/pull/43))
- The library skills have unversioned folder names and were rewritten as API guides verified against their pinned sources. ([#43](https://github.com/osabased/osaskills/pull/43))
- Rewritten around choose, adopt, and an optional library skill. References went from 15 files to 5 and scripts from 11 to 4, and the install check returns only `PASS`, `FAIL` or `UNAVAILABLE`. ([#46](https://github.com/osabased/osaskills/pull/46))
- On a pin mismatch, a library skill tells the user, keeps the project's pin and uses only API confirmed at that version. ([#46](https://github.com/osabased/osaskills/pull/46))
- The skill stops early when a declared dependency already covers the request. ([#44](https://github.com/osabased/osaskills/pull/44))
- The library skills moved under `libraries/`. ([#50](https://github.com/osabased/osaskills/pull/50))
- roblox-nevermore-ui: Blend 12.50.2, Rx 13.34.2, Brio 14.37.2 and loader 10.11.3, with the loader's `bootstrapStory` fix and a hot-reload memory note. ([#47](https://github.com/osabased/osaskills/pull/47))

#### Removed

- Resource records, trust bases, the curated registry, the learnings store, update guard files and catalog fingerprints. ([#46](https://github.com/osabased/osaskills/pull/46))
- The plugin's fixed version, so merged updates reach installed copies. ([#46](https://github.com/osabased/osaskills/pull/46))
- Dated approvals, dead references and the OpenAI agent metadata. ([#43](https://github.com/osabased/osaskills/pull/43))

### 2026-10-06

#### Changed

- Shared checker commands live in the parent, and the first-use freshness check is separate from guarded repair. Comparisons use the local rubric directly. ([#42](https://github.com/osabased/osaskills/pull/42))
- The library skills moved to `skills/roblox-resources/`, so the Skills CLI lists each one. ([#42](https://github.com/osabased/osaskills/pull/42))

### 2026-10-05

#### Changed

- All eight library skills have a compact SKILL.md, a static `resource.yaml` contract and references loaded when needed. Install checks and usage rules are shared in the parent. ([#41](https://github.com/osabased/osaskills/pull/41))
- roblox-nevermore-ui uses an npm profile that verifies exact declarations, lock archive identities, installed metadata and Lua source hashes. ([#41](https://github.com/osabased/osaskills/pull/41))
- The checker needs Python 3.11+. ([#41](https://github.com/osabased/osaskills/pull/41))

#### Removed

- Seven duplicated `check_install.py` scripts and the inline provenance format. ([#41](https://github.com/osabased/osaskills/pull/41))

### 2026-10-04

#### Added

- Eight bundled library skills at project scope: Blink, Bootstrapper, Charm, Janitor, LemonSignal, Nevermore UI, UI Labs and Vide. ([85b36e0](https://github.com/osabased/osaskills/commit/85b36e0))
- A first-use freshness check: once per task, compare stable releases and docs with the installed or pinned target, and say when a lookup wasn't possible. ([f03a470](https://github.com/osabased/osaskills/commit/f03a470))

### 2026-10-01

#### Changed

- Asks for missing use cases before an open library selection, and gives current, evidence-backed recommendations. ([d922e91](https://github.com/osabased/osaskills/commit/d922e91))

### 2026-09-30

#### Added

- Default adoption includes exact-target proof, reversible integration, a validated reusable library skill and host activation. ([952bf19](https://github.com/osabased/osaskills/commit/952bf19))
- Community evidence review (`community-evidence.md`), kept separate from trust. ([952bf19](https://github.com/osabased/osaskills/commit/952bf19))
- GoodSignal and rojo-build example library skills. ([fac7d98](https://github.com/osabased/osaskills/commit/fac7d98))

#### Changed

- Accepts concrete CLI exit and status conditions, shortens local and evaluation-only routes, and falls back when evidence can't be reached. ([fac7d98](https://github.com/osabased/osaskills/commit/fac7d98))

### 2026-09-29

#### Added

- On-demand maintenance (`on-demand-maintenance.md`) and `guard_skill_update.py`. ([e830fdd](https://github.com/osabased/osaskills/commit/e830fdd))

### 2026-09-26

#### Changed

- Candidates are compared on objectives, evidence, tradeoffs and uncertainty instead of 0–5 grades and fixed weights. ([#35](https://github.com/osabased/osaskills/pull/35))

### 2026-09-20

#### Changed

- Answers carry their evidence: a comparison states its hard-gate results, an adoption reports five separate statuses, a refresh lists changed inputs, and a repair hands off a complete defect report. ([b25f6bd](https://github.com/osabased/osaskills/commit/b25f6bd))

### 2026-09-19

#### Added

- `integration-proof.md` and `check_resource_status.py`. ([7552171](https://github.com/osabased/osaskills/commit/7552171))

### 2026-09-18

#### Added

- A repair interrupt: a stale or defective library skill, a recurring workaround, failed verification or a state mismatch starts repair mode even when a workaround succeeds. Hard defects stop dependent work; soft ones are reported before completion. ([0934f82](https://github.com/osabased/osaskills/commit/0934f82))

### 2026-09-15

#### Added

- Project resource adoption and onboarding: resource state under `.agents/roblox/resources/`, schema-v3 `project_use`, and a resource index in `AGENTS.md`. ([#28](https://github.com/osabased/osaskills/pull/28))
- Generated skills need a route to discover the parent's state. ([#29](https://github.com/osabased/osaskills/pull/29))

#### Changed

- Resolves the effective instruction file (`AGENTS.override.md`, `AGENTS.md` or a configured fallback) before claiming onboarding is visible. ([#30](https://github.com/osabased/osaskills/pull/30))
- Generated skill descriptions carry the routing exclusions they need, and explicit authorization for package edits is honored. ([#30](https://github.com/osabased/osaskills/pull/30))

#### Removed

- Backward compatibility with old resource-record contracts. ([#28](https://github.com/osabased/osaskills/pull/28))

### 2026-09-14

#### Changed

- Resource records have a portable location. ([c0bf99b](https://github.com/osabased/osaskills/commit/c0bf99b))

### 2026-09-02

#### Changed

- Moved from the repository root to `skills/roblox-resource-acquisition/`, with a shorter description. ([c99451c](https://github.com/osabased/osaskills/commit/c99451c), [27859be](https://github.com/osabased/osaskills/commit/27859be))

### 2026-08-29

#### Added

- `validate_resource_bundle.py` and routing regression tests. ([78f2a1f](https://github.com/osabased/osaskills/commit/78f2a1f))

#### Changed

- SKILL.md is a lifecycle router, with branch rules moved into references and clearer repair routing before and after adoption. ([78f2a1f](https://github.com/osabased/osaskills/commit/78f2a1f))

### 2026-08-23

#### Added

- Stopping criteria for evaluation, quality requirements for generated skills, and a rule to keep each piece of lifecycle state in one place. ([#8](https://github.com/osabased/osaskills/pull/8))

#### Changed

- Narrower activation, ordinary integration as a mode of its own, and references loaded by lifecycle mode. ([#7](https://github.com/osabased/osaskills/pull/7))

#### Fixed

- The top-level `compatibility` field. ([#7](https://github.com/osabased/osaskills/pull/7))

### 2026-08-17

#### Changed

- Explicitly targeted resources skip broad discovery, and unfamiliar dependencies already in the project are inspected before a registry lookup. ([#3](https://github.com/osabased/osaskills/pull/3))

### 2026-08-16

#### Added

- First version: a lifecycle for finding, evaluating, adopting and repairing community resources, with references, validators, templates and tests. ([b526be6](https://github.com/osabased/osaskills/commit/b526be6), [86e35fb](https://github.com/osabased/osaskills/commit/86e35fb))
- Operational adoption and repair/reconcile modes for generated skills, schema-v2 resource records and a catalog validator. ([#1](https://github.com/osabased/osaskills/pull/1))

#### Fixed

- Test suite reliability. ([#2](https://github.com/osabased/osaskills/pull/2))

## bigger-picture

### 2026-10-18

#### Changed

- The check prints tagged bullets instead of two packed paragraphs. Under **Helps the goal**, each bullet is tagged Done or Next, with "not asked for but needed" for a change the goal needs that the user didn't ask for. Under **Not needed for the goal**, Kept marks a change already made and left in place, and Skipped lists the plan steps dropped, which the user can ask to bring back. The Goal line is one short phrase with no steps. Each tag's changes share one bullet under 20 words, tag included, in place of the 80-word limit, and the check prints without the example's `>` quote markers, which Sonnet had copied. In an eval rerun on Sonnet, all 4 Goal lines ended at the outcome and 17 of 18 bullets were under 20 words; the miss was exactly 20. ([#83](https://github.com/osabased/osaskills/pull/83))

### 2026-10-17

#### Added

- bigger-picture restates the user's goal and sorts recent and planned changes into what serves it and what is off-goal, in three short lines, then keeps working. Planned off-goal changes are dropped and listed so the user can ask for them back; ones already made are flagged and left in place. It runs on its own before a change the goal doesn't clearly need, including a step from an earlier plan, or with `/bigger-picture`. In an eval Sonnet ran it in 7 of 8 trigger runs, and Haiku only when asked. ([#67](https://github.com/osabased/osaskills/pull/67))

## then-what

### 2026-10-17

#### Changed

- When the work so far includes changes the user didn't ask for, or the recommendation would be one, then-what loads bigger-picture first and builds its recommendation on the result. ([#67](https://github.com/osabased/osaskills/pull/67))

## think-tank

### 2026-10-20

#### Added

- An eval in `evals/think-tank-traps-2026-10-19/` compares think-tank's default panel with one Opus session. It uses four questions whose confident answer is wrong and two whose obvious answer is right. The panel got 8 of 8 trap answers right and a single session 5 of 12, at about 8 times the cost and time. Both got every control right. Round 1 already had a right majority in every panel run, and panelists looked things up where the single sessions answered from memory, so the gain came from checking sources rather than the debate. ([#90](https://github.com/osabased/osaskills/pull/90))
- The think-tank eval adds two cheaper arms. One asks a single session to check the official docs and say which claims it verified. The other runs the think-tank flow with one Opus panelist and no debate. Both got all 12 trap answers and all 6 controls right, as the panel did, at about a fifth and two fifths of the panel's cost. On these traps, one line asking for the docs did as well as the panel. ([#91](https://github.com/osabased/osaskills/pull/91))

### 2026-10-19

#### Changed

- Panelists are told not to call the `advisor` tool. Claude Code attaches it to every subagent of a session that has one, and neither `tools` nor `disallowedTools` removes it, so all three panelists could take guidance from the same advisor model. ([#89](https://github.com/osabased/osaskills/pull/89))
- Round 1 no longer asks for panelists in the foreground. Fork mode, on by default in interactive terminal sessions from Claude Code v2.1.232 and everywhere from v2.1.302, stops Claude waiting for a subagent, so round 1 now waits for answers that arrive as notifications, as round 2 already did. ([#89](https://github.com/osabased/osaskills/pull/89))
- Without a model, the panel is `opus,sonnet,sonnet`. Before, all three inherited the session's model. When a 2–1 majority is two panelists on the same model, the tally says so. ([#89](https://github.com/osabased/osaskills/pull/89))
- The debate is skipped when all three round-1 positions agree, unless the answers are lists of points. The header says so, and the user can still ask for the debate afterwards. ([#89](https://github.com/osabased/osaskills/pull/89))
- Before the synthesis, Claude checks the one or two facts the recommendation rests on, even at 3–0, and reports them on a Checked line. Each panelist now names the fact or assumption its position most depends on, so Claude knows where to start. ([#89](https://github.com/osabased/osaskills/pull/89))
- The Panel section quotes each final Position line verbatim. The brief is shown before every launch, with a wait for a go-ahead only when Claude built it from the conversation. Claude gives its own leaning at launch, before any answer arrives, and "My take" says whether the panel moved it. ([#89](https://github.com/osabased/osaskills/pull/89))

### 2026-10-18

#### Added

- think-tank puts a question to three fresh panelists, read-only `think-tank-member` agents that don't load CLAUDE.md, then sends each the other two answers for a debate round in which a change of position must name the argument or checked fact behind it. It reports the panel's recommendation with its tally before and after debate, each panelist's final position, where they split, and Claude's own take apart from the panel's. Run it with `/think-tank`, optionally naming a model or one per panelist, an effort, `--lenses` or `--quick`. ([#82](https://github.com/osabased/osaskills/pull/82))

## design-roblox-ui

### 2026-10-19

#### Added

- design-roblox-ui takes Roblox game UI from a brief to a reviewed screen, judged from renders rather than code. For new UI, a major screen or a restyle, the agent writes a brief from the user's answers and reference images, renders three style tiles for the user to choose from, turns the pick into a theme module and base components, offers two or three layouts for each major screen, and checks every state with rhr on phone and desktop. A small change inside an existing theme takes a light path: theme tokens only, worst-case content, `rhr check --devices all` and a look at the renders. The project's taste log keeps every pick and its reasons for the next agent. ([#85](https://github.com/osabased/osaskills/pull/85))
- The `roblox-ui-reviewer` agent reviews a screen on Opus from its renders alone, against the brief, the references, the taste log, a rubric and a list of generic-UI tells, and returns a verdict and at most five ranked fixes a round, for up to three rounds. ([#85](https://github.com/osabased/osaskills/pull/85))
- Three scripts: `contact_sheet.py` lays renders out side by side, optionally over white, black and busy backdrops; `contrast.py` gives WCAG contrast ratios, including for see-through colours; and `theme_guard.py` fails a project's check on colours, fonts and text sizes written outside the theme module. ([#85](https://github.com/osabased/osaskills/pull/85))
- The rendering guide pins rhr to a commit of osabased's fork and lists where that build differs from Studio, from side-by-side comparisons. The Roblox checklist's engine defaults were read in Studio on 2026-10-19. ([#85](https://github.com/osabased/osaskills/pull/85))

#### Changed

- The rendering guide pins rhr `1.0.0rc1+osabased.14`, which lays a story's screen out while the story runs, so `AbsoluteSize`, `AbsolutePosition`, `TextBounds`, a layout's `AbsoluteContentSize` and a ScrollingFrame's canvas and window sizes read what Roblox works out and fire their change signals, where they read zero: a list's canvas set from its `AbsoluteContentSize` reads Studio's 280, where it read 0. A read in the same resumption that parents an element still reads zero, so the known gaps say to read sizes from a change signal, `task.defer` or a later frame, and What matches Studio names the reads compared with Studio's. Timers and `os.clock` run on story time, 1/60 s a frame. ([#88](https://github.com/osabased/osaskills/pull/88))
- Since rhr `1.0.0rc1+osabased.13`, UIGradients ramp over Studio's length at any Rotation, on frames, text and UIStrokes alike. Off the axes, osabased.10's matched Studio's only near 45°: at 30° on a 172 by 100 frame, rhr's ramp ran 157 px and Studio's 198. A UIStroke's gradient spans the stroke's outer edge, as Studio's does, so the known gaps drop it. ([#88](https://github.com/osabased/osaskills/pull/88))
- Since rhr `1.0.0rc1+osabased.12`, the id of a Decal, a Model or a sound draws nothing, as in Roblox, where rhr drew the asset's thumbnail. `missingAssets` lists such an image as `not an image`, and the Roblox checklist says to use an Image's id, which a Decal's `Texture` holds. An image whose download failed on rhr's side is tried again on the next render, where it waited a day, and its `missingAssets` reason says why the download failed, where it said `no thumbnail`. ([#88](https://github.com/osabased/osaskills/pull/88))
- Since rhr `1.0.0rc1+osabased.11`, ImageLabels draw their own Image whatever they're named: one whose name held "sunburst" or "rays", as "GrayscaleIcon" and "Arrays" do, drew rhr's own sunburst icon in its place, and a missing image under such a name wasn't listed in `missingAssets`. ([#88](https://github.com/osabased/osaskills/pull/88))
- Since rhr `1.0.0rc1+osabased.10`, UIGradients ramp as Studio's do off the axes and on text: a 45° ramp drew about a third too long, and text turned its gradient 10° counter-clockwise. The known gaps drop the off-axis gradient and add one on a UIStroke, which reaches its end colours a few pixels early, and the reviewer's example render notes and a behavioral scenario use the 9-slice gap in its place. ([#87](https://github.com/osabased/osaskills/pull/87))
- Since rhr `1.0.0rc1+osabased.9`, stories can read what Roblox works out in layout, where each read raised an error. `TextBounds`, `AbsoluteContentSize`, `GuiState` and the rest read as Studio reads them on a new element, before layout, `TextFits` and an image's `IsLoaded` read true, and the story's target reads `AbsolutePosition` 0, 0. The known gaps say to size UI from these with AutomaticSize or a layout, list what still errors, and say that a deprecated name such as `TextWrap` does nothing when set. ([#87](https://github.com/osabased/osaskills/pull/87))
- The install steps say which processes are rhr's background worker on Windows, and how to list them: the one whose command line names the tool's own Python, and the Python it starts. The agent stops both before installing, and leaves the workers of other rhr installs running. ([#87](https://github.com/osabased/osaskills/pull/87))
- Since rhr `1.0.0rc1+osabased.8`, stories read their device's gamepads and TV: `UserInputService:GetConnectedGamepads()` lists Gamepad1 on `console` and none elsewhere, and `GuiService:IsTenFootInterface()` is true only on `console`. Both were missing before, and reading `GuiService.TouchControlsEnabled` raised an error. The known gaps add that `under-touch-controls` goes by the preset, even for a story that turns the controls off. ([#87](https://github.com/osabased/osaskills/pull/87))
- Since rhr `1.0.0rc1+osabased.7`, `missingAssets` lists every image a render leaves empty, with the reason, the area it would cover and, where rhr knows, how to get it drawn. Before, it missed files built into the Roblox client, thumbnails and in-world GUIs' images, and could list an image that drew. `rhr check` keeps its `image-missing` warnings for images Roblox won't show either, so fixing every warning still holds, and reports images only rhr leaves out as info. The reviewer's render notes now say where each empty image is and what the game shows there, and the known gaps add `rbxthumb://` thumbnails, which rhr doesn't draw. ([#87](https://github.com/osabased/osaskills/pull/87))
