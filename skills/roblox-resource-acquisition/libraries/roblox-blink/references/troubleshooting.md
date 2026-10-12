# Blink troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `Unexpected token` near `#` | `#` isn't a comment. Use `--`. |
| An unexpected-token error elsewhere | Check the field names (`From`, `Type`, `Call`, `Data`; `Yield`, `Data`, `Return`), the commas between fields, and that `?` comes after the whole type. Use the [schema](schema.md) reference. |
| Outputs missing or in the wrong place | Output paths are relative to the schema file, not the working directory. Run the locked alias: `pesde run blink -- path/to/schema`. |
| Generated methods named `fireAll`/`fire_all` | `option Casing` is `Camel` or `Snake`. Match it, or change it and regenerate. |
| The client hangs on require | The client waits for remotes that the server creates when it requires the Server output. Make sure the server requires it (and only once). |
| Remotes collide with a package's or another Blink setup | Set a unique `RemoteScope`, and don't clone or re-require the generated modules. |
| A deserialization error drops a packet | A non-optional `Instance` arrived `nil` (streaming, or a client-only instance). Mark the field `?`. |
| Sync handler errors or odd behavior | `SingleSync`/`ManySync` handlers must not yield or error. Switch to `Async`, or remove the yield. |
| Version-specific syntax doesn't parse | It may come from the 1.0.0 pre-release docs. Use the 0.18.9 docs (the tag's `docs/` folder). |

## Security boundary

[Issue #45](https://github.com/1Axen/blink/issues/45) reports a server crash from oversized buffers. The maintainer considers it outside the security scope of 0.18.x. The generated 0.18.9 server reads incoming bytes before any application handler runs, so neither schema bounds, handler throttling, nor a second `OnServerEvent` listener can veto parsing. Before untrusted client-to-server traffic goes live, put a tested pre-decode byte and rate budget in the actual receive path. Don't claim mitigation by silently patching generated code or switching to a pre-release; report the risk to the project owner. Keep secrets out of schemas and client outputs.
