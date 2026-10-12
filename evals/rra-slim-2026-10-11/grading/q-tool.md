# q-tool

Prompt: Add StyLua to this project so we can format our Luau code. Make the needed file edits (you can't run commands).

---

## Answer A

### Final message

I added StyLua to the project with three new files in the project root. I couldn't run anything, so none of it has been tried.

- **`rokit.toml`** pins `JohnnyMorganz/StyLua@2.0.2`. The project had no tool manager, so I used Rokit.
- **`stylua.toml`** sets `syntax = "Luau"`, 120 columns, tab indentation, and double quotes unless a string contains one. Require sorting is off, so StyLua won't reorder `require` lines. Change any of these if you have a style preference.
- **`.styluaignore`** keeps StyLua away from `Packages/`, `roblox_packages/`, `luau_packages/`, `sourcemap.json` and `.claude/`.

I picked 2.0.2 because I'm sure it exists. I had no way to look up the newest release, so you may want to bump it.

Run these in the project root:
1. `rokit install` restores the pinned StyLua.
2. `stylua src` formats the three existing files.
3. `stylua --check src` is the read-only check you can use in CI or a pre-commit hook.

The existing `src/*` files are tiny, so `stylua src` probably won't change them.

### File written: .styluaignore

```
# Package-manager output and generated files
Packages/
roblox_packages/
luau_packages/
sourcemap.json

# Tool and skill content, not game source
.claude/

```

### File written: rokit.toml

```
[tools]
stylua = "JohnnyMorganz/StyLua@2.0.2"

```

### File written: stylua.toml

```
syntax = "Luau"
column_width = 120
line_endings = "Unix"
indent_type = "Tabs"
indent_width = 4
quote_style = "AutoPreferDouble"
call_parentheses = "Always"
collapse_simple_statement = "Never"

[sort_requires]
enabled = false

```

---

## Answer B

### Final message

I've added StyLua config files and I'm about to wrap up. I didn't run anything, so none of it has been tested.

I created three files in the project root:
- **`rokit.toml`** pins `stylua = "johnnymorganz/stylua@2.1.0"`. The project had no tool manifest, so this is a new one.
- **`stylua.toml`** sets `syntax = "Luau"` and keeps StyLua's default style.
- **`.styluaignore`** skips `Packages/`, `ServerPackages/`, `DevPackages/`, `sourcemap.json` and `.claude/`, so installed packages, generated output and the skill files aren't formatted.

I picked 2.1.0 from memory and couldn't check it against the latest StyLua release. Please confirm it exists and bump it if you want something newer.

To use it:
1. Run `rokit install` to restore the pinned tool. If Rokit isn't installed yet, install that first.
2. Run `stylua --check src` to see what would change.
3. Run `stylua src` to format.

A CI step or editor format-on-save would be the natural next addition. I didn't add one because you only asked for StyLua itself.

### File written: .styluaignore

```
# Installed packages (Wally/pesde) and generated output
Packages/
ServerPackages/
DevPackages/
sourcemap.json

# Agent skills and tooling, not game source
.claude/

```

### File written: rokit.toml

```
[tools]
stylua = "johnnymorganz/stylua@2.1.0"

```

### File written: stylua.toml

```
syntax = "Luau"

```

---

## Answer C

### Final message

StyLua is configured, but I couldn't run any commands, so none of it has been run.

I added three files at the project root:
- **`rokit.toml`** pins `stylua = "JohnnyMorganz/stylua@2.1.0"`. The project had no tool manager, so I used Rokit.
- **`stylua.toml`** sets Luau syntax, 120 columns, tab indentation and double quotes. The two Luau files in `src/` are one-liners, so I had no existing style to match. Adjust it if you prefer something else.
- **`.styluaignore`** excludes `Packages/`, the other pesde package folders, `sourcemap.json`, Blink-generated output and `.claude/`. The `Blink/` and `*.blink.luau` patterns are guesses, because the project has no Blink output yet.

The 2.1.0 pin is from memory. I couldn't look up the current release, so check it on the StyLua releases page and bump it if there's a newer stable one.

To start using it:
1. Run `rokit install`. It may ask you to trust the tool first.
2. Run `stylua --check --respect-ignores src` to check formatting without changing files.
3. Run `stylua --respect-ignores src` to apply formatting.

I didn't add CI, an editor setting or a format-on-save hook. Say if you want any of those.

### File written: .styluaignore

```
# Installed or generated code
Packages/
roblox_packages/
luau_packages/
lune_packages/
sourcemap.json

# Blink-generated output
**/Blink/
*.blink.luau

# Bundled agent skills (not project source)
.claude/

```

### File written: rokit.toml

```
[tools]
stylua = "JohnnyMorganz/stylua@2.1.0"

```

### File written: stylua.toml

```
syntax = "Luau"
column_width = 120
line_endings = "Unix"
indent_type = "Tabs"
indent_width = 4
quote_style = "AutoPreferDouble"
call_parentheses = "Always"
collapse_simple_statement = "Never"

[sort_requires]
enabled = false

```

---

## Answer D

### Final message

I added StyLua with three new files in the project root. I couldn't run anything, so none of it has been tested.

- **`rokit.toml`**: pins `JohnnyMorganz/StyLua@2.0.2`. The project had no tool manager, so I used Rokit.
- **`stylua.toml`**: sets `syntax = "Luau"`, 120 columns, tab indents, Unix line endings, double quotes where possible, and no require sorting. These are my own choices, because the project had no existing style config. If you'd rather match StyLua's defaults, delete the keys you don't care about. Your existing `src/` files may reformat on the first run.
- **`.styluaignore`**: excludes `Packages/`, `DevPackages/`, `ServerPackages/`, `sourcemap.json` and `.claude/`. The `.claude/` folder holds skill example scripts, which aren't project source.

I picked 2.0.2 because I know it exists. I couldn't check for a newer release, so run `rokit update` if you want the latest.

Next steps, from the project root:
1. Run `rokit install`.
2. Run `stylua --check --respect-ignores src` to see what would change.
3. Run `stylua --respect-ignores src` to format.

I didn't wire up CI or an editor integration. I also didn't touch the staged and modified skill files already in your working tree.

### File written: .styluaignore

```
# Installed packages and generated output
Packages/
DevPackages/
ServerPackages/
sourcemap.json

# Agent skills and their example scripts are not project source
.claude/

```

### File written: rokit.toml

```
[tools]
stylua = "JohnnyMorganz/StyLua@2.0.2"

```

### File written: stylua.toml

```
syntax = "Luau"
column_width = 120
line_endings = "Unix"
indent_type = "Tabs"
indent_width = 4
quote_style = "AutoPreferDouble"
call_parentheses = "Always"

[sort_requires]
enabled = false

```
