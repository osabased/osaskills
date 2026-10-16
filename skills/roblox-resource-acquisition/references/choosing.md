# Choosing a resource

Use this to evaluate or compare libraries and development tools. The goal is a well-supported choice, not exhaustive browsing.

Contents: [Brief](#brief) · [Find candidates](#find-candidates) · [Hard gates](#hard-gates) · [Compare and decide](#compare-and-decide) · [Community evidence](#community-evidence)

## Brief

Settle only what could change the choice: the capability and its lifecycle (creation, use, cleanup), client/server side and trust boundary, scale that matters, and project constraints (package manager, Luau or roblox-ts, license, a ban on third-party code). If the purpose is unclear and the answer could change the choice, ask one short question; don't ask what the project already shows.

A named target stays the target. Resolve which resource the user meant (canonical repository and package) and inspect it directly. Look for alternatives only when asked or when evidence shows a real fit, compatibility or safety problem, and raise that problem before substituting anything. If the project's `CLAUDE.md` lists a preferred resource for the role, prefer it unless it fits this task poorly. A transitive dependency or a package that is merely present is not an approved choice.

## Find candidates

Start Roblox libraries at the DevForum [Community Resources](https://devforum.roblox.com/c/resources/71) category, and tools at their ecosystem: GitHub, the Wally index, the pesde registry, npm and Rokit-installable releases. Search the terms Roblox authors use (cleanup → maid, janitor, trove; networking → remote, packet, serialization) and, after one plausible find, at least one `<candidate> vs` or `<candidate> alternative` query. Two to five serious candidates is usually enough.

From each serious candidate's canonical source, establish the current version or commit and how it installs, the API and lifecycle the task needs, the client/server model, dependencies and license, relevant open issues and release notes, and how a project can tell which version it has. Then search the chosen one for `deprecated`, `broken`, `security`, `exploit` and `successor`; only findings relevant to the intended use matter.

If a page or API won't load, try one other route to the same answer (the repository API instead of the web page), then say which claim stayed unchecked. Today's `main` branch doesn't identify a project's installed pin.

## Hard gates

Reject a candidate when any applicable gate fails:

- **Fit:** it can't do the required behavior.
- **Evaluability:** the source or behavior needed for safe use can't be inspected or tested.
- **Compatibility:** a known incompatibility with required Roblox or project behavior.
- **Safety:** unacceptable client trust, credential, remote-code or asset-script risk. Opaque loaders, `require(assetId)` of unreviewed code, or embedded secrets fail this gate.
- **License:** terms disallow the intended use.
- **Proof:** the required behavior fails reproducibly in an isolated test.

Unknown is not failure, but a material unknown must be checked before adoption. Absence of evidence is not evidence.

## Compare and decide

Compare survivors on only the criteria that could change the decision, applied the same way to each:

| Criterion | Good evidence |
| --- | --- |
| Fit | Solves the brief without major unrelated machinery |
| Correctness | Tests, clear source behavior, credible issue history |
| Integration cost | Simple install, few project assumptions, easy to remove |
| Maintenance | Compatible recent releases or responsive fixes; a stable library need not release often |
| API and docs | Public API and lifecycle are explicit and match the source |
| Security | Preserves server authority; no suspicious loaders |
| Dependencies | Small, justified dependency graph |
| Performance | Evidence matches the project's real scale |

Prefer evidence in roughly this order: a test you ran, source plus canonical docs, maintainer release notes and issues, maintainer posts, independent user reports, popularity. Stars and download counts help discovery; they don't prove correctness. Don't invent scores or weights. Before rejecting a serious candidate on one weakness, count the cost of a small, bounded workaround.

For a real tie, prefer the smaller surface, then better testability, clearer lifecycle and failure behavior, fewer security-sensitive behaviors, easier removal and more current maintenance. Missing evidence is not a tie. When the choice hinges on a preference only the user can decide, lay out the options and ask.

For a delivery or tooling decision (Wally vs pesde, Rokit vs Aftman, vendoring), compare the routes separately from the library: exact-pin support, restore and update behavior, upkeep. Keep a healthy existing manager; another tool's newer release is not a reason to migrate.

## Community evidence

Use community experience for broad discovery, real comparisons and a risk check before adopting something new, not for routine use of an adopted library. Read DevForum comparison and Scripting Support threads, repository issues and maintainer docs; awesome lists are leads, not endorsements. For a deciding claim, note its author, date, version and whether it is firsthand. Reposts count once, and likes don't establish consensus. A demonstrated relevant defect outweighs popularity, and community preference never overrides a hard gate or the user's choice. Say what you read, with dates, and how it affected the decision.
