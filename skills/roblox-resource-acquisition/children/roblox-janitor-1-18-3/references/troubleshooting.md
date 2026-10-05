# Troubleshooting

### Wrong setup, stale API or cleanup ownership

Wrong cleanup method -> use explicit Disconnect, Destroy or true. Consumer dies before producer -> split phases. Cleanup stops on a thrown callback -> isolate the callback and keep later top-level phases protected. UI remains after bootstrap removal -> verify module-owned removal handling rather than relying only on caller-owned Destroying connections. Wrapper missing -> locked restoration, mapping and actual ModuleScript class first.

## Security boundary

Janitor has no special network or persistence trust boundary. Cleanup callbacks execute arbitrary application code: register only trusted local callbacks and owned objects. Never accept client-provided cleanup method names or object ownership. Keep privileged rules server-authoritative. Preserve pinned dependencies and ordinary locked restoration.

## Alternatives

- Trove and Maid are informational alternatives. Direct native Disconnect/Destroy is sufficient for a lone resource. The user selected Janitor; preserve the owner’s identity and pin rather than substituting.
