===== R1 =====
**Recommendation (evaluation only, no files changed): don't add Blink yet. Start with plain RemoteEvents. Revisit Blink when you have many remotes or high-frequency traffic.**

**Where the project is now**
- There is no networking yet. `src` has no remotes at all.
- Coin balances live only in server memory (`Coins.luau`). The client mounts UI and never talks to the server (`init.client.luau`).
- The only thing that would cross the wire today is a server-to-client "coins changed" or "round state" update. That is a handful of low-frequency events.

**Why plain RemoteEvents fit for now**
- Blink earns its keep with many events, large or frequent payloads, or the need for typed, validated schemas. This game has none of those yet.
- Blink adds a CLI step, generated modules and a `.blink` schema. You would also need `blink` as a pesde dev tool, and the project doesn't have one yet.
- Server-to-client events carry no trust risk, so Blink's server-side validation adds little for a coin-and-round loop.

**What would change my mind**
- You add roughly 10 or more remotes, or a hot path such as per-frame positions or many coin-pickup events.
- You want enforced schemas on client-to-server requests (buy, claim, pickup).
- You adopt TypeScript.

**If you do adopt Blink**
- The catalog's pinned version, 0.18.9, is current.
- That version has a known receive-side DoS issue ([issue #45](https://github.com/1Axen/blink/issues/45)). The generated server parses the whole incoming buffer before any handler runs. Schema bounds don't stop that. Before you accept untrusted client-to-server events in production, you would need a tested byte and rate budget in the receive path.
- The 1.0.0 pre-releases are a rewrite, so don't mix their docs with 0.18.9.
- Requiring a generated module starts networking immediately, so keep it unrequired until you mean to go live.

**Cheap prep that keeps migration easy**
- Put all remotes behind one small shared module, for example `src/shared/Network.luau`, instead of scattering `FireServer` and `OnClientEvent` calls. Swapping in Blink later then only touches that one file.
- Validate client input on the server regardless of transport.

**What I read and ran**
- **Read:** the Blink skill docs, the project's `src` and `pesde.toml`, and the skill's selection criteria.
- **Ran:** the update check, which showed Blink 0.18.9 as current.
- **Not done:** I didn't install Blink, test it, or do a fresh DevForum or community search. I also haven't compared it against other networking libraries such as ByteNet, since you asked only about Blink versus RemoteEvents.

----- R1 commands run -----
$ cd "./.claude/skills/roblox-resource-acquisition" && python scripts/check_updates.py 2>&1 | head -20

----- R1 changed no files -----

===== R2 =====
**Recommendation: don't adopt Blink yet. Stay on plain RemoteEvents until the game has a real client-to-server surface, and revisit Blink then.** This is evaluation only. I changed nothing.

**What I checked**
- `src/` has no remotes at all today. The server has `Coins` and `Round`, and the client has a Vide UI plus Charm state.
- I read the Blink skill for pin 0.18.9. I haven't run Blink in this project, and I haven't checked upstream issues beyond what the skill records.

**Why not now**
- **No problem for it to solve.** Blink pays off with many events, structured payloads and bandwidth pressure. A coin-run round game will probably need only a handful of events, such as coin count, round state and a collect request. Typed plain remotes cover that.
- **Receive-side DoS risk at this pin.** In 0.18.9 the generated server parses the whole incoming buffer before any handler runs (issue #45). A client can send an oversized buffer, and schema bounds and handler throttling don't stop it. Adopting Blink for client-to-server events means writing and testing your own pre-decode byte and rate budget. With plain remotes you write server-side validation and rate limits anyway. With Blink you also have to guard its parser.
- **Extra build step and project weight.** You'd add a `.blink` schema, a pesde dev-dependency on the `lune` target, generated files that must never be hand-edited, and a regenerate step. That step would need to go into `scripts/check.sh` so schema and output can't drift. Requiring the generated module also starts networking process-wide, with no teardown.
- **Pre-release churn.** 1.0.0 pre-releases are a rewrite with different syntax, so a later upgrade is a migration, not a bump.

**What Blink would give you**
- Compact binary serialization, so less bandwidth.
- One schema as the source of truth, with generated types on both sides.
- Range-checked fields, which are useful but are serialization, not authorization. You'd still validate ownership, cost and cooldown on the server.

**When to switch**
- You have around a dozen or more events.
- You send high-frequency or large payloads, such as per-coin or per-player state.
- Bandwidth shows up in profiling.

If you reach that point, adopt it through the acquisition flow:
1. Pin `=0.18.9`.
2. Clone the `roblox-blink` skill.
3. Add Blink to the `CLAUDE.md` resource list.
4. Add the regenerate step to `check.sh`.
5. Deal with issue #45 before enabling untrusted client events.

**Cheaper step now:** put all remotes behind one small `src/shared` module with typed wrappers, and validate every server handler. That keeps a later move to Blink mostly mechanical.

**Unchecked:** I didn't re-check whether Blink has fixed #45 in a newer release. Check that before deciding later.

----- R2 commands run -----
$ cd "." && cat pesde.toml rokit.toml && ls scripts

----- R2 changed no files -----

===== R3 =====
**Recommendation: stay on plain RemoteEvents for now. Revisit Blink once the networking surface grows, and only with a receive-side limit in place.** This is evaluation-only. I changed no files.

**What the game sends today**
- There are no remotes at all. `Round.luau` and `Coins.luau` run entirely on the server, using `Touched` to award coins.
- The client has no way to send anything to the server, so there is no trust boundary yet.
- Blink's main benefits are compact buffer serialization and typed schemas. Neither helps when almost nothing is sent.
- Blink is not in `pesde.toml`, so adopting it would add a package, a `.blink` schema, a compile step and generated files. I haven't compared other networking libraries such as ByteNet.

**Why not now**
- **Integration cost:** you'd maintain a schema and a generated-code workflow, and `bash scripts/check.sh` would likely need a step to catch stale generated output.
- **Likely traffic:** a coin-count update per player and round state changes are small and infrequent. The bandwidth saving would be negligible.
- **Known risk at the pinned version:** the Blink skill documents a receive-side DoS in 0.18.9 ([issue #45](https://github.com/1Axen/blink/issues/45)). The generated server parses the whole incoming buffer before any handler runs, so a client can send an oversized one. Schema bounds don't prevent this. Blink would add risk exactly where plain remotes are simple to validate.
- **Version churn:** 1.0.0 pre-releases exist upstream and are a rewrite, so the syntax you adopt now may change.

**When Blink would be worth it**
- Many client-to-server or high-frequency events, such as per-frame input or many replicated entities.
- A larger set of event shapes where one typed schema shared by client and server beats hand-written remote checks.
- Bandwidth showing up as a real problem in profiling.

**Cheaper option for now**
Put a thin typed wrapper in `src/shared` around a few RemoteEvents. Validate each argument type on the server. Add per-player rate limiting. Keep client state in Charm. This keeps the abstraction small, and a later move to Blink only touches that one wrapper.

**If you adopt Blink later**
- Pin 0.18.9 exactly through pesde.
- Add a tested pre-decode byte and rate budget before enabling any untrusted client-to-server event.
- Give it a unique `RemoteScope`.
- Treat schema types as serialization only, and validate ownership, cost and cooldown on the server.

**Evidence and gaps**
I read the Blink skill (reviewed 2026-10-03 against 0.18.9) and the project source. I didn't run Blink here, and I didn't check upstream issues or the DevForum for newer information. A Blink 0.18.x release that fixes #45 is unverified.

----- R3 changed no files -----

===== R4 =====
**Recommendation: Blink is a reasonable fit, but don't adopt it yet. Start with plain RemoteEvents behind one small wrapper, and move to Blink when the remote count or payload size justifies a schema.** This is evaluation only. I changed no files and installed nothing.

**What I checked**
- `src/` has no remotes today. The server has `Coins` and `Round`, and the client has a Vide UI. So there's no networking to migrate and no measured bandwidth problem.
- The project uses pesde, which fits Blink. The Blink skill pins `1axen/blink` 0.18.9 as a `lune` dev dependency, run as a CLI. That's a small install and easy to remove.
- I read the catalog's Blink skill, which was reviewed on 2026-10-03. I did not run Blink or check DevForum or upstream issues beyond what that skill cites.

**Where Blink would help this game**
- The schema is a single source of truth. A coin-run game will have a few events: `CoinsChanged`, round state, and a pickup or claim request. Typed generated `Fire` and `On` calls keep the client and server in sync.
- It gives you range-bounded types and compact buffer serialization. Both are useful if you send frequent coin or round updates to many players.
- It supports unreliable events, with a 1000-byte payload limit.

**Where it costs you**
- **Receive-side DoS risk ([issue #45](https://github.com/1Axen/blink/issues/45)).** In 0.18.9 the generated server code parses the whole incoming buffer before any handler runs. Schema bounds don't protect against that. Before you accept untrusted client-to-server events, you'd need a tested byte and rate budget in the receive path. A plain RemoteEvent handler can validate its arguments before doing any work. This is the strongest reason not to adopt it casually.
- **Generated code.** It adds a compile step, and the generated files must never be edited by hand. A failed compile can leave stale outputs. You also need a check, via `scripts/check.sh`, to keep them current.
- **Startup side effects.** Requiring a generated module immediately creates remotes and starts connections, and there's no teardown. That works against your Janitor-based cleanup ownership.
- **Version risk.** 1.0.0 pre-releases are a rewrite with different syntax, so an upgrade later is a migration.
- **Types aren't authorization.** You still validate ownership, cooldowns and similar checks on the server, exactly as with RemoteEvents.

**Why RemoteEvents first**
- With a handful of low-frequency events, Blink's bandwidth savings are negligible.
- A thin wrapper module in `src/shared`, with one function per event and server-side validation, gives you the same call-site shape. Blink's generated `Net.Event.Fire/On` API can then replace it later without touching callers.
- It avoids the #45 risk and the build step until you actually need them.

**When to switch**
- You have roughly a dozen or more remotes, or high-frequency or per-player replication such as many coins or positions per tick.
- Profiling shows network cost.
- You're willing to add a pre-decode budget for client-sent events and a guard that keeps the generated output current.

If you do adopt it, I'd follow the `roblox-resource-acquisition` adoption flow:
- Pin 0.18.9.
- Clone the `roblox-blink` skill.
- List it in `CLAUDE.md`.
- Give it a unique `RemoteScope`.
- Add a guard against hand-edited generated files.

----- R4 commands run -----
$ cd "." && cat pesde.toml default.project.json 2>/dev/null; ls

----- R4 changed no files -----
