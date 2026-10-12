# q-compare

Prompt: Janitor or Trove for cleaning up per-round objects (parts, tweens, connections) in our server round system? Just give me a recommendation, don't change anything.

---

## Answer A

### Final message

**Use Janitor.** I didn't change anything.

- **It's already in your project.** `wally.toml:8` pins `howmanysmall/janitor@1.18.3`, and a bundled `roblox-janitor` skill matches that version. Adding Trove would put a second cleanup library in the project for no gain, and the project has no Trove code today.
- **It covers what you listed.** Janitor cleans up parts and other Instances, tweens (via `Add(tween, "Cancel")`) and connections. It also handles threads and plain callbacks.
- **It fits a per-round lifecycle.** Create one Janitor per round and add each object as you spawn it. When the round ends, call `janitor:Cleanup()`, which empties it and leaves it reusable for the next round. If you want a fresh one each round, call `Destroy()` instead.
- **Trove isn't better enough to switch.** Trove does the same job, and `trove:Extend()` for sub-scopes is a nice touch. You can get the same nesting by adding a child Janitor to the round Janitor. The difference doesn't justify a second dependency.

One caveat: I didn't run anything or test it against your round system. I only checked the manifest and the bundled catalog. If the round system has its own cleanup convention that I haven't seen, that would take precedence.

---

## Answer B

### Final message

**Use Janitor.** Your `wally.toml` already pins `howmanysmall/janitor@1.18.3`, and it covers per-round cleanup of parts, tweens and connections.

**Why Janitor**
- **It's already a declared dependency.** Trove isn't in either manifest, so adding it would be a second cleanup library for the same job.
- **It fits the lifecycle.** Make one Janitor per round. Add each part, tween and connection as it's created. Call `janitor:Cleanup()` when the round ends. The same instance can be reused for the next round, or you can `Destroy()` it. It cleans Instances, connections, threads and functions, and `LinkToInstance` ties a Janitor to an Instance's lifetime.
- **A child skill is bundled.** `roblox-janitor` is pinned to the same 1.18.3.

**Trove's tradeoff**
- Trove covers the same ground (Instances, connections, tweens, threads), so it wouldn't fail on fit.
- It has no advantage that matters here, and it would add another API to learn and another pin to maintain.

**What would change this:** a project rule or a teammate preference for Trove, or a feature you need that Janitor 1.18.3 lacks. Neither is visible in the repo.

**What I checked:** I read the two manifests and the Roblox resource-acquisition skill's selection guidance (`choosing.md`). I did not install or run either library, and I didn't look at the DevForum or either repository's issues. The Trove comparison comes from general knowledge, not a check against a pinned version. This is an evaluation only, and nothing was changed.

---

## Answer C

### Final message

**Recommendation: use Janitor.** This is an evaluation only, and I haven't changed anything.

**Decisive evidence**
- Your `wally.toml` already declares `Janitor = "howmanysmall/janitor@1.18.3"`. Trove isn't declared anywhere in the project. Adding it would mean a second cleanup library with the same job.
- Janitor covers all three of your object types, based on the bundled `roblox-janitor` guidance (I read it, I didn't run it):
  - **Parts:** `janitor:Add(part)` destroys them on cleanup.
  - **Tweens:** `janitor:Add(tween, "Cancel", "Tween")` cancels the tween. Using an index also replaces the previous tween under that name.
  - **Connections:** `janitor:Add(conn, "Disconnect")` disconnects them. The same call with `"Destroy"` handles a signal your round created.
- It also fits a round system with these features:
  - `LinkToInstance` cleans up when a round model is destroyed.
  - A throwing `Cleanup` call is a bug, not a retryable state.
  - Threads are cancelled, and Promises are cancelled if still pending.

**Pattern for rounds:** create one `Janitor.new()` when a round starts and add everything to it as you create it. Call `janitor:Destroy()` when the round ends. If the round also has setup-time work that can fail, use the pcall-and-rollback pattern from the guidance. If teardown order matters, keep one Janitor for producers (connections, tasks) and one for consumers, and clean the producers first.

**Trove:** it does the same job and is a reasonable library. It loses here only because it adds a dependency without adding anything you need. Trove has `Extend` for child troves, but that is a convenience, and I haven't checked its current version or maintenance.

**What would change my mind**
- A project rule or team preference for Trove.
- A need Janitor can't meet, such as the Janitor 1.18.3 `Cleanup` behavior biting you. If a cleanup entry throws, the Janitor stops cleaning and later calls return immediately. Make sure nothing you add can error during teardown.

I didn't research Trove's current state or read DevForum threads, because the existing dependency settled the choice.

---

## Answer D

### Final message

**Use Janitor.** I didn't compare Janitor and Trove on their merits, because the question is already settled by your project. `wally.toml` declares `Janitor = "howmanysmall/janitor@1.18.3"`, and I found no Trove or Maid dependency. Adding Trove would give you two cleanup libraries doing the same job, and nothing in per-round cleanup needs a second one. The pinned `roblox-janitor` skill matches that version, so its guidance applies directly.

For a round system, one Janitor per round covers all three kinds of object:

- **Parts and other instances:** `janitor:Add(part, "Destroy")`. You can also use `janitor:Add(part)`, which destroys it by default.
- **Tweens:** `janitor:Add(tween, "Cancel")`. This stops the tween when the round ends. Destroying it alone doesn't cancel playback.
- **Connections:** `janitor:Add(conn, "Disconnect")`.
- **Ending the round:** call `janitor:Cleanup()` and drop the reference. That leaves any janitor you reuse in a clean state. Call `Destroy()` only if the janitor itself is done.
- **Instances that may be destroyed early:** `LinkToInstance` ties a janitor to an instance's lifetime, for example a round folder or a player's character.

I'd keep each round's janitor on the round object, so ending the round and cleaning up are a single call. That also makes early exits and aborted rounds go through the same path.

I haven't run any of this in your project, and I'm relying on the bundled pin and its skill. Please test one full round followed by an aborted round. Check that tweens stop and that no connections or parts are left behind.

I changed nothing.
