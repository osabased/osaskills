# Rubrics

Scaffold: Rojo + Wally + pesde project. `wally.toml` declares Janitor 1.18.3, LemonSignal 2.0.0 and Charm 0.11.1; `pesde.toml` declares Vide (commit `5ed4c01`) and Blink 0.18.9 (dev, lune target). There is no `rokit.toml`. The agent cannot run commands, search the web or use subagents.

Score each criterion 1 (met) or 0 (missed). Also give an overall 0–10 for how useful and correct the answer is for a working Roblox developer.

## q-addsignal

Ground truth: `wally.toml` already declares `data-oriented-house/lemonsignal@2.0.0`. The best answer uses it and adds no new dependency.

- A1 Notices LemonSignal is already a declared dependency.
- A2 Does not add a second signal library or a hand-rolled Signal without justification.
- A3 Shows correct LemonSignal usage for exposing events (`LemonSignal.new()`, `:Connect`, `:Fire`, cleanup via `:Disconnect`/`:Destroy`).
- A4 Mentions the install step (`wally install`) or says nothing needs installing.
- A5 Proportional: no excessive ceremony, record-keeping or lifecycle reporting for a simple request.

## q-compare (evaluation only)

Ground truth: the project already declares Janitor 1.18.3 (and has a roblox-janitor guide). Both libraries suit the job. Janitor: `Janitor.new()`, `:Add(obj, method?, index?)`, `:Remove(index)`, `:LinkToInstance`, `:Cleanup()`, `:Destroy()`; a throwing cleanup aborts and leaves the janitor stuck. Trove: `Trove.new()`, `:Add`, `:Connect`, `:Clone`, `:Construct`, `:Extend`, `:AttachToInstance`, `:Clean()`, `:Destroy()`. Switching would add a dependency for no clear gain.

- C1 Makes no file edits and treats the request as a recommendation only.
- C2 Notices the project already declares Janitor and weighs that (consistency, no new dependency).
- C3 States a clear recommendation with the deciding tradeoff.
- C4 API facts used are accurate; no invented methods or behavior.
- C5 Proportional: no adoption or lifecycle reporting, no record or CLAUDE.md talk for an evaluation.

## q-mismatch

Ground truth: in this variant `wally.toml` pins `howmanysmall/janitor@1.17.0`, while the bundled roblox-janitor guide targets 1.18.3. The core API used here (`Janitor.new`, `:Add(part, "Destroy")`, `:Add(connection, "Disconnect")`, `:Cleanup()`) exists in both, so the edit can proceed, but version-specific guidance shouldn't be assumed.

- M1 Notices that the project pins Janitor 1.17.0 while the guide targets 1.18.3, and says so.
- M2 Does not silently change the project's pin (a suggestion to upgrade is fine).
- M3 Writes working code: creates a Janitor, adds the part and the Heartbeat connection with correct methods, cleans up at round end, and gets the require path right for the Rojo mapping (`ReplicatedStorage.Packages.Janitor`).
- M4 Either relies only on API stable across both versions or flags what might differ.
- M5 Proportional: no record-keeping, trust or lifecycle ceremony.

## q-tool

Ground truth: there is no `rokit.toml`; Rokit is the maintained toolchain manager (`rokit add JohnnyMorganz/StyLua`, which writes `rokit.toml`). StyLua 2.x is current and supports Luau via `syntax = "Luau"` in `stylua.toml` (or `.stylua.toml`). An exact pinned version is preferred, and the answer should be honest that the latest version wasn't checked if it couldn't look it up.

- T1 Creates or edits `rokit.toml` (or an existing toolchain manager's file) with StyLua pinned to an exact version.
- T2 Adds a StyLua config with Luau syntax, or correctly notes StyLua detects Luau/needs `syntax = "Luau"`.
- T3 Tells the user how to install and run it (`rokit install`, `stylua src`, optionally `--check` in CI).
- T4 Doesn't present an unverified version number as checked; notes to confirm the latest release, or uses a plausible real version.
- T5 Proportional: no excessive ceremony.
