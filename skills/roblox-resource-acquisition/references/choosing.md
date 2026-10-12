# Choosing a resource

Use this to find, evaluate or compare libraries and development tools. The goal is a well-supported choice, not exhaustive browsing.

Contents: [Brief](#1-write-a-short-brief) · [Existing options](#2-check-what-already-exists) · [Search](#3-search) · [Inspect](#4-inspect-serious-candidates) · [Hard gates](#5-apply-the-hard-gates) · [Compare](#6-compare-and-decide) · [Community evidence](#community-evidence) · [When a source fails](#when-a-source-fails)

## 1. Write a short brief

From the request and the project, settle only what could change the choice:

- the capability actually needed, its behavior and lifecycle (creation, normal use, cleanup);
- client/server side and any trust boundary;
- scale or performance that matters;
- project constraints: package manager, Luau or roblox-ts, licensing, a ban on third-party code;
- each resource the user named, and its role (use, compare, replace, avoid).

If the purpose is unclear and the answer could change the choice, ask one short question (or a small batch) before selecting. Keep researching meanwhile. Don't ask about things the project already shows.

A named target stays the target. Resolve which resource the user meant (canonical repository and package), inspect it directly, and look for alternatives only when asked or when evidence shows a real fit, compatibility or safety problem. Raise that problem before substituting anything. A resource named only as something to avoid or replace is not a target.

## 2. Check what already exists

Before searching, rule out:

- a Roblox built-in that solves the need cleanly;
- a dependency the project already declares, or first-party project code;
- a small local implementation that is simpler than a dependency;
- a project rule against third-party code.

Look only at project surfaces plausibly related to the need: manifests and locks, package folders, requires, nearby code and project docs. If the project's `CLAUDE.md` or docs list preferred resources, prefer the best-fitting one without broad discovery, unless it is a poor fit for this task or the user asks for alternatives. A transitive dependency, or a package that is merely present, is not an approved choice.

Search is a means, not the goal. Stop here when an existing option suffices.

## 3. Search

For Roblox libraries, start with the DevForum [Community Resources](https://devforum.roblox.com/c/resources/71) category. For development tools, start with the tool's ecosystem: GitHub, the Wally index, the pesde registry, npm, and Rokit-installable releases. A tool needs no DevForum thread.

Expand the capability into terms Roblox authors use, without widening the requirement:

- networking → RemoteEvent, replication, packet, serialization;
- signals/events → signal, event, RBXScriptSignal alternative;
- cleanup → maid, janitor, trove;
- persistence → datastore, player data, profile;
- state replication → replica, synchronized table;
- UI → UI framework, component, reactive;
- projectiles / hit detection → raycast, FastCast, hitbox, spatial query.

Useful queries: `site:devforum.roblox.com <capability> "Community Resources"`, `<capability> roblox luau library`, `<candidate> vs`, `<candidate> alternative`.

After finding one plausible resource, run at least one alternative-oriented query unless the need is unique. Two to five serious candidates is usually enough; stop when more results would not change the decision. Recency is not quality, and age is not obsolescence.

## 4. Inspect serious candidates

Open the actual thread and follow it to the canonical source. Don't rely on search cards. In long threads, search for `deprecated`, `rewrite`, `successor`, `broken`, `security`, `exploit`, `license` and `version` rather than reading every reply, and read the surrounding context of each hit.

From the canonical source (repository, releases, package page, docs), establish:

- current version or commit, and how it is installed;
- the public API the task needs, and the lifecycle (init, use, cleanup);
- client/server model and replication assumptions;
- dependencies and license;
- relevant open issues and recent release notes;
- how a project can tell which version is installed.

Then run a short adversarial search on the chosen candidate: `<resource> deprecated`, `broken`, `security`, `exploit`, `successor`, `Roblox update`. Only findings relevant to the intended use matter.

## 5. Apply the hard gates

Reject a candidate when any applicable gate fails:

- **Fit:** it can't do the required behavior.
- **Evaluability:** the source or behavior needed for safe use can't be inspected or tested.
- **Compatibility:** a known incompatibility with required Roblox or project behavior.
- **Safety:** unacceptable client trust, credential, remote-code or asset-script risk. Opaque loaders, `require(assetId)` of unreviewed code, or embedded secrets fail this gate.
- **License:** terms disallow the intended use.
- **Proof:** the required behavior fails reproducibly in an isolated test.

Unknown is not failure, but a material unknown must be checked before adoption. Absence of evidence is not evidence.

## 6. Compare and decide

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

Prefer evidence in roughly this order: a test you ran, source plus canonical docs, maintainer release notes and issues, maintainer DevForum posts, independent user reports, popularity. Stars, likes and download counts help discovery; they don't prove correctness.

Don't invent scores or weights. Keep measurements in real units. Before rejecting a serious candidate on one weakness, consider whether a small, bounded workaround would change the result, and count its cost.

For a real tie, prefer the smaller surface, then better testability, clearer lifecycle and failure behavior, fewer security-sensitive behaviors, easier removal, and more current maintenance. Don't prefer features the brief doesn't need. Missing evidence is not a tie.

Recommend the best-supported fit. State the decisive evidence, the strongest alternative's losing tradeoff, material uncertainty and what would change the choice. When the choice hinges on a preference only the user can decide, lay out the concrete options and ask. Don't manufacture a winner.

For a delivery or tooling decision (Wally vs pesde, Rokit vs Aftman, vendoring), compare the routes separately from the library: exact-pin support, restore and update behavior, and upkeep. Keep a healthy existing manager; another tool's newer release is not a reason to migrate.

## Community evidence

Use community experience for broad discovery, meaningful comparisons and a quick risk check before adopting something new. Don't survey the community for routine use of an adopted library.

Look at DevForum comparative and Scripting Support threads (not only resource announcements), repository issues and discussions, and maintainer docs. Awesome lists and directories are discovery leads, not endorsements. A maintainer's own material speaks for that maintainer, not as an independent review.

For a deciding claim, note its author, date, version and context, and whether it is firsthand. Reposts of the same claim count once. Likes, stars and repeated names do not establish consensus. Describe agreement only within what you actually read, and resolve disagreement by version and environment where you can. A demonstrated relevant defect outweighs popularity, and community preference never overrides a hard gate or the user's choice.

Stop when more reading is unlikely to change the choice. Include a short note with the recommendation: what you read (with dates), where sources agreed or disagreed, and how it affected the decision.

## When a source fails

If a page, API or tool won't load, try one other route that can answer the same question: the repository API instead of the web page, or an already-installed versioned binary in the tool manager's cache instead of a broken shim. Don't install a new toolchain just to get around a blocker, and don't retry an unchanged failing route. Say which claim stayed unchecked.

Resolving today's `main` branch does not identify a project's installed pin. Inspect the project's actual pin when that is what matters.
