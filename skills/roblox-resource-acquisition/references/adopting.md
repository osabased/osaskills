# Adopting a resource

Use this when adding, upgrading, replacing or removing a project dependency or development tool.

Contents: [Scope](#scope) · [Check for conflicts first](#check-for-conflicts-first) · [Pin and install](#pin-and-install) · [Check that it works](#check-that-it-works) · [Clone the library skill](#clone-the-library-skill) · [Keep the resource list in CLAUDE.md](#keep-the-resource-list-in-claudemd) · [Guard a banned feature](#guard-a-banned-feature) · [Upgrade, replace or remove](#upgrade-replace-or-remove) · [Security defaults](#security-defaults)

## Scope

A normal "add/use a library" request covers choosing (when needed), pinning, installing, integrating, running the project's checks, cloning the library skill, updating the `CLAUDE.md` resource list and guarding any feature the project bans. Carry that through routine reversible steps without asking again. An explicit evaluation-only, download-only or integration-only request sets its own narrower boundary.

Bring these to the user with a concrete proposal instead of acting: costs, major architecture changes, replacing an adequate existing dependency, a conflict with existing project guidance, or a choice the evidence can't settle.

## Check for conflicts first

Read the project's `CLAUDE.md` (and files it imports with `@path`) and any guide it points to, such as the structure guide at `.claude/roblox/project.md`. A conflict exists only when existing guidance picks a different resource for the **same role**. Adjacent capabilities don't conflict. When there is a conflict, show the user both and change nothing until they decide.

A pin fixed by another document stays fixed. For example, a project using the ModuleLoader SSA layout from `structure-roblox-projects` changes its loader pin only through that skill's upgrade steps. You may install and check that exact target, but don't substitute or upgrade it.

## Pin and install

Use the project's existing manager. Don't migrate managers as a side effect. When the [catalog](library-skills.md) has a skill for the library, its pin is the latest stable release the guidance was reviewed against; pin that version unless the project needs another, so the skill applies.

- **Wally:** add `name = "scope/package@=X.Y.Z"` for an exact pin (a bare `X.Y.Z` is a caret range), run `wally install`, and keep `wally.lock` in version control. Server-only packages go in `[server-dependencies]`. Regenerate type stubs (`wally-package-types`) if the project uses them.
- **pesde:** add the dependency with an exact version (`version = "=X.Y.Z"`, or a git `rev`), run `pesde install`, and keep `pesde.lock`.
- **npm (roblox-ts):** `npm install --save-exact <package>@X.Y.Z` and keep `package-lock.json`.
- **Tools (Rokit):** `rokit add owner/tool@X.Y.Z`, which writes `rokit.toml`. Aftman is unmaintained (as checked 2026-10); keep it only where the project already uses it.
- **Vendored source or `.rbxm`:** record the source URL, version or commit and SHA-256 next to the file (for example in a header comment or the project guide), and preserve the license notice.

Map the package into the DataModel through the project's existing Rojo mapping (normally `ReplicatedStorage/Packages` and `ServerScriptService/ServerPackages`). Never run install scripts or loaders you haven't inspected.

## Check that it works

Run the smallest checks that show the intended use works at the exact pin:

1. It installs and resolves: the require path or import works, or the tool runs and prints the expected version.
2. Static analysis passes where the project uses it (`luau-lsp analyze`, `selene`, the roblox-ts compiler).
3. The required behavior works: a small happy path in a test runner, a Lune script, or a Studio play test, as appropriate.
4. For something that owns cleanup (connections, threads, instances), destroying it releases what it created.

Require Studio runtime evidence only for claims that depend on the engine. A development tool can be checked with its own CLI or a build.

If the install or a needed check can't run here, the adoption is pending. Don't stop at the blocked step: finish everything that doesn't depend on it, such as code that doesn't need the installed package, any guard with its break-test, and the `CLAUDE.md` entry. Then say which steps are missing and give the exact commands to run them.

Re-check volatile facts (current version, API, deprecation) at adoption time instead of relying on memory or old notes.

## Clone the library skill

When the catalog has a skill for the library, clone it as [library skills](library-skills.md#clone-into-a-project) describes, including pending installs and other pins, and read the clone's `SKILL.md`. When the catalog has none, offer to [write one](writing-library-skills.md) in one sentence, and write it only when the user asks.

## Keep the resource list in CLAUDE.md

Once at least one resource is adopted, keep this owned block in the project root's `CLAUDE.md`:

```markdown
<!-- roblox-resource-acquisition:onboarding:start -->
## Roblox resources

Use these project-standard resources for their roles. Raise a conflict with other project guidance before changing either.

- **RESOURCE** — ROLE. [Optional: "Use the `roblox-LIBRARY` skill."] [Optional: blocked use and its guard.]
<!-- roblox-resource-acquisition:onboarding:end -->
```

1. Edit only the project root's `CLAUDE.md`, or a file it imports (such as `@AGENTS.md`) if the project keeps its instructions there. If no `CLAUDE.md` exists, create one containing only the block.
2. Change only the text between the markers; append the block if the markers are absent.
3. List adopted resources only, with one exception: a pending adoption whose use the project bans gets its entry now, with the ban and its guard, ending in "Pending: CHECKS not run yet." Remove that note once the checks pass. The manifest and lock hold the pin; don't duplicate versions here.
4. Add "Use the `roblox-LIBRARY` skill." only when that skill is in the project's `.claude/skills/`.
5. When the project bans part of a resource's use (a known defect, a security hole), keep the entry, say which use is blocked and why, and name its guard if it has one, so later sessions don't rediscover it.
6. Remove the whole block when nothing is adopted any more.

An authorized adoption also authorizes these block edits once the conflict check passes.

If sessions usually start in a parent folder of the Roblox project, the nested `CLAUDE.md` loads only when Claude works in that folder. When the parent's `CLAUDE.md` is in scope, add one pointer line to it, such as `For Roblox resource work under game/, read game/CLAUDE.md first.`

## Guard a banned feature

A ban in `CLAUDE.md` relies on every session reading it. When breaking it would be a security hole, permanent or silent (for example a networking library's client-to-server events whose receive path has a known flaw), add a guard to the project's check script so a violation fails the build. Leave style and preference bans in `CLAUDE.md`.

- **Pin it to the version you reviewed.** Read the library's version from the lockfile and fail when it differs, with a message such as "reviewed against 0.18.9, found 0.19.0: re-review this guard". A guard that silently passes after the library changes is worse than none.
- **Say how to fix it.** The message names the rule, the file and line, and how to change the rule on purpose.
- **Break-test it once:** make the violation, confirm the check fails with that message, revert.
- **List it** with the project's other guards (in the guide or the guard script's header) and name it in the resource entry.

When the project follows `structure-roblox-projects`, its checks reference describes where guards live and how they run.

## Upgrade, replace or remove

- **Upgrade:** read the release notes and breaking changes between the current and target versions, update the pin and lock, and rerun the checks the change affects. Re-review every guard pinned to the old version, then update its version. Re-clone the library skill when the catalog pins the new version; otherwise remove the clone and its "Use the skill" line, or say the guidance is now out of date. A newer release alone is not a reason to upgrade.
- **Replace:** only on the user's request or with their agreement. Migrate call sites, remove the old dependency, its library skill and its guards, and update the resource list.
- **Remove:** delete the dependency and its mappings, confirm nothing still requires it, and remove its library skill, guards and resource-list entry.

## Security defaults

- Inspect scripts in unfamiliar packages and models before they enter a real project.
- Avoid opaque or dynamically fetched code (`require(assetId)`, `loadstring` of remote content) without strong justification.
- Treat auto-updating or range-pinned packages as a supply-chain decision; prefer exact pins.
- Never put secrets or API keys in source.
- Keep server authority and validate everything the client sends.
