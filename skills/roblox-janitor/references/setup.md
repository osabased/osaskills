# Janitor setup

The reviewed project installed Janitor from the Wally index through pesde (reviewed 0.7.4):

```toml
[dependencies]
Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }

[wally_indices]
default = "https://github.com/UpliftGames/wally-index"
```

A plain Wally project declares `Janitor = "howmanysmall/janitor@1.18.3"` in `wally.toml` and relies on `wally.lock`.

- First install, when adding or changing the dependency: `pesde install`. Restoring an existing lock: `pesde install --locked`.
- The package's Rojo project is named `janitor` (lowercase). The generated wrapper requires it correctly; check the sourcemap before writing a require path.
- Requiring Janitor also loads its `FastDefer` and `Promise` modules. `Promise.luau` looks for a sibling `Promise` package; the reviewed lock resolved `howmanysmall/typed-promise` 4.0.6 and `evaera/promise` 4.0.0. Their identities are recorded as companions in [resource.yaml](../resource.yaml).
- MIT licensed. Don't edit generated wrappers or vendor source.
