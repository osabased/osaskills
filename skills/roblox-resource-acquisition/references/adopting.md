# Adopting a resource

Use this when adding, upgrading, replacing or removing a project dependency or development tool.

## Scope

A normal "add/use a library" request covers choosing (when needed), pinning, installing, integrating, running the project's checks and updating the `CLAUDE.md` resource list. Carry that through routine reversible steps without asking again. An explicit evaluation-only, download-only or integration-only request sets its own narrower boundary.

Bring these to the user with a concrete proposal instead of acting: costs, major architecture changes, replacing an adequate existing dependency, a conflict with existing project guidance, or a choice the evidence can't settle.

## Check for conflicts first

Read the project's `CLAUDE.md` (and files it imports with `@path`) and any guide it points to, such as the structure guide at `.claude/roblox/project.md`. A conflict exists only when existing guidance picks a different resource for the **same role**. Adjacent capabilities don't conflict. When there is a conflict, show the user both and change nothing until they decide.

A pin fixed by another document stays fixed. For example, a project using the ModuleLoader SSA layout from `structure-roblox-projects` changes its loader pin only through that skill's upgrade steps. You may install and check that exact target, but don't substitute or upgrade it.

## Pin and install

Use the project's existing manager. Don't migrate managers as a side effect.

- **Wally:** add `name = "scope/package@=X.Y.Z"` for an exact pin (a bare `X.Y.Z` is a caret range), run `wally install`, and keep `wally.lock` in version control. Server-only packages go in `[server-dependencies]`. Regenerate type stubs (`wally-package-types`) if the project uses them.
- **pesde:** add the dependency with an exact version, run `pesde install`, and keep `pesde.lock`.
- **npm (roblox-ts):** `npm install --save-exact <package>@X.Y.Z` and keep `package-lock.json`.
- **Tools (Rokit):** `rokit add owner/tool@X.Y.Z`, which writes `rokit.toml`. Aftman is unmaintained; keep it only where the project already uses it.
- **Vendored source or `.rbxm`:** record the source URL, version or commit and SHA-256 next to the file (for example in a header comment or the project guide), and preserve the license notice.

Map the package into the DataModel through the project's existing Rojo mapping (normally `ReplicatedStorage/Packages` and `ServerScriptService/ServerPackages`). Never run install scripts or loaders you haven't inspected.

## Check that it works

Run the smallest checks that show the intended use works at the exact pin:

1. It installs and resolves: the require path or import works, or the tool runs and prints the expected version.
2. Static analysis passes where the project uses it (`luau-lsp analyze`, `selene`, the roblox-ts compiler).
3. The required behavior works: a small happy path in a test runner, a Lune script, or a Studio play test, as appropriate.
4. For something that owns cleanup (connections, threads, instances), destroying it releases what it created.

Require Studio runtime evidence only for claims that depend on the engine. A development tool can be checked with its own CLI or a build. If a needed check can't run here, the adoption is pending: say which check is missing and how to run it, and don't list the resource as adopted yet.

Re-check volatile facts (current version, API, deprecation) at adoption time instead of relying on memory or old notes.

## Keep the resource list in CLAUDE.md

Once at least one resource is adopted, keep this owned block in the project root's `CLAUDE.md`:

```markdown
<!-- roblox-resource-acquisition:onboarding:start -->
## Roblox resources

Use these project-standard resources for their roles. Raise a conflict with other project guidance before changing either.

- **RESOURCE** — ROLE. [Optional: "Use the `CHILD` skill."] [Optional: known issue or blocked use.]
<!-- roblox-resource-acquisition:onboarding:end -->
```

1. Edit only the project root's `CLAUDE.md`, or a file it imports (such as `@AGENTS.md`) if the project keeps its instructions there. If no `CLAUDE.md` exists, create one containing only the block.
2. Change only the text between the markers; append the block if the markers are absent.
3. List adopted resources only. The manifest and lock hold the pin; don't duplicate versions here.
4. Add "Use the `CHILD` skill." only when that child is installed for the project.
5. When a known defect blocks part of a resource's use, keep the entry and say which use is blocked, so later sessions don't rediscover it.
6. Remove the whole block when nothing is adopted any more.

An authorized adoption also authorizes these block edits once the conflict check passes.

If sessions usually start in a parent folder of the Roblox project, the nested `CLAUDE.md` loads only when Claude works in that folder. When the parent's `CLAUDE.md` is in scope, add one pointer line to it, such as `For Roblox resource work under game/, read game/CLAUDE.md first.`

## Upgrade, replace or remove

- **Upgrade:** read the release notes and breaking changes between the current and target versions, update the pin and lock, rerun the checks the change affects, and update any installed child whose pin changed (or say it is now out of date). A newer release alone is not a reason to upgrade.
- **Replace:** only on the user's request or with their agreement. Migrate call sites, remove the old dependency, and update the resource list.
- **Remove:** delete the dependency and its mappings, confirm nothing still requires it, and remove its resource-list entry.

## Security defaults

- Inspect scripts in unfamiliar packages and models before they enter a real project.
- Avoid opaque or dynamically fetched code (`require(assetId)`, `loadstring` of remote content) without strong justification.
- Treat auto-updating or range-pinned packages as a supply-chain decision; prefer exact pins.
- Never put secrets or API keys in source.
- Keep server authority and validate everything the client sends.
