# Blink setup

The reviewed project installed the Blink CLI as a pesde dev dependency (pesde reviewed 0.7.4, Lune reviewed 0.10.5):

```toml
[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }

[indices]
default = "https://github.com/pesde-pkg/index"
```

- First install, when adding or changing the dependency: `pesde install`. Restoring an existing lock: `pesde install --locked`.
- Run the locked CLI with `pesde run blink -- <schema-path-without-extension>`. Check the version with `pesde run blink -- --version`.
- The pesde package runs `release/blink_pesde.luau` under Lune. No Studio plugin is needed. Upstream also offers Rokit (`rokit add 1Axen/blink`) and a Studio editor plugin; use whatever the project already uses.
- MIT licensed. Don't edit generated outputs or vendor files.
