===== R1 =====
Add a top-level `globIgnorePaths` array to `default.project.json`. It's available in Rojo 7.7.

```json
{
  "name": "MyProject",
  "globIgnorePaths": [
    "**/*.story.luau",
    "src/client/Shop/Preview"
  ],
  "tree": {
    "$className": "DataModel",
    ...
  }
}
```

- **Path base:** patterns are relative to the project file's directory.
- **Directory match:** Rojo skips an ignored directory before it descends into it. So `src/client/Shop/Preview` removes the whole folder, including its `init.luau`.
- **Several Preview folders:** use a wildcard such as `"**/Preview"`. It will match any folder or file with that name, so use `"src/client/**/Preview"` if the name appears elsewhere and you want to keep those.
- **Other extensions:** if some stories use `.story.lua` or `.story.tsx`, add `"**/*.story.*"` instead of the narrower pattern.

**Scope:** `globIgnorePaths` applies to every Rojo operation, including `rojo serve`, not just `rojo build`. If you want Preview folders and stories to sync into Studio during development but be left out of builds, keep `default.project.json` unchanged. Make a second file, for example `build.project.json`, with the same tree plus `globIgnorePaths`, and run `rojo build build.project.json -o out.rbxl`.

I haven't run this against your project, so test it with `rojo build` and check that the output no longer contains the Preview and story instances.


===== R2 =====
Rojo's project file has a top-level `globIgnorePaths` field for this. Add it next to `name` and `tree`:

```json
{
  "name": "MyProject",
  "globIgnorePaths": [
    "**/*.story.luau",
    "src/client/Shop/Preview"
  ],
  "tree": {
    "...": "..."
  }
}
```

- **Story files:** `**/*.story.luau` matches every story file at any depth.
- **Preview folder:** list the directory itself (`src/client/Shop/Preview`), not `Preview/**` or just `init.luau`. If you only ignore the contents or the init file, Rojo still turns the directory into an empty `Folder` instance. Ignoring the directory path skips it entirely.
- **All Preview folders:** to cover every one in the project, use `**/Preview` instead.
- **Path base:** patterns are relative to the folder containing the project file.
- **Serve as well as build:** the ignore applies to `rojo serve` too, so stories and previews won't sync into Studio either. If you want them during development, keep a second project file (e.g. `dev.project.json`) without the ignore list. Build with `rojo build default.project.json` for release and `rojo serve dev.project.json` for development.

I haven't looked at your project, so check the result with `rojo build -o test.rbxl` and confirm nothing from Preview or the stories ends up in it.


===== R3 =====
Use the top-level `globIgnorePaths` field in the project file. It is an array of glob patterns matched against paths relative to the project file's directory.

```json
{
  "name": "MyGame",
  "globIgnorePaths": [
    "**/*.story.luau",
    "**/Preview"
  ],
  "tree": {
    "$className": "DataModel",
    "...": "your existing tree"
  }
}
```

- **Stories:** `**/*.story.luau` drops every story file wherever it sits.
- **Init-backed folders:** `**/Preview` ignores the directory itself, so `init.luau` and everything under it go with it. If you wrote `**/Preview/**` instead, the folder's own `init.luau` ModuleScript would stay in the build. Don't use that form alone.
- **Scoping:** to hit only the Shop preview, use the project-relative path `src/client/Shop/Preview`. Don't drop the `src/` prefix, because patterns are relative to the project file's directory.
- **Negation:** Rojo 7.7 supports `!` negation, for example `!**/Keep/Preview` to keep one.

**Dev and release split:** `globIgnorePaths` applies to everything built from that project file, including `rojo serve`. If you want previews and stories in dev and only dropped in release, use a shared `common.project.json` with the full tree. Then add thin wrappers whose `tree` is just `{ "$path": "common.project.json" }`, with the ignore list only in the release wrapper:

```json
{
  "name": "MyGame Release",
  "globIgnorePaths": ["**/*.story.luau", "**/Preview"],
  "tree": { "$path": "common.project.json" }
}
```

Build with `rojo build release.project.json -o game.rbxlx`. Don't add extra services such as `ReplicatedStorage` next to that wrapper's root `$path`. In 7.7.0, `rojo build` then emits two copies of the service, while `rojo sourcemap` shows one and silently drops the added children.

**Verify the result:** I haven't run this against your project. Check the built `.rbxlx` or `rojo sourcemap` output for leftover `Preview` or `.story` instances. Excluded files also disappear from sourcemap-based tooling such as luau-lsp and test discovery, so keep that in mind if you still want type checking on stories.


===== R4 =====
Use `globIgnorePaths`, a top-level field in the project file. It takes glob patterns relative to the project file's directory.

```json
{
  "name": "MyGame",
  "globIgnorePaths": [
    "**/*.story.luau",
    "**/Preview",
    "**/Preview/**"
  ],
  "tree": {
    "$className": "DataModel"
    // ...your existing tree
  }
}
```

- **`**/*.story.luau`** matches every story file at any depth.
- **`**/Preview`** and **`**/Preview/**`** exclude the whole directory, not just the `init.luau` inside it. If you ignored only `**/Preview/init.luau`, Rojo would still turn the folder into a plain `Folder` holding whatever else is in it. The first pattern covers the directory itself and the second covers everything under it.
- **Narrower option:** if only `Shop` should lose its Preview, use `src/client/Shop/Preview` and `src/client/Shop/Preview/**`.

Caveats:
- **Serve is affected too.** `globIgnorePaths` applies to `rojo serve` and `rojo syncback`, not only `rojo build`. If you want stories synced into Studio during development but left out of release builds, keep the default project file with the ignores for builds. Use a second file such as `dev.project.json` without them, and run `rojo serve dev.project.json`.
- **Nested projects don't inherit it.** If a subfolder has its own `*.project.json`, it needs its own `globIgnorePaths`.
- **Not tested here.** I haven't run it against your project, since you asked for chat only. After adding it, run `rojo build -o /tmp/test.rbxl` and check that the Preview folders and stories are gone. The `Preview` directory patterns are the part I'd confirm.
