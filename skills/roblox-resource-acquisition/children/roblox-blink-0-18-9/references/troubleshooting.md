# Troubleshooting

### Wrong setup, stale API or cleanup ownership

Unexpected-token diagnostic -> inspect the schema grammar; # is not a comment marker here. Missing outputs -> inspect schema-relative paths and run the exact local alias. Wrong generated side -> require Server only on server and Client only on client when runtime activation is authorized. Duplicate scope -> unique RemoteScope and avoid cloned/re-required transport modules. Client waits forever -> its server transport was not activated. Handler rate checks leave parser exposed -> receiver validation must precede decode, a second listener cannot veto the generated listener.

## Security boundary

[Upstream issue #45](https://github.com/1Axen/blink/issues/45) documents oversized-buffer server DoS; the reviewed 0.18.9 generator still loops over incoming bytes before any application handler. Do not represent schema bounds, handler throttling or a parallel RemoteEvent listener as a fix. Before untrusted server activation, require an explicit tested predecode byte/rate budget in the actual receive path and server-authoritative permission/business validation. Do not silently patch generated/vendor source or advance to a prerelease to claim mitigation. Compiler-only empty adoption leaves generated network modules unrequired. No secrets in schemas/client output; arbitrary payload Instance references require server validation.

## Alternatives

- Native RemoteEvent/UnreliableRemoteEvent, Zap and ByteNet are informational alternatives. Small projects may use native remotes with explicit contracts. The user selected Blink; preserve the adopted pin and return runtime-security blockers to the owner rather than substitute.
