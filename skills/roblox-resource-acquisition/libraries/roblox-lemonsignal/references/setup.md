# LemonSignal setup

The reviewed project installed LemonSignal from the Wally index through pesde (reviewed 0.7.4):

```toml
[dependencies]
LemonSignal = { wally = "data-oriented-house/lemonsignal", version = "=2.0.0" }

[wally_indices]
default = "https://github.com/UpliftGames/wally-index"
```

A plain Wally project declares `LemonSignal = "data-oriented-house/lemonsignal@2.0.0"` in `wally.toml` and relies on `wally.lock`.

- First install, when adding or changing the dependency: `pesde install`. Restoring an existing lock: `pesde install --locked`.
- The package is a single file, `src/LemonSignal.lua`, with no dependencies. The tag's `wally.toml` says `version = "2.0"`, but the Wally index publishes it as `2.0.0`.
- Check the sourcemap before writing a require path. Don't edit generated wrappers or vendor source.
- The canonical repository is `Data-Oriented-House/LemonSignal`. Similarly named forks are different packages.
