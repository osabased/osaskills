# Bootstrapper setup

The reviewed project installed Bootstrapper with pesde (reviewed 0.7.4) as a Git dependency, because the package is Wally-format:

```toml
[dependencies]
Bootstrapper = { repo = "https://github.com/LDGerrits/Bootstrapper", rev = "ff6700d32875dde5ef9e3625a159436ebd4dc3e9" }
```

A plain Wally project declares `Bootstrapper = "ldgerrits/bootstrapper@1.2.2"` in `wally.toml` and relies on `wally.lock`.

- First install, when adding or changing the dependency: `pesde install`. Restoring an existing lock: `pesde install --locked`.
- Keep a `[scripts].sourcemap_generator` hook so the exported types resolve.
- **Wrapper casing, observed with pesde 0.7.4:** the generated wrapper looks for a lowercase `bootstrapper`, but the package's Rojo root is named `Bootstrapper`. Changing alias casing and restoring cleanly did not fix it. Use a small project-owned adapter module that requires the real `Bootstrapper` ModuleScript inside the locked `.pesde` package folder, and check its class and source. Don't edit generated packages or upstream source.
- MIT licensed. The package is a single file, `src/init.luau`.
