===== R1 =====
**Put it in `src/client/` as a ModuleScript, and have the existing client entrypoint require it. Don't add a second entrypoint.**

`default.project.json` maps `src/client` to `ReplicatedStorage.Client`. The folder already contains `src/client/init.client.luau`. Rojo turns that file into a `Script` named `Client` with `RunContext = Client`, which is the currently recommended client entrypoint for a `ReplicatedStorage` location. It is a placeholder (`print("client")`), and nothing else in the project starts client code.

- **Controller:** create `src/client/InputController.luau` (no `.client` suffix). Rojo will make it a `ModuleScript` at `ReplicatedStorage.Client.InputController`. It should return a table with something like `init`/`start` or `new`/`Destroy`.
- **Startup:** edit `src/client/init.client.luau` to `require` it with `script.InputController` and call its start function. That Script is the single client startup owner. The server side already follows the same pattern with `src/server/init.server.luau`.
- **Not a `LocalScript`, and not a second `.client.luau`:** a `LocalScript` in `ReplicatedStorage` never runs. A second RunContext-Client `Script` would split startup ownership for no benefit.
- **Not in `src/shared`:** the controller is client-only, and `src/shared` is `ReplicatedStorage.Shared`. Only put input action names, types or constants there if the server also needs them. The server should still validate anything the client sends.
- **Dependencies:** `wally.toml` and `pesde.toml` both exist, and `Packages` is mapped under `ReplicatedStorage`. I didn't check which one is actually in use. If you want a loader or scheduler such as Bootstrapper, confirm that first. For one controller, a plain `require` from `init.client.luau` is enough.

I haven't edited anything.


===== R2 =====
I've traced the wiring and I'm about to give the recommendation.

**Recommendation:** put the entrypoint at `src/client/init.client.luau`, the file that already exists. It should be a client `Script` with `RunContext = Client`, not a `LocalScript`. It stays in `ReplicatedStorage` and needs one small mapping change first. I didn't edit anything.

**How the project is wired today**
- `default.project.json` is a Rojo project named `arena`.
- `src/shared` maps to `ReplicatedStorage.Shared`.
- `src/client` maps to `ReplicatedStorage.Client`.
- `Packages` maps to `ReplicatedStorage.Packages`.
- `src/server` maps to `ServerScriptService.Server`.
- All three source folders are stubs:
  - `src/client/init.client.luau` is just `print("client")`.
  - `src/server/init.server.luau` is just `print("server")`.
  - `src/shared/init.luau` is `return {}`.
- There is no `StarterPlayer` mapping and no `Packages` folder on disk yet.

**The catch:** the existing client entrypoint probably never runs.
- Rojo turns `init.client.luau` into a `LocalScript` by default. The project doesn't set `emitLegacyScripts`, and I didn't find a pinned Rojo version, so I'm assuming that default.
- That `LocalScript` lands in `ReplicatedStorage.Client`, and a `LocalScript` in `ReplicatedStorage` never runs.
- The `print("client")` line is likely dead code today. I haven't run it in Studio.

**What I'd do**
- **Class:** keep `src/client` mapped to `ReplicatedStorage.Client`. Roblox's current recommendation is a `Script` with `RunContext = Client` in `ReplicatedStorage`.
- **Mapping:** the new controller has to be a client `Script` rather than a `LocalScript`. Either set `"emitLegacyScripts": false` in `default.project.json`, or add an `init.meta.json` next to the entrypoint with `className: Script` and `RunContext: Client`.
- **Folder layout:** two ways to keep the folder usable:
  - Keep the entrypoint as `init.client.luau` and put the controller modules beside it as `.luau` ModuleScripts.
  - Move the entrypoint to its own file (for example `ClientMain.client.luau`) with the modules in sibling folders.
- **Don't use `StarterPlayerScripts`.** A Client-`RunContext` `Script` placed there runs twice (the original and its clone). A `LocalScript` there is the other valid choice, but it would need a new `StarterPlayer` mapping the project doesn't have.
- **Shared code:** anything shared with the server, such as input action names or remote definitions, goes in `src/shared`. That is a dependency, not an entrypoint. Keep secrets out of it, because clients can see everything in `ReplicatedStorage`.
- **Server side:** the server must validate any input the controller sends. `src/server` already has an entrypoint for that.
- **Check:** the remaining Rojo and RunContext questions can only be settled by a Studio play test, which I haven't done. After the change, confirm in Studio that the entrypoint prints on the client only, once per player.


