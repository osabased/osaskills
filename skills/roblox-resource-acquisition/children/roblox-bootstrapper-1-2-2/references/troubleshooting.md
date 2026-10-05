# Troubleshooting

### Discovery or phase failure

- No module starts: check mapping/root, suffix pattern, table return and exact method case/prefix.
- Start-only module vanishes: the caller replaced the original array with run's filtered init result.
- Init failure still lets Start run: Bootstrapper continues its current phase; check errors and abort the next phase in your caller.
- Wrong argument/self: dot is static; colon/unprefixed injects self.
- Work after teardown: retain the binding disposer; a binding cleanup does not cancel independently spawned module work.
- Wrapper/type missing: verify official sourcemap hook and restore locked packages; preserve upstream source.

## Security boundary

There is no special network/credential boundary in discovery/dispatch. Requiring discovered
modules executes their code: constrain roots/predicates to authored trusted modules and preserve
server authority. Avoid arbitrary asset/string paths or client-supplied module lists; use actual
ModuleScript instances/tables in Roblox. Keep the immutable Git pin and locked restoration.

## Alternatives

Direct explicit requires are sufficient for small fixed startup sequences. Other loaders are
informational alternatives, not authority to replace this project's user-selected Bootstrapper pin.
