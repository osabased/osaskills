# Resource Search Playbook

Use this when broad discovery is required after checking built-ins/project dependencies and the external user/project curated registry described in [curated-registry.md](curated-registry.md). The objective is a small set of credible candidates, not exhaustive browsing. Curated resources are already trusted by policy; broad discovery is for needs the curated registry does not adequately cover, material contradiction checks, or explicit alternative/comparison requests.

For development tools, supplement or replace forum discovery with capability-directed searches in the canonical tool ecosystem, repositories and package sources. Tool suitability is not conditional on having a DevForum announcement. Apply the same reliability/maintenance evidence standard and follow the canonical source.

## 1. Translate the need into search terms

Start with the capability, then expand only with terms Roblox authors commonly use for the same kind of resource.

Examples:

- networking -> networking, RemoteEvent, replication, packet, serialization;
- pathfinding -> pathfinding, NPC movement, navigation;
- projectiles -> projectile, raycast, FastCast, ballistics;
- state/data replication -> replication, state, replica, synchronized table;
- persistence -> datastore, player data, profile, persistence;
- UI -> UI framework, component, interface, GUI;
- signals/events -> signal, event, RBXScriptSignal alternative;
- cleanup -> cleanup, maid, janitor, trove;
- hit detection -> hitbox, raycast hitbox, spatial query.

Do not let synonyms silently broaden the requirement. They are discovery terms only.

## 2. Review topic experience and discover resources

Apply [community-evidence.md](community-evidence.md) before finalizing the shortlist. Search relevant topic-level recommendations and comparative discussions as well as resource announcements. DevForum Scripting Support, canonical repository discussions/issues and accessible Roblox OSS material may reveal approaches or tradeoffs that Community Resources announcements omit. Community directories are discovery leads, not the trusted-curated registry or a vote.

For resource announcements, search Community Resources directly.

Prefer results from:

- [Roblox DevForum Resources](https://devforum.roblox.com/c/resources/71)
- Community Resources topics beneath that category;
- relevant DevForum tag pages;
- domain-restricted web search targeting `devforum.roblox.com` when forum search is insufficient.

Useful query shapes:

- `site:devforum.roblox.com <capability> "Community Resources" Roblox`
- `site:devforum.roblox.com/t <capability> module Roblox`
- `<capability> site:devforum.roblox.com/c/resources`

Search both current/recent results and established resources when maturity matters. Recency alone is not quality; age alone is not obsolescence.

## 3. Open the actual thread

For every serious candidate, inspect the thread rather than relying on a search card.

Extract:

- the original post's actual claims;
- edit/update markers;
- install/source/docs links;
- resource status such as old, deprecated, rewrite, successor, beta, paid, or abandoned;
- maintainer replies that materially change setup or limitations;
- recent reports of breakage or incompatibility.

Do not read every reply. Search within long threads for terms such as:

`deprecated`, `obsolete`, `old`, `rewrite`, `successor`, `bug`, `broken`, `security`, `exploit`, `license`, `github`, `docs`, `release`, `version`, `update`.

Read surrounding context before treating a hit as evidence.

## 4. Follow canonical links

If the thread points to GitHub, Wally, Pesde, documentation, a package/model, or another canonical release source, inspect that source before selection.

Prefer canonical source for:

- current version/release;
- installation;
- API names and signatures;
- dependencies;
- source behavior;
- tests;
- license;
- open issues and release notes.

The DevForum thread remains useful for provenance, developer discussion, migration warnings, and real-world failure reports.

## When an evidence route fails

Use a bounded fallback that can answer the missing question before declaring canonical evidence or compatible execution unavailable. Inspect relevant available capabilities: a connected repository API may resolve a commit or read an exact source file when browser or shell access fails. For a broken CLI shim, use project/tool-manager configuration to locate an already installed versioned executable in that tool's cache; run its version command and check identity/integrity before using it. A compatible existing harness may cover a non-engine claim. Keep normal permission and mutation boundaries.

Choose fallbacks from the observed failure and required claim, stopping when the claim is established or remaining relevant routes are unavailable, incompatible or disproportionate. Do not impose a universal retry count, sweep unrelated caches, install a new toolchain just to avoid a blocker, or repeat an unchanged failing route. Record what was attempted and the exact remaining unavailable claim.

Resolving today's moving branch head does not bind earlier reads from `main`/`master` or identify a project's installed pin. Re-read material source at the resolved immutable selector, or label the earlier observation as unbound; inspect the actual project pin when that is the target. A discovered executable or source coordinate is a route to proof, not proof itself.

## 5. Search for alternatives deliberately

After finding one plausible resource, run at least one alternative-oriented query unless the need is truly unique.

Use:

- same capability + `library` / `module` / `framework`;
- candidate name + `alternative` or `vs`;
- relevant DevForum tag page;
- the same capability sorted mentally across recent and established resources.

Stop once you have enough evidence to show that additional candidates are unlikely to change the decision. Usually 2-5 serious candidates is sufficient.

## 6. Search against the candidate

Before establishing verified-acquisition trust for a newly discovered resource, perform a short adversarial search around the selected resource:

- `<resource> deprecated`
- `<resource> broken`
- `<resource> security`
- `<resource> exploit`
- `<resource> bug`
- `<resource> successor`
- `<resource> Roblox update`

Only findings relevant to the required behavior matter. Do not reject a library because unrelated users have unrelated problems.

## 7. Evidence discipline

For each material selection claim, be able to point to one of:

- executed proof;
- source code;
- canonical docs/release notes/issues;
- DevForum maintainer statement/discussion or inspected firsthand community experience, with date/version/context and independence assessed under [community-evidence.md](community-evidence.md);
- current Roblox Creator Hub platform documentation.

If the search yields only marketing claims and no evaluable implementation, downgrade or reject the candidate rather than filling gaps with assumptions.
