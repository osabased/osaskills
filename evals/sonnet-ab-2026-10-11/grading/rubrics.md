# Rubrics (ground truth verified against pinned upstream source)

## q-vide (Vide 0.4.1 @5ed4c01)
Ground truth: `source(v)` returns a Source; `s()` reads, `s(x)` writes. `create "Class" { ... }`: string keys = properties; a function on a normal property is reactive; a function on an event property (e.g. Activated) is connected as a listener; numeric keys are children. `derive`, `effect`, `show(cond, fn)`, `indexes(tbl, fn(valueSrc, key))`, `values(tbl, fn(value, keySrc))`. `mount(fn, target)` returns a disposer; calling it twice errors. The disposer destroys the scope but does NOT destroy/unparent the returned Instance unless it was registered with `cleanup(instance)` (or destroyed manually). `cleanup(x)` registers teardown. There is no `Vide.destroy`, `Vide.unmount`, `Vide.New`, `Vide.Children`, `Vide.state`, `Vide.OnEvent`.
Criteria:
- V1 Reads/writes sources correctly (call to read, call with value to write).
- V2 Event handler as a function on the event property (e.g. `Activated = function() ... end`) — no Fusion/React-style `OnEvent`/`[Vide.Event]` inventions.
- V3 List rendered reactively with `indexes`/`values` (or a correct derive-based approach) from the source table.
- V4 Uses `mount(..., PlayerGui)` and keeps/calls the returned disposer for teardown.
- V5 Ensures the ScreenGui/Instance is actually destroyed on teardown (registers `cleanup(gui)` or destroys it explicitly) OR explicitly notes the disposer doesn't destroy the instance.
- V6 No invented/nonexistent Vide APIs.

## q-blink (Blink 0.18.9)
Ground truth syntax: `option ServerOutput = "path"`, `option ClientOutput = "path"` (paths relative to schema). `event Name { From: Server|Client, Type: Reliable|Unreliable, Call: SingleSync|ManySync|SingleAsync|ManyAsync|Polling, Data: T }`; multiple values `Data: (A, B)` or a struct. `function Name { Yield: Coroutine|Future|Promise, Data: T, Return: T }`. Types include `u16`, `vector`, `string`, arrays `T[..6]`/`T[1..6]` / `T[0..6]`, optional `T?`, `struct Name { Field: T }`. Comments are `--`. Generated server API: `Net.Ev.Fire(player, ...)`, `FireAll(...)`, `FireList`, `FireExcept`, `Net.Ev.On(function(player, ...) end)`; functions: server `Net.Fn.On(function(player, ...) return v end)`, client `Net.Fn.Invoke(...)`. Client: `Net.Ev.Fire(...)`, `Net.Ev.On(fn)`. Casing default Pascal. Unreliable payload limit 1000 bytes.
Criteria:
- B1 Event declarations use the correct field syntax (From/Type/Call/Data) and valid Call values.
- B2 Function declaration uses Yield/Data/Return correctly (Data may be omitted) and the return is a bounded array of strings.
- B3 Output options declared with valid `option` syntax.
- B4 Server usage uses the correct generated API (Fire/FireAll/On, function On returning a value).
- B5 Client usage uses the correct generated API (Fire / On / Invoke).
- B6 No invented syntax (e.g. `#` comments, `remote`, `packet`, `Payload:`, `Direction:`, JSON-like schemas, nonexistent methods like `:Connect` on generated events).
- B7 Mentions server-side validation of client data or the unreliable-size/DoS concern (any security note).

## q-janitor (Janitor 1.18.3, LemonSignal 2.0.0)
Ground truth: `Janitor.new()`; `j:Add(obj, method?, index?)` returns obj; default method: functions/threads -> called (`true`), RBXScriptConnection -> "Disconnect", otherwise "Destroy". A LemonSignal connection is a table with `Disconnect` (no `Destroy`), so it must be added with `"Disconnect"` — added with the default it warns once and is then silently skipped at cleanup. `j:LinkToInstance(inst, allowMultiple?)` cleans when the Instance is destroyed (Destroying). `j:Cleanup()`, `j:Destroy()`. If a cleanup entry throws, the cleanup aborts (remaining entries not cleaned), and the janitor is left in a state where every later `Cleanup()`/`Destroy()` silently does nothing. Recommend pcall-wrapping risky callbacks. Cleanup order is not guaranteed.
Criteria:
- J1 Adds the LemonSignal connection with "Disconnect" as the method.
- J2 Part added with default/Destroy; Heartbeat connection added (default or "Disconnect"); callback added as a function.
- J3 Uses LinkToInstance (or Destroying/AncestryChanged correctly) to tie to the Instance lifetime.
- J4 Correctly states a throwing cleanup aborts the remaining entries.
- J5 States that later Cleanup()/Destroy() calls silently do nothing (janitor stuck) — or equivalently that the janitor cannot recover.
- J6 Recommends pcall or nonthrowing callbacks.
- J7 No invented APIs or wrong claims (e.g. "Janitor catches errors and continues", "cleanup is LIFO guaranteed").

