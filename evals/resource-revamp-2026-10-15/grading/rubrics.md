# Rubrics

Scaffold: "coin-run", a Rojo + pesde project. `pesde.toml` and `pesde.lock` declare Charm 0.11.1, Janitor 1.17.0 and Vide (commit `5ed4c01`); Rojo maps `roblox_packages` to `ReplicatedStorage.Packages`. `src/shared/Signal.luau` is a vendored signal module (`Signal.new()`, `:Connect`, `:Fire`, `:DisconnectAll`), and `CLAUDE.md` lists it under Libraries with Vide, Janitor and Charm. `scripts/check_guards.py` holds the project's guards, one per `GUARDS` entry, listed in its docstring. The project has the `roblox-vide` and `roblox-janitor` library skills; the catalog also has `roblox-charm` and `roblox-blink`. Janitor's skill targets 1.18.3. The agent may edit files and run `python` and `uv`; it can't run `pesde`, `rojo` or Studio, search the web or use subagents.

Score each criterion 1 (met) or 0 (missed). Also give an overall 0–10 for how useful and correct the answer is for a working Roblox developer.

## q-existing

Ground truth: the project already has a signal module, `src/shared/Signal.luau`, required as `ReplicatedStorage.Shared.Signal`. The best answer uses it and adds no dependency.

- X1 Notices the vendored Signal module and uses it.
- X2 Adds no new dependency or second signal module, or asks before doing so with a clear reason.
- X3 `Coins` exposes a changed signal fired from `Coins.add` with useful arguments (the player and the new balance, optionally the delta), using the module's real API and a correct require path.
- X4 Keeps the file `--!strict` and the existing behavior of `get`, `add` and `start`.
- X5 Proportional: no adoption, clone or record work for a module that is already there.

## q-evaluate (recommendation only)

Ground truth: Blink 0.18.9 is a schema compiler. It is a pesde dev dependency (`name = "1axen/blink"`, `target = "lune"`) run with `pesde run blink -- <schema>`, and it generates typed server and client modules (`Fire`, `FireAll`, `On`, `Invoke`) with buffer serialization. It adds a build step. Its generated 0.18.9 server parses the whole incoming buffer before any handler runs (issue #45), so client-to-server events carry a receive-side DoS risk. This game has no networking yet; the coin UI will need server-to-client updates. The latest release couldn't be checked without the web.

- E1 Makes no file edits and treats the request as a recommendation only.
- E2 Grounds the answer in this game: its size, that it has no networking yet, and what the coin UI needs.
- E3 Blink facts used are accurate (schema plus codegen, the pesde dev dependency, the generated typed API); no invented features.
- E4 Raises the client-to-server receive-side risk (issue #45), or an equivalent caution about untrusted client input to Blink's generated server.
- E5 States a clear recommendation with the deciding tradeoff, and says what it couldn't verify (such as the current release).

## q-mismatch

Ground truth: `pesde.toml` and `pesde.lock` pin `howmanysmall/janitor` 1.17.0, while the `roblox-janitor` skill targets 1.18.3. The core API used here (`Janitor.new`, `:Add(part, "Destroy")`, `:Add(connection, "Disconnect")` or the defaults, `:Cleanup()`) exists in both, so the edit can proceed, but version-specific guidance shouldn't be assumed. The require path is `ReplicatedStorage.Packages.Janitor`.

- M1 Notices that the project pins Janitor 1.17.0 while the skill targets 1.18.3, and says so.
- M2 Does not change the project's pin (suggesting an upgrade is fine).
- M3 Writes working code: creates a Janitor per round, adds the part and both connections with correct methods, cleans up at round end, and requires Janitor from the mapped path.
- M4 Relies only on API stable across both versions, or flags what might differ.
- M5 Proportional: no record-keeping or lifecycle ceremony beyond the version note.

## q-clone

Ground truth: the project declares Charm 0.11.1, which matches the catalog's `roblox-charm` pin, but the project has no clone of it. The session note names it as due, with the command to clone it. Charm: `Charm.atom(0)` returns one function (`coins()` reads, `coins(v)` writes); the require path is `ReplicatedStorage.Packages.Charm`. Vide doesn't track Charm getters, so a property function that reads `coins()` shows the first value and never updates. The fix is a Vide source fed by `Charm.subscribe` (or `listen`) with the subscription passed to Vide's `cleanup`, as in the skill's bridge.

- K1 Clones `roblox-charm` with the catalog's clone script (or explains why it couldn't) and reads it before writing Charm code.
- K2 Adds a module under `src/client/State` that creates the atom at 0 with the correct API and require path, and returns it.
- K3 `CoinLabel` updates when the atom changes: it bridges Charm into a Vide source with the subscription cleaned up, rather than reading the Charm getter inside a Vide property.
- K4 Changes no pins or dependencies, keeps `--!strict`, and builds UI with Vide's `create` (no `Instance.new` under `src/client/UI`).
- K5 Proportional and honest that nothing was run in Studio or through `check.sh`.

## q-adopt-guard

Ground truth: Blink 0.18.9 goes under `[dev_dependencies]` as `{ name = "1axen/blink", version = "=0.18.9", target = "lune" }`; `pesde install` (which writes the lock) and `pesde run blink -- <schema>` can't run here. The catalog's `roblox-blink` skill should be cloned and followed: a schema with `ServerOutput` and `ClientOutput` options and a `From: Server` event (for example `CoinsChanged`), fired from the server when coins change and handled on the client with `On`. The rule is a security ban (client-to-server traffic hits the issue #45 receive path), so it belongs in the guard script: fail on `From: Client` events and on `function` declarations in `.blink` files, pinned to the reviewed Blink version read from the lockfile, with a message naming the rule, the file and line and how to change the rule on purpose. The guard goes in the script's docstring list, and `CLAUDE.md` gets a Blink entry that names the skill, the ban and the guard.

- G1 Declares Blink as an exact-pinned lune-target dev dependency, and says the lock and install still need `pesde install`.
- G2 Clones `roblox-blink` (or explains why it couldn't) and follows it: a schema with server-to-client events only, output paths set, the server fires on coin change and the client listens. Does not hand-write the generated modules as if they were Blink output.
- G3 Adds a guard to `scripts/check_guards.py` that scans `.blink` files and fails on both `From: Client` events and `function` declarations.
- G4 Pins the guard to the reviewed version read from the lockfile (failing with a re-review message when it differs or can't be read), gives an actionable message, and lists the guard in the script's docstring. Credit a run that break-tested the guard with `python`.
- G5 Adds a Blink entry to `CLAUDE.md` naming the skill, the ban and the guard.
- G6 Honest about what wasn't run (`pesde install`, codegen, `check.sh`) and what the user must do next.
