===== R1 =====
Add `globIgnorePaths` at the top level of the project file, next to `name` and `tree`:

```json
{
  "name": "MyGame",
  "globIgnorePaths": [
    "**/*.story.luau",
    "**/Preview"
  ],
  "tree": {
    "$path": "src"
  }
}
```

- **`**/*.story.luau`** drops every story file at any depth.
- **`**/Preview`** drops the whole `Preview` directory, including its `init.luau`. Don't write `**/Preview/**` instead. That pattern removes the contents but leaves the directory's own ModuleScript, so an empty `Preview` still gets built.
- Globs are matched relative to the directory containing the project file. If the project file isn't at the repo root, the patterns still work, but check where it lives.
- `globIgnorePaths` applies to everything Rojo reads, including `rojo serve` and `rojo sourcemap`, not just `rojo build`. Once you add it to `default.project.json`, stories and previews also vanish from live sync, from the sourcemap, and from luau-lsp's view of those files. That is probably not what you want if you use UI Labs in Studio or type-check the stories.

I'd recommend a two-file setup, which I've confirmed on Rojo 7.7. Move the current tree into `common.project.json` and leave `default.project.json` as a thin wrapper for dev (serve, sourcemap, luau-lsp). Then add a release wrapper that applies the ignores:

```json
{
  "name": "MyGame Release",
  "globIgnorePaths": [
    "**/*.story.luau",
    "**/Preview"
  ],
  "tree": {
    "$path": "common.project.json"
  }
}
```

Build it with `rojo build release.project.json -o build.rbxlx`. Two caveats:

- Don't add a service next to the wrapper's root `$path`. On 7.7.0 and 7.7.1, `rojo build` then emits that service twice.
- If you want it settled, check the built `.rbxlx` for `.story` and `Preview` and confirm neither appears. The sourcemap and the built place can disagree.

Packages can also ship their own dev files, such as a dependency's `init.spec.lua`. Add patterns for those if you want them gone too.

You asked for the exclusion to be in `default.project.json`, so the first snippet does that directly. The two-file setup changes how your dev workflow behaves, so tell me which you want if you'd like me to make the edit.

----- R1 changed no files -----

===== R2 =====
Add a top-level `globIgnorePaths` to `default.project.json`. It sits beside `name` and `tree`, not inside `tree`. It is available in Rojo 7.x, and your 7.7 supports it.

```json
{
  "name": "arena",
  "globIgnorePaths": [
    "**/*.story.luau",
    "**/Preview"
  ],
  "tree": {
    "$className": "DataModel",
    "ReplicatedStorage": {
      "Shared": { "$path": "src/shared" },
      "Client": { "$path": "src/client" },
      "Packages": { "$path": "Packages" }
    },
    "ServerScriptService": { "Server": { "$path": "src/server" } }
  }
}
```

- **Glob base:** patterns match relative to the project file's directory.
- **Why `**/Preview` and not `**/Preview/**`:** because `Preview` is backed by `init.luau`, it becomes a ModuleScript with children. `**/Preview` drops the directory and everything under it. `**/Preview/**` would remove only the contents and leave the empty `Preview` ModuleScript in the build.
- **Scope:** `**/Preview` matches any folder named `Preview` anywhere in the mapped paths, including `Packages`. If you only want `src/client/Shop/Preview`, use `src/client/**/Preview` instead.
- **Negation:** `!` patterns work from 7.7.0. You can use one to keep a specific match.

This config applies to `rojo serve` as well as `rojo build`. Your stories and previews will therefore disappear from live sync, and from the sourcemap and luau-lsp. UI Labs needs them in Studio, so that is probably not what you want.

The pattern the Rojo reference in this project's skill recommends is to split the config into two files:

- **`common.project.json`:** holds the full tree you have now.
- **`default.project.json`:** a thin dev wrapper with `"tree": { "$path": "common.project.json" }`. It has no ignores, so `serve`, the sourcemap and luau-lsp still see stories.
- **`release.project.json`:** the same wrapper plus the `globIgnorePaths` above. You build with `rojo build release.project.json -o game.rbxl`.

Two caveats with the split:

- **Service placement:** don't add services beside the wrapper's root `$path`. On 7.7.0 and 7.7.1 that makes `rojo build` emit the service twice.
- **`emitLegacyScripts`:** if you set it, put it in the file that holds the tree. A wrapper's value doesn't reach a nested project.

After building, confirm the exclusions worked. Check that no `.story` or `Preview` instances appear in the built `.rbxlx`.

I haven't edited any files. I can do the split if you want.

----- R2 changed no files -----

===== R3 =====
Add a top-level `globIgnorePaths` array to `default.project.json`. Patterns are globs relative to the project file's directory:

```json
{
  "name": "srp-revamp",
  "globIgnorePaths": [
    "src/client/Shop/Preview",
    "**/*.story.luau"
  ],
  "tree": {
    "...": "..."
  }
}
```

- **`src/client/Shop/Preview`:** this matches the folder itself, so Rojo skips the whole thing, including `init.luau` and any children. A pattern like `**/Preview/**` can leave the folder (and its `init`) behind as an empty instance, so I'd ignore the directory path. To exclude every `Preview` folder in the project, use `**/Preview`. That also catches any unrelated folder with that name.
- **`**/*.story.luau`:** this matches story files at any depth.

I haven't run this against your tree, so check it with `rojo build -o test.rbxl` and look for the stories and Preview in the output. `rojo sourcemap default.project.json` also works and is quicker to inspect.

`globIgnorePaths` applies to `rojo serve` as well as `rojo build`. Rojo has no build-only exclusion. If you use UI Labs, your stories and Preview folders would stop syncing into Studio, so they'd disappear from the storybook.

The usual fix is a second project file for builds. Copy `default.project.json` to something like `build.project.json`, add `globIgnorePaths` only there, and run `rojo build build.project.json -o game.rbxl`. Keep `default.project.json` without the ignores for `rojo serve`.

I can set up either layout if you want me to.

----- R3 changed no files -----

===== R4 =====
Use the top-level `globIgnorePaths` field in `default.project.json`. It takes glob patterns relative to the project file's folder, and Rojo skips any matching path:

```json
{
  "name": "srp-revamp",
  "globIgnorePaths": [
    "**/*.story.luau",
    "src/client/Shop/Preview"
  ],
  "tree": {
    "$className": "DataModel"
  }
}
```

Keep your existing `tree` as it is. The snippet only shows where the new field goes.

- **Ignore the folder, not the `init.luau`.** If you ignore only `src/client/Shop/Preview/init.luau`, Rojo no longer sees an init script. The folder then becomes a plain `Folder`, and its children still sync. Ignoring the directory path drops the whole subtree.
- **Match all Preview folders.** To exclude every init-backed Preview folder, use `**/Preview` instead of the explicit path.
- **Use forward slashes.** Write patterns with `/`, even on Windows.
- **The ignore applies to `rojo serve` as well as `rojo build`.** `globIgnorePaths` can't distinguish between them. If you want stories synced in Studio for UI Labs but left out of release builds, keep the ignore list in a separate project file, such as `build.project.json`. Then run `rojo build build.project.json -o game.rbxl`.

I haven't edited any files and haven't run a build to confirm the pattern behavior. Test it with `rojo build -o test.rbxl` and check that no Preview or story instances appear.

----- R4 changed no files -----
