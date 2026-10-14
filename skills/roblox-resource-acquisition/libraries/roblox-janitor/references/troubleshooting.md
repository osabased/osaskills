# Janitor troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `Object ... doesn't have method Destroy, are you sure you want to add it?` | A custom object (for example a signal library's connection) went in with the default method. Pass the right one: `janitor:Add(conn, "Disconnect")`. Otherwise cleanup silently skips it. |
| `Object is a function and as such expected true? ...` | A function or thread was added with a string method. Use `true`, or omit the method. |
| `Cleanup()` suddenly does nothing | An earlier cleanup threw, leaving the Janitor stuck as cleaning. Find and fix the throwing entry, then replace the Janitor with a new one. |
| `attempt to call a nil value` on a Janitor | It was used after `Destroy()`, which removes the metatable. Create a new Janitor, or guard with a disposed flag. |
| A consumer errors because its producer was already gone, or the reverse | Janitor's order is unspecified. Split producers and consumers into separate Janitors and clean them in order. |
| Objects survive when the model is removed | `LinkToInstance` watches `Destroying` only. Destroy the Instance, or clean up explicitly when it is reparented. |
| Connections made from a LocalScript disappear when that script is destroyed | Engine connections die with their script. Keep long-lived owners in a ModuleScript that outlives it. |
| The require fails or the wrapper is missing | Restore the lock (`pesde install --locked`) and check the mapped `janitor` ModuleScript ([setup](setup.md)). |
