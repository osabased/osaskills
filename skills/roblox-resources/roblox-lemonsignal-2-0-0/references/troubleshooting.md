# Troubleshooting

### Wrong setup, stale API or cleanup ownership

Unexpected callback argument -> check Fire payloads and remove old Connect bound-argument examples. Callback finishes after disposal -> owner invalidation/cancellation, not Destroy alone. Wait never resumes after teardown -> cancel the owned waiter. Engine events continue -> destroy the owned wrap, not just one subscriber. Wrong identity -> preserve Data-Oriented-House/LemonSignal; do not substitute a similarly named fork.

## Security boundary

LemonSignal has no built-in remote, HTTP, persistence or arbitrary asset loading. A local signal cannot authenticate client claims or cross runtime boundaries. Keep server validation at the real network boundary. Preserve exact identity and lock; callbacks execute trusted local application code.

## Alternatives

- Native RBXScriptSignal for engine events, BindableEvent or Sleitnick Signal for local dispatch are informational alternatives. The user selected LemonSignal; preserve the owner’s package identity and pin.