===== R3 =====
**Short answer:** the entrypoint should be `src/client/init.client.luau`, a LocalScript. It already exists, but the project mapping means it won't run as wired today.

**How it's wired**

- `default.project.json` is a Rojo project named "arena". It maps `src/shared` to `ReplicatedStorage.Shared`, `src/client` to `ReplicatedStorage.Client`, and `src/server` to `ServerScriptService.Server`.
- `src/client/init.client.luau` is just `print("client")`. Rojo turns the `.client.luau` suffix into a LocalScript.
- `src/server/init.server.luau` is the server equivalent, a Script.
- `src/shared/init.luau` is `return {}`, a ModuleScript.
- `wally.toml` and `pesde.toml` are both present, and `Packages` is mapped under ReplicatedStorage.

**The problem**

A LocalScript placed in `ReplicatedStorage` doesn't execute. Client scripts only run under containers like `StarterPlayerScripts`, `StarterGui`, `StarterCharacterScripts` or the player's `Backpack`. So the existing `print("client")` never fires.

**Recommendation**

1. Remap the client folder in `default.project.json` so it runs. The usual shape is:
   ```json
   "StarterPlayer": {
     "StarterPlayerScripts": { "Client": { "$path": "src/client" } }
   }
   ```
   You can keep `Shared` and `Packages` in ReplicatedStorage so both sides can require them.
2. Keep `init.client.luau` as the one bootstrap LocalScript. It should only require and start things.
3. Put the controller itself in a ModuleScript, for example `src/client/InputController.luau`, and have the bootstrap call something like `InputController.start()`. Don't make the controller its own `.client.luau`. A single entrypoint gives you deterministic start order, and ModuleScripts are easier to test.
4. Put anything the server also needs, like action names or input-to-intent types, in `src/shared`. The controller logic itself stays client-only.

I didn't edit any files. If you want, I can make the mapping change and add the `InputController` stub.


===== R4 =====
**Put the entrypoint at `src/client/init.client.luau` and make it a LocalScript.** That file already exists, but it won't run as the project is wired today.

**How the project is wired**
- `default.project.json` is a Rojo project named `arena`. It has three source folders: `src/shared`, `src/server` and `src/client`.
- `src/server/init.server.luau` becomes a `Script` in `ServerScriptService.Server`. It only prints "server".
- `src/shared/init.luau` becomes a `ModuleScript` in `ReplicatedStorage.Shared`. It returns `{}`.
- `src/client/init.client.luau` becomes a `LocalScript` in `ReplicatedStorage.Client`. It only prints "client".
- `wally.toml` and `pesde.toml` both exist, and `Packages` is mapped under `ReplicatedStorage`.

**The problem**
A LocalScript only runs in client-side containers such as `StarterPlayer.StarterPlayerScripts`, `StarterGui` or `StarterPack`. It doesn't run when it sits in `ReplicatedStorage`, so the current client entrypoint never executes. The input controller would hit the same problem unless the mapping changes.

**Recommendation**
1. Change the `src/client` mapping in `default.project.json` to put it under `StarterPlayer`. For example, add `"StarterPlayer": { "StarterPlayerScripts": { "Client": { "$path": "src/client" } } }`, and remove the `Client` entry from `ReplicatedStorage`.
2. Keep `init.client.luau` as the single bootstrap LocalScript. It should only `require` modules and start them.
3. Write the input controller as a ModuleScript, for example `src/client/InputController.luau`, that returns a table with `Start()` or `Init()`. The entrypoint requires it and calls it.
4. Put any input action names or types that the server also needs in `src/shared`.

Make the bootstrap a LocalScript, not a ModuleScript or a `Script` with `RunContext = Client`. It matches how the project is already set up, and it needs no extra configuration. Only the mapping needs to change.