## q-glob (Rojo 7.7 globIgnorePaths)
Ground truth: `globIgnorePaths` is a top-level array in the project file. Patterns are matched relative to the project file's directory (so `src/client/...`, not `client/...`). `**/Preview` excludes an init-backed Preview directory and all its children. `**/Preview/**` ALONE excludes the children but leaves the directory's own init ModuleScript. `**/*.story.luau` excludes stories. Verify with `rojo build`/`rojo sourcemap`.
Criteria:
- G1 Uses top-level `globIgnorePaths`.
- G2 Includes a story pattern like `**/*.story.luau`.
- G3 Preview pattern that actually excludes the init-backed folder (`**/Preview` or `src/client/**/Preview`, possibly alongside `/**`).
- G4 Does not claim `**/Preview/**` alone is sufficient; ideally explains that it leaves the init module.
- G5 Correct about paths being relative to the project file directory (or uses patterns consistent with that).
- G6 Suggests verifying with a build or sourcemap.

## q-entry (client entrypoint; scaffold: default.project.json maps src/client -> ReplicatedStorage.Client; src/client/init.client.luau exists)
Ground truth: Roblox currently recommends a `Script` with `RunContext = Client` placed in ReplicatedStorage (or similar) for client code; LocalScripts only run in specific containers (StarterPlayerScripts, StarterCharacterScripts, StarterGui, PlayerGui, Backpack, character) — NOT in ReplicatedStorage. A RunContext=Client Script in StarterPlayerScripts/StarterCharacterScripts runs twice. In Rojo 7, `init.client.luau` becomes a LocalScript unless `emitLegacyScripts: false` (then a Script with RunContext Client). So in this scaffold, `src/client/init.client.luau` mapped into ReplicatedStorage.Client becomes a LocalScript that will NOT run.
Criteria:
- E1 Inspects the actual project mapping (default.project.json) and reports where src/client lands.
- E2 Notices the existing client entry would be a LocalScript in ReplicatedStorage and won't run (or flags the emitLegacyScripts issue).
- E3 Recommends a correct option: RunContext=Client Script in ReplicatedStorage (preferred) and/or LocalScript in StarterPlayerScripts, with the needed Rojo mapping/setting.
- E4 No wrong claims (e.g. "LocalScripts run in ReplicatedStorage", "Client RunContext script in StarterPlayerScripts is fine" without the run-twice caveat).
- E5 Proportional: answers the question without excessive process.

## q-review (checkout flow)
Ground truth issues: (1) retries after a successful charge can double-charge unless an idempotency key is passed to the payment provider and tied to the request; (2) charge-then-insert: if the insert fails (unique race) after the charge, money is taken with no order — needs compensation (refund/void), outbox/reservation-first, or reconciliation; (3) a timeout doesn't mean failure — the server may have completed; client retry must be safe; (4) the unique-constraint race should be handled as an idempotent "already exists → return existing order" rather than 5xx (which triggers retries); (5) closure/verification evidence (tests for retry after commit, etc.).
Criteria:
- S1 Identifies double-charge on retry and proposes idempotency key end to end (client→server→provider).
- S2 Identifies charged-but-no-order and proposes a concrete remedy (order-first/pending, compensation, outbox, reconciliation).
- S3 Treats the unique-constraint failure correctly (return existing order / map to non-retryable) and notes 5xx triggers retries.
- S4 Gives a clear verdict (does it hold up: no).
- S5 Gives concrete verification/closure checks (scenarios to test).
- S6 Concise and well organized (not padded).

## q-addsignal (wally.toml already declares LemonSignal 2.0.0; pesde.toml exists too)
Ground truth: The project already declares `data-oriented-house/lemonsignal@2.0.0` in wally.toml. The best answer notices this and uses it (no new dependency), or clearly justifies something else; shows how modules expose events with it; does not add a duplicate signal library or hand-roll one without reason. Cannot run commands, so should say how to install (`wally install`) if anything changes.
Criteria:
- A1 Notices LemonSignal is already a declared dependency.
- A2 Does not add a second signal library or a hand-rolled Signal without justification.
- A3 Shows correct LemonSignal usage for exposing events (`LemonSignal.new()`, `:Connect`, `:Fire`, cleanup via `:Disconnect`/`:Destroy`).
- A4 Mentions install/sync step or that packages must be installed (Packages folder) — or explains nothing needs installing beyond `wally install`.
- A5 Proportional (no excessive ceremony or lifecycle reporting for a simple request).
