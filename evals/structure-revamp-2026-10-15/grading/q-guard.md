===== R1 =====
I added a guard at the top of `scripts/check.sh`. It fails the check if `src/server/PlayerData.luau` no longer contains `GetDataStore("PlayerData_v3")`. I haven't run the script.

The failure message says that changing the name orphans saved player data. It also says to update the script if the rename is intended. It runs before `rokit install`, so it fails immediately.

The guard only matches that exact call. If someone moves the name into a constant or another file, it will fail and need updating.

----- R1 changed file: scripts/check.sh -----
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! grep -qF 'GetDataStore("PlayerData_v3")' src/server/PlayerData.luau; then
	echo 'check: DataStore name in src/server/PlayerData.luau is not "PlayerData_v3"; changing it orphans saved player data. Update scripts/check.sh if the rename is intended.' >&2
	exit 1
fi

rokit install
wally install
stylua --check src
selene src
rojo build default.project.json -o build/arena.rbxlx

===== R2 =====
I added the guard to `scripts/check.sh`, right after the restore steps and before the format check. I haven't run it, so it hasn't been break-tested. Bash is disabled in this session.

The guard keeps an exact copy of the line `local store = DataStoreService:GetDataStore("PlayerData_v3")`. It fails the check if any of these is true:
- `src` has more than one `GetDataStore` call.
- `src` has none.
- The one call differs from that line.

The error message names the rule, prints what it found, and says to update `expected_store` in `scripts/check.sh` if the rename is intended. Changing the name on purpose therefore takes two edits, the script and `src/server/PlayerData.luau`.

To break-test it, change `PlayerData_v3` to `PlayerData_v4` in `PlayerData.luau`, run `scripts/check.sh` and confirm it fails with that message. Then revert the change. Run it with Git Bash, not WSL.

I left `KEY_PREFIX` ("player_") unguarded since you only asked about the DataStore name. It's the same kind of saved-data identity, so say if you want it covered too.

----- R2 changed file: scripts/check.sh -----
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

rokit install
wally install

# Guard: the DataStore name is saved-data identity. Changing it hides every existing player's data.
# To rename on purpose, update this line and src/server/PlayerData.luau together.
expected_store='local store = DataStoreService:GetDataStore("PlayerData_v3")'
store_lines=$(grep -rn --include='*.lua' --include='*.luau' 'GetDataStore' src || true)
if [ "$(printf '%s\n' "$store_lines" | grep -c .)" -ne 1 ] || ! printf '%s\n' "$store_lines" | grep -qF -- ":$expected_store"; then
	echo "FAIL guard datastore-name: expected exactly one GetDataStore call, '$expected_store'" >&2
	echo "found:" >&2
	echo "${store_lines:-<none>}" >&2
	echo "If the rename is intended, update expected_store in scripts/check.sh." >&2
	exit 1
fi

stylua --check src
selene src
rojo build default.project.json -o build/arena.rbxlx

===== R3 =====
I added a guard to `scripts/check.sh` that fails the check if `src/server/PlayerData.luau` no longer contains `GetDataStore("PlayerData_v3")`. I haven't run it.

It runs before `rokit install`, so a rename fails right away. It prints the file and the expected name to stderr and exits 1.

If you do mean to change the name, say for a `_v4` migration, update the string in `check.sh` in the same commit.

The guard only looks at that one file. A second `GetDataStore` call elsewhere in `src/` wouldn't be caught.

----- R3 changed file: scripts/check.sh -----
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Renaming the store orphans every saved player's data.
if ! grep -qF 'GetDataStore("PlayerData_v3")' src/server/PlayerData.luau; then
	echo 'src/server/PlayerData.luau: DataStore name must be "PlayerData_v3"' >&2
	exit 1
fi

rokit install
wally install
stylua --check src
selene src
rojo build default.project.json -o build/arena.rbxlx

===== R4 =====
I added the guard, but I couldn't run it. I have no shell tool in this session, so I haven't break-tested it.

- **`scripts/guard_datastore.sh` (new):** it searches `src` for `GetDataStore`, `GetOrderedDataStore` and `GetGlobalDataStore`. It fails unless the only match is `local store = DataStoreService:GetDataStore("PlayerData_v3")` in `src/server/PlayerData.luau`. That covers renaming the store and also adding a second one. The failure message shows the expected and found lines and says to edit `EXPECTED` in the script to change the name on purpose.
- **`scripts/check.sh`:** it now runs `bash scripts/guard_datastore.sh` right after `wally install`.

Changing the name on purpose now takes two edits, the source line and `EXPECTED` in the guard.

To break-test it, change `"PlayerData_v3"` to another name and run `bash scripts/check.sh`. The check should fail at the guard with that message. Then revert the name.

Two things you didn't ask for:
- `KEY_PREFIX = "player_"` is also saved-data identity, and the guard doesn't cover it. I can add it if you want.
- `check.sh` has no per-step output or guard list yet. I kept to its current style.

----- R4 changed file: scripts/check.sh -----
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

rokit install
wally install
bash scripts/guard_datastore.sh
stylua --check src
selene src
rojo build default.project.json -o build/arena.rbxlx

----- R4 changed file: scripts/guard_datastore.sh -----
#!/usr/bin/env bash
# Guard: the DataStore name is saved-data identity. Renaming it hides every
# existing player's data. To change it on purpose, edit EXPECTED below and the
# source line in the same change.
set -euo pipefail
cd "$(dirname "$0")/.."

EXPECTED='src/server/PlayerData.luau:local store = DataStoreService:GetDataStore("PlayerData_v3")'

found=$(grep -rE 'GetDataStore|GetOrderedDataStore|GetGlobalDataStore' src | sed -E 's/^([^:]+):[[:space:]]*/\1:/' || true)

if [ "$found" != "$EXPECTED" ]; then
	echo "FAIL guard datastore-name: saved-data identity changed or a DataStore was added." >&2
	echo "  expected: $EXPECTED" >&2
	echo "  found:    ${found:-<none>}" >&2
	echo "  To change it on purpose, update EXPECTED in scripts/guard_datastore.sh." >&2
	exit 1
fi
