===== R1 =====
Blink is only partly in. I couldn't run `pesde install`, because the command needs your approval and it wasn't granted. Until it runs, `scripts/check_guards.py` and `bash scripts/check.sh` fail, and the server doesn't send anything yet.

**Done:**
- **Dependency:** `pesde.toml` now pins Blink in `[dev_dependencies]` as `blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }`. That is the version the `roblox-blink` skill was reviewed against.
- **Schema:** `network/main.blink` declares one event, `CoinsChanged`. It is `From: Server`, reliable, carries a `u32`, and uses `RemoteScope = "CoinRun"`. The generated modules will go to `src/server/Network/Server.luau`, `src/client/Network/Client.luau` and `src/shared/Network/Types.luau`.
- **Guard:** `scripts/check_guards.py` now fails the build in three cases:
  - **Event not from the server:** any Blink event that isn't `From: Server`, including one with no `From`.
  - **Functions:** any Blink `function`, because functions are called by the client.
  - **Pin drift:** a locked Blink version other than 0.18.9, with a "re-review this guard" message.

  The messages say how to change the rule on purpose. The reason for pinning is that 0.18.9's generated server parses the incoming buffer before any handler runs (Blink issue #45).
- **Tests:** I tested the schema rules on throwaway files. A good event passes. `From: Client`, a missing `From`, and a `function` inside a `scope` all fail. A commented-out `From: Client` is ignored. I haven't tested the version-pin check, because it needs the lock entry that the install creates.

**Still to do once you approve `pesde install`:**
1. Run `pesde install`, then `pesde run blink -- network/main`, to update `pesde.lock` and generate the modules.
2. Make `Coins.add` in `src/server/Coins.luau` call `Network.CoinsChanged.Fire(player, balance)`. I held this back because `--!strict` would fail on a module that doesn't exist yet. I'll also send the initial 0 on `PlayerAdded`, so a client sees its starting balance. Requiring the generated server module starts networking, so only `Coins.luau` should require it.
3. Clone the `roblox-blink` skill, add Blink to a resource list in `CLAUDE.md`, and run the full `check.sh`.

The `CLAUDE.md` entry will also name the guard, which is why I'm waiting on the install before writing it.

I'll continue from step 1 when you approve the install, or you can run `pesde install` yourself and tell me.

----- R1 commands run -----
$ cd "." && ls -a && cat pesde.toml default.project.json scripts/check.sh && cat src/server/Coins.luau && find src scripts -type f
$ cd "./.claude/skills/roblox-resource-acquisition" && cat references/adopting.md && grep -n -i -B2 -A15 blink references/library-skills.md | head -80; cd ../../..; cat scripts/check_guards.py; cat pesde.lock | head -30; cat rokit
$ cd "./.claude/skills/roblox-resource-acquisition" && cat references/adopting.md
$ cd "." && cat scripts/check_guards.py rokit.toml && ls .claude/skills && grep -n -i blink .claude/skills/roblox-resource-acquisition/references/library-skills.md
$ cd "." && S=".claude/skills/roblox-resource-acquisition" && python "$S/scripts/clone_children.py" --project . --status; ls $S/../../../; ls $S/libraries 2>/dev/null; cat $S/libraries/roblox-blink/SKILL.md 2>/dev/null
$ cd "." && python .claude/skills/roblox-resource-acquisition/scripts/clone_children.py --project . --status
$ cd "." && grep -n -i -B3 -A12 "dev_dependencies\|blink" .claude/skills/roblox-resource-acquisition/scripts/clone_children.py | head -120; cat .claude/skills/roblox-resource-acquisition/references/library-skills.md | sed -n 1,60p
$ cd "./.claude/skills/roblox-resource-acquisition/libraries/roblox-blink" && cat resource.yaml SKILL.md; ls -R .
$ cd "." && cat .claude/skills/roblox-resource-acquisition/libraries/roblox-blink/references/setup.md; cat pesde.lock; cat src/server/init.server.luau src/server/Round.luau; cat .gitignore; which pesde rokit
$ cd "." && cat >> pesde.toml <<'EOF'

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }
EOF
pesde install 2>&1 | tail -15; pesde run blink -- --version 2>&1 | tail -3; grep -n -i blink pesd
$ cd "." && pesde install 2>&1 | tail -15; pesde run blink -- --version 2>&1 | tail -3; grep -n -i blink pesde.lock
$ pesde install
$ cd "./scripts" && python -c "
import check_guards as g, tempfile, pathlib
t = pathlib.Path(tempfile.mkdtemp()); g.ROOT = t
cases = {
 'ok': 'event A { From: Server, Type: Reliable, Call: SingleAsync, Data: u32 }',
 'client': 'ev

----- R1 commands refused by permissions -----
$ cd "./.claude/skills/roblox-resource-acquisition" && cat references/adopting.md && grep -n -i -B2 -A15 blink references/library-skills.md | head -80; cd ../../..; cat scripts/check_guards.py; cat pesde.lock | head -30; cat rokit
$ cd "." && S=".claude/skills/roblox-resource-acquisition" && python "$S/scripts/clone_children.py" --project . --status; ls $S/../../../; ls $S/libraries 2>/dev/null; cat $S/libraries/roblox-blink/SKILL.md 2>/dev/null
$ cd "." && cat >> pesde.toml <<'EOF'

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }
EOF
pesde install 2>&1 | tail -15; pesde run blink -- --version 2>&1 | tail -3; grep -n -i blink pesd
$ cd "." && pesde install 2>&1 | tail -15; pesde run blink -- --version 2>&1 | tail -3; grep -n -i blink pesde.lock
$ pesde install

----- R1 changed file: pesde.toml -----
name = "example/coin_run"
version = "0.1.0"
private = true

[target]
environment = "roblox"

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }

[indices]
default = "https://github.com/pesde-pkg/index"

[wally_indices]
default = "https://github.com/UpliftGames/wally-index"

[dependencies]
Charm = { wally = "littensy/charm", version = "=0.11.1" }
Janitor = { wally = "howmanysmall/janitor", version = "=1.17.0" }
vide = { repo = "https://github.com/centau/vide", rev = "5ed4c01940e6bd578fb83253cfbeda0a6c05177c" }

----- R1 changed file: network/main.blink -----
option ServerOutput = "../src/server/Network/Server.luau"
option ClientOutput = "../src/client/Network/Client.luau"
option TypesOutput = "../src/shared/Network/Types.luau"
option RemoteScope = "CoinRun"

event CoinsChanged { From: Server, Type: Reliable, Call: SingleAsync, Data: u32 }

----- R1 changed file: scripts/check_guards.py -----
"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
- No client-to-server Blink: every event is `From: Server` and there are no functions, which
  clients invoke. Pinned to the Blink version reviewed, because 0.18.9's generated server parses
  an incoming buffer before any handler runs (https://github.com/1Axen/blink/issues/45).
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
GUARDS = [
    ("src/client/UI", "*.luau", re.compile(r"Instance\.new"), "build UI Instances with Vide's create"),
]

BLINK_REVIEWED = "0.18.9"
BLINK_LOCK_KEY = re.compile(r'^\[graph\."1axen/blink@([^ "]+) lune"\]', re.MULTILINE)
BLINK_SCHEMA_GLOBS = ["**/*.blink", "network/**/*.txt"]
BLINK_IGNORED = {"roblox_packages", "lune_packages", ".pesde", "build"}
BLINK_COMMENT = re.compile(r"--[^\n]*")
BLINK_DECLARATION = re.compile(r"\b(event|function)\s+\w+\s*\{")
BLINK_RULE = (
    "Blink is server-to-client only; declare `From: Server` and no functions. "
    "To allow client-to-server, first add a tested receive-side byte and rate budget "
    "(see roblox-blink troubleshooting), then change this guard"
)


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_guards() -> list[str]:
    failures = []
    for folder, pattern, banned, reason in GUARDS:
        for path in sorted((ROOT / folder).rglob(pattern)):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if banned.search(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: {reason}")
    return failures


def check_blink_version() -> list[str]:
    lock = (ROOT / "pesde.lock").read_text(encoding="utf-8")
    found = BLINK_LOCK_KEY.search(lock)
    if not found:
        return ["pesde.lock: Blink is not locked; run `pesde install`"]
    if found.group(1) != BLINK_REVIEWED:
        return [
            f"pesde.lock: client-to-server guard reviewed against Blink {BLINK_REVIEWED}, "
            f"found {found.group(1)}: re-review scripts/check_guards.py, then update BLINK_REVIEWED"
        ]
    return []


def blink_schemas() -> list[Path]:
    paths = {path for glob in BLINK_SCHEMA_GLOBS for path in ROOT.glob(glob)}
    return sorted(p for p in paths if not BLINK_IGNORED & set(p.relative_to(ROOT).parts))


def block_end(text: str, open_at: int) -> int:
    depth = 0
    for index in range(open_at, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return len(text)


def top_level(body: str) -> str:
    depth = 0
    kept = []
    for char in body:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif depth == 0:
            kept.append(char)
    return "".join(kept)


def check_blink_schema(path: Path) -> list[str]:
    text = BLINK_COMMENT.sub(lambda m: " " * len(m.group()), path.read_text(encoding="utf-8"))
    name = path.relative_to(ROOT)
    failures = []
    for declaration in BLINK_DECLARATION.finditer(text):
        number = line_of(text, declaration.start())
        if declaration.group(1) == "function":
            failures.append(f"{name}:{number}: client-invoked function. {BLINK_RULE}")
            continue
        open_at = declaration.end() - 1
        body = top_level(text[open_at + 1 : block_end(text, open_at)])
        if not re.search(r"\bFrom\s*:\s*Server\b", body):
            failures.append(f"{name}:{number}: event is not `From: Server`. {BLINK_RULE}")
    return failures


def check_blink() -> list[str]:
    failures = check_blink_version()
    for path in blink_schemas():
        failures += check_blink_schema(path)
    return failures


def main() -> int:
    failures = check_guards() + check_blink()
    for failure in failures:
        print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

===== R2 =====
The Blink wiring and the guard are written, but I couldn't finish the install, so the project doesn't build yet. `pesde install` needs your approval and I can't run it. I haven't run `check.sh` or any of the other tools.

**To finish, run these from the project root:**
```
pesde install
pesde run blink -- network/main
bash scripts/check.sh
```
`pesde install` updates `pesde.lock`, which `check.sh` needs because it installs with `--locked`. The second command generates `src/server/Network/Server.luau`, `src/client/Network/Client.luau` and `src/shared/Network/Types.luau`. Until they exist, `Coins.luau` requires a missing module. Don't hand-edit those files. `selene src` may complain about the generated code; I haven't seen it run.

**What changed**
- **`pesde.toml`:** adds the Blink CLI 0.18.9 as a `[dev_dependencies]` entry, as the Blink skill describes.
- **`network/main.blink`:** declares one event, `CoinsChanged`, sent from the server and carrying a `u32` balance. Remotes are scoped to `CoinRun`, and the client handler is async.
- **`src/server/Coins.luau`:** `Coins.add` now fires `CoinsChanged` to that player with their new balance.
- **`scripts/check_guards.py`:** a new Blink guard fails on any `From: Client` event or any `function` declaration in any `.blink` file. It ignores comments, handles declarations split across lines, and is part of `check.sh`. I tested it on a throwaway schema and then deleted that file.

**Things to know**
- I banned Blink `function` too, even though your rule only mentions events, because a function is a client call the server answers. Say so if you want functions allowed.
- The guard only reads `.blink` files. Blink also accepts a `.txt` schema, which it would miss.
- I did not touch the client. Nothing listens to `CoinsChanged` yet, so `CoinLabel` still shows "Coins: 0". Updating the label changes what players see, so I held off. The natural fit is a Charm atom in `src/client/State` that the Blink handler sets and `CoinLabel` reads. Want me to do that?
- I don't fire anything on join, because the client may not be listening yet and the label already starts at 0. The first update arrives with the first coin. A client that joins late won't see coins it earned before it connected, and it can't ask for them, since client-to-server events are banned.

----- R2 commands run -----
$ cd "." && ls -a && cat scripts/check.sh && cat scripts/check_guards.py && cat src/server/Coins.luau && cat default.project.json pesde.toml rokit.toml 2>/dev/null; find src .claude -type f | head -50
$ ls "<plugin>/skills/roblox-resource-acquisition/" 2>&1 | head
$ cd "./.claude/skills/roblox-resource-acquisition/libraries/roblox-blink" && cat SKILL.md resource.yaml references/setup.md references/schema.md references/api-and-lifecycle.md
$ cd "." && cat src/server/init.server.luau src/server/Round.luau src/client/init.client.luau src/client/UI/CoinLabel.luau src/client/State/README.md .claude/settings.json selene.toml pesde.lock | head -250
$ cd "." && for t in rokit pesde rojo stylua selene lune python; do printf "%s: " $t; command -v $t || echo missing; done; ls roblox_packages 2>&1 | head -3
$ which rokit pesde rojo stylua selene lune python; ls roblox_packages
$ pesde install 2>&1 | tail -15 && pesde run blink -- --version && pesde run blink -- network/main 2>&1 | tail -10; ls -R src | head -30
$ pesde install
$ cat > scripts/check_guards.py <<'EOF'
"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
- No client-to-server Blink: schemas may only declare events with From: Server.
"""
from pathlib import Path
import re
imp
$ python scripts/check_guards.py
$ python scripts/check_guards.py
$ rm network/bad_probe.blink

----- R2 commands refused by permissions -----
$ ls "<plugin>/skills/roblox-resource-acquisition/" 2>&1 | head
$ cd "." && for t in rokit pesde rojo stylua selene lune python; do printf "%s: " $t; command -v $t || echo missing; done; ls roblox_packages 2>&1 | head -3
$ pesde install 2>&1 | tail -15 && pesde run blink -- --version && pesde run blink -- network/main 2>&1 | tail -10; ls -R src | head -30
$ pesde install
$ cat > scripts/check_guards.py <<'EOF'
"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
- No client-to-server Blink: schemas may only declare events with From: Server.
"""
from pathlib import Path
import re
imp

----- R2 changed file: pesde.toml -----
name = "example/coin_run"
version = "0.1.0"
private = true

[target]
environment = "roblox"

[indices]
default = "https://github.com/pesde-pkg/index"

[wally_indices]
default = "https://github.com/UpliftGames/wally-index"

[dependencies]
Charm = { wally = "littensy/charm", version = "=0.11.1" }
Janitor = { wally = "howmanysmall/janitor", version = "=1.17.0" }
vide = { repo = "https://github.com/centau/vide", rev = "5ed4c01940e6bd578fb83253cfbeda0a6c05177c" }

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }

----- R2 changed file: network/main.blink -----
option ServerOutput = "../src/server/Network/Server.luau"
option ClientOutput = "../src/client/Network/Client.luau"
option TypesOutput = "../src/shared/Network/Types.luau"
option RemoteScope = "CoinRun"

event CoinsChanged { From: Server, Type: Reliable, Call: SingleAsync, Data: u32 }

----- R2 changed file: scripts/check_guards.py -----
"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
- No client-to-server Blink: schemas may only declare events with From: Server.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
GUARDS = [
    ("src/client/UI", "*.luau", re.compile(r"Instance\.new"), "build UI Instances with Vide's create"),
]
BLINK_BANNED = [
    (re.compile(r"\bFrom\s*:\s*Client\b"), "Blink events must be From: Server"),
    (re.compile(r"^\s*(?:export\s+)?function\b", re.MULTILINE), "Blink functions are client-to-server calls"),
]
BLINK_COMMENT = re.compile(r"--\[\[.*?\]\]|--[^\n]*", re.DOTALL)


def blank_comments(text: str) -> str:
    return BLINK_COMMENT.sub(lambda match: re.sub(r"[^\n]", " ", match.group()), text)


def check_lines() -> list[str]:
    failures = []
    for folder, pattern, banned, reason in GUARDS:
        for path in sorted((ROOT / folder).rglob(pattern)):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if banned.search(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: {reason}")
    return failures


def check_blink() -> list[str]:
    failures = []
    for path in sorted(ROOT.rglob("*.blink")):
        text = blank_comments(path.read_text(encoding="utf-8"))
        for banned, reason in BLINK_BANNED:
            for match in banned.finditer(text):
                number = text.count("\n", 0, match.start()) + 1
                failures.append(f"{path.relative_to(ROOT)}:{number}: {reason}")
    return failures


def main() -> int:
    failures = check_lines() + check_blink()
    for failure in failures:
        print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

----- R2 changed file: src/server/Coins.luau -----
--!strict
local Players = game:GetService("Players")

local Network = require(script.Parent.Network.Server)

local Coins = {}

local balances: { [Player]: number } = {}

function Coins.get(player: Player): number
	return balances[player] or 0
end

function Coins.add(player: Player, amount: number)
	balances[player] = Coins.get(player) + amount
	Network.CoinsChanged.Fire(player, balances[player])
end

function Coins.start()
	Players.PlayerAdded:Connect(function(player)
		balances[player] = 0
	end)
	Players.PlayerRemoving:Connect(function(player)
		balances[player] = nil
	end)
end

return Coins

===== R3 =====
I've stopped. I added Blink to `pesde.toml`, but I couldn't install it, so nothing else is wired up.

**Done:**
- `pesde.toml` now has `blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }` under `[dev_dependencies]`. It's pinned to the version the Blink skill was reviewed against.

**Blocked:** `pesde install` needs your approval and it was declined. It downloads the Blink CLI from the pesde registry and rewrites `pesde.lock`. I haven't retried or tried another route.

**Still to do once the install works:**
1. Write `network/main.blink` with one server-to-client event, `CoinsChanged`, carrying the new balance. I'd use a `u32` payload with `SingleAsync` handling. The client output would go in `src/client/Network`, the server output in `src/server/Network` and the types in `src/shared/Network`.
2. Compile it with `pesde run blink -- network/main`.
3. Call `CoinsChanged.Fire(player, balance)` from `Coins.add` in `src/server/Coins.luau`.
4. Add a guard to `scripts/check_guards.py`, so `check.sh` fails on any of these:
   - an event with `From: Client`
   - any `function` declaration, because Blink functions are called by the client
   - a Blink version in `pesde.lock` other than 0.18.9, with a "re-review this guard" message

   The guard covers every `.blink` file, so a client-to-server event can't be added later without failing the check. I'd break-test it once.
5. Clone the `roblox-blink` skill, and add a Blink entry to `CLAUDE.md` that names the ban and the guard.

**Why the ban matters:** the Blink skill notes that 0.18.9 parses the whole incoming buffer before any handler runs (Blink issue #45). A client could send a huge buffer to the server and Blink's schema limits wouldn't stop it. That's why the guard enforces your rule and doesn't leave it to `CLAUDE.md`.

**Decision for you:** I've only planned the server side. Showing the new balance in `CoinLabel` would be a visible change, so I'd leave it for you to decide.

Can you approve `pesde install`, or run it yourself? Once it's done I'll do steps 1 to 5 and then run `bash scripts/check.sh`.

----- R3 commands run -----
$ cd "." && ls -a && cat pesde.toml default.project.json scripts/check.sh scripts/check_guards.py; find src .claude -type f | head -80
$ cd "./.claude/skills/roblox-resource-acquisition" && python scripts/check_updates.py; python scripts/clone_children.py --project "." --status
$ cd "." && cat .claude/skills/roblox-resource-acquisition/libraries/roblox-blink/references/setup.md; for f in src/server/init.server.luau src/server/Round.luau src/client/init.client.luau src/client/State/README.md src/client/UI
$ cd "."
cat .claude/skills/roblox-resource-acquisition/libraries/roblox-blink/references/setup.md
cat src/server/init.server.luau src/server/Round.luau src/client/init.client.luau src/client/State/README.md src/client/UI/CoinLabe
$ which pesde rokit python stylua selene rojo
$ cd "."
cat >> pesde.toml <<'EOF'

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }
EOF
cp pesde.lock /tmp/pesde.lock.bak
pesde install 2>&1 | tail -15; git status 2>&1 | head -1; ls; pesd
$ cd "." && pesde install 2>&1 | tail -15; pesde run blink -- --version 2>&1 | tail -3; grep -n "blink" pesde.lock | head -5
$ pesde install

----- R3 commands refused by permissions -----
$ cd "." && cat .claude/skills/roblox-resource-acquisition/libraries/roblox-blink/references/setup.md; for f in src/server/init.server.luau src/server/Round.luau src/client/init.client.luau src/client/State/README.md src/client/UI
$ cd "."
cat >> pesde.toml <<'EOF'

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }
EOF
cp pesde.lock /tmp/pesde.lock.bak
pesde install 2>&1 | tail -15; git status 2>&1 | head -1; ls; pesd
$ cd "." && pesde install 2>&1 | tail -15; pesde run blink -- --version 2>&1 | tail -3; grep -n "blink" pesde.lock | head -5
$ pesde install

----- R3 changed file: pesde.toml -----
name = "example/coin_run"
version = "0.1.0"
private = true

[target]
environment = "roblox"

[indices]
default = "https://github.com/pesde-pkg/index"

[wally_indices]
default = "https://github.com/UpliftGames/wally-index"

[dependencies]
Charm = { wally = "littensy/charm", version = "=0.11.1" }
Janitor = { wally = "howmanysmall/janitor", version = "=1.17.0" }
vide = { repo = "https://github.com/centau/vide", rev = "5ed4c01940e6bd578fb83253cfbeda0a6c05177c" }

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }

===== R4 =====
The Blink setup and the guard are written, but nothing has been installed, generated or run end to end. `pesde install` needed approval that wasn't granted, so the Blink CLI isn't installed and `Coins.luau` requires a generated module that doesn't exist yet.

**What I changed**
- **Dependency:** `pesde.toml` now pins Blink `=0.18.9` as a dev dependency.
- **Schema:** `network/main.blink` has one event, `CoinsChanged`, which is server-to-client, reliable, and carries a `u32` balance. The generated server, client and types modules go to `src/server/Network`, `src/client/Network` and `src/shared/Network`.
- **Server:** `Coins.add` in `src/server/Coins.luau` now fires `CoinsChanged` to that player with their new balance.
- **Guard:** `scripts/check_guards.py` now fails the check on any `From: Client` event or any Blink `function` in the schema files. A `function` counts because the client invokes it, so it's also a client-to-server entry point.
  - It reads the schema with comments stripped, so a comment mentioning `From: Client` won't trigger it, and `From:` split across lines is still caught.
  - It also fails if the lockfile's Blink version isn't 0.18.9, or if no schema is found, so it can't silently stop protecting you.
- **`check.sh`:** it now runs the guards and then regenerates the Blink modules before `stylua` and `selene`.
- **`CLAUDE.md`:** I added Blink to the library list and noted the rule.

**What I checked**
I ran the guard against a throwaway copy with a fake lock entry. It passed a clean schema and failed an event with `From:` split across lines and a `function`, each with a file and line. `python scripts/check_guards.py` fails right now because `pesde.lock` has no Blink entry. That's the version check doing its job until you install.

**What's left for you**
1. Run `pesde install`, which pins Blink in `pesde.lock`.
2. Run `bash scripts/check.sh` to generate the three modules and run all the checks.
3. The generated Blink code may fail `stylua --check` or `selene`. If it does, I'd exclude the three `Network/` folders from both.

**Open question**
I didn't touch the client UI, since that changes what players see. Right now `CoinLabel` still shows a fixed "Coins: 0". Do you want me to wire the client to `CoinsChanged`, through a Charm atom in `src/client/State` that `CoinLabel` reads?

----- R4 commands run -----
$ cd "." && ls -la && cat src/server/Coins.luau && cat scripts/check.sh && cat scripts/check_guards.py && cat default.project.json pesde.toml rokit.toml 2>/dev/null; ls .claude/skills; find src -type f | head -50
$ cd "./.claude/skills" && ls -R roblox-resource-acquisition | head -60; grep -ril blink . | head; cat ../../src/server/init.server.luau ../../src/client/init.client.luau ../../src/client/State/README.md ../../src/server/Round.lua
$ cd "." && cat selene.toml stylua.toml pesde.lock src/server/Round.luau src/client/UI/CoinLabel.luau src/client/UI/App.luau; cat .claude/skills/roblox-resource-acquisition/libraries/roblox-blink/resource.yaml; ls .claude/skills/r
$ cd "." && export PATH="$HOME/.rokit/bin:$PATH" && which pesde rokit stylua selene rojo lune python; pesde --version
$ cd "."; ls ~/.rokit/bin 2>&1; which pesde rokit python
$ which pesde rokit python stylua selene rojo
$ cd "." && pesde install 2>&1 | tail -20 && pesde run blink -- --version 2>&1 | tail -5; ls
$ pesde install
$ cd "." && python - <<'EOF'
from pathlib import Path
p = Path("scripts/check.sh")
s = p.read_text()
s = s.replace("python scripts/check_guards.py\n", "python scripts/check_guards.py\npesde run blink -- network/main\n")
p.write_te
$ cd "." && python scripts/check_guards.py; echo "exit $?"
$ python scripts/check_guards.py
$ python -I - <<'EOF'
import importlib.util, tempfile
from pathlib import Path
src = Path("scripts/check_guards.py").resolve()
spec = importlib.util.spec_from_file_location("g", src)
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
cases = {
 "clean": 'event A { From: Server, Type
$ python -I scripts/_breaktest.py
$ rm scripts/_breaktest.py && ls scripts
$ rm -r scripts/__pycache__

----- R4 commands refused by permissions -----
$ cd "./.claude/skills" && ls -R roblox-resource-acquisition | head -60; grep -ril blink . | head; cat ../../src/server/init.server.luau ../../src/client/init.client.luau ../../src/client/State/README.md ../../src/server/Round.lua
$ cd "." && export PATH="$HOME/.rokit/bin:$PATH" && which pesde rokit stylua selene rojo lune python; pesde --version
$ cd "."; ls ~/.rokit/bin 2>&1; which pesde rokit python
$ cd "." && pesde install 2>&1 | tail -20 && pesde run blink -- --version 2>&1 | tail -5; ls
$ pesde install
$ cd "." && python - <<'EOF'
from pathlib import Path
p = Path("scripts/check.sh")
s = p.read_text()
s = s.replace("python scripts/check_guards.py\n", "python scripts/check_guards.py\npesde run blink -- network/main\n")
p.write_te
$ cd "." && python scripts/check_guards.py; echo "exit $?"
$ python -I - <<'EOF'
import importlib.util, tempfile
from pathlib import Path
src = Path("scripts/check_guards.py").resolve()
spec = importlib.util.spec_from_file_location("g", src)
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
cases = {
 "clean": 'event A { From: Server, Type

----- R4 changed file: CLAUDE.md -----
# coin-run

Roblox round game: Rojo + pesde + Vide + Charm + Janitor. Run `bash scripts/check.sh` before calling a change done; `python scripts/check_guards.py` runs the project's guards on their own.

## Libraries

- **Vide**: UI rendering. Use the `roblox-vide` skill.
- **Janitor**: cleanup ownership. Use the `roblox-janitor` skill.
- **Charm**: client-only UI state shared across components, in `src/client/State`.
- **Signal** (`src/shared/Signal.luau`): in-runtime custom events. A vendored module, not a package.
- **Blink**: server-to-client networking, schema in `network/main.blink`, generated modules in each `Network/` folder (never edit). No client-to-server events or functions: `check_guards.py` enforces it.

----- R4 changed file: pesde.toml -----
name = "example/coin_run"
version = "0.1.0"
private = true

[target]
environment = "roblox"

[indices]
default = "https://github.com/pesde-pkg/index"

[wally_indices]
default = "https://github.com/UpliftGames/wally-index"

[dependencies]
Charm = { wally = "littensy/charm", version = "=0.11.1" }
Janitor = { wally = "howmanysmall/janitor", version = "=1.17.0" }
vide = { repo = "https://github.com/centau/vide", rev = "5ed4c01940e6bd578fb83253cfbeda0a6c05177c" }

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }

----- R4 changed file: network/main.blink -----
option ServerOutput = "../src/server/Network/Server.luau"
option ClientOutput = "../src/client/Network/Client.luau"
option TypesOutput = "../src/shared/Network/Types.luau"
option RemoteScope = "CoinRun"

event CoinsChanged { From: Server, Type: Reliable, Call: SingleAsync, Data: u32 }

----- R4 changed file: scripts/check.sh -----
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

rokit install
pesde install --locked
python scripts/check_guards.py
pesde run blink -- network/main
stylua --check src
selene src
rojo build default.project.json -o build/coin-run.rbxlx

----- R4 changed file: scripts/check_guards.py -----
"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
- No client-to-server Blink: schemas under network/ may not declare `From: Client` events or
  functions (a function is invoked by the client). Reviewed against Blink 0.18.9, whose generated
  server parses every incoming buffer before any handler runs. To allow one on purpose, add a
  receive-side byte and rate budget first, then change this guard.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
GUARDS = [
    ("src/client/UI", "*.luau", re.compile(r"Instance\.new"), "build UI Instances with Vide's create"),
]

BLINK_VERSION = "0.18.9"
BLINK_DIR = "network"
BLINK_BANS = [
    (re.compile(r"\bFrom\s*:\s*Client\b", re.IGNORECASE), "client-to-server Blink events are banned"),
    (re.compile(r"\bfunction\s+\w+", re.IGNORECASE), "Blink functions are client-to-server calls and are banned"),
]
BLINK_COMMENT = re.compile(r"--\[(=*)\[.*?\]\1\]|--[^\n]*", re.DOTALL)


def blink_failures() -> list[str]:
    lock = (ROOT / "pesde.lock").read_text(encoding="utf-8")
    found = re.search(r"1axen/blink@([^\s\"]+)", lock)
    if not found or found.group(1) != BLINK_VERSION:
        return [f"pesde.lock: blink guard reviewed against {BLINK_VERSION}, found {found and found.group(1)}: re-review it"]

    schemas = sorted([*(ROOT / BLINK_DIR).rglob("*.blink"), *(ROOT / BLINK_DIR).rglob("*.txt")])
    if not schemas:
        return [f"{BLINK_DIR}/: no Blink schema found, so the client-to-server guard has nothing to check"]

    failures = []
    for path in schemas:
        text = BLINK_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), path.read_text(encoding="utf-8"))
        for banned, reason in BLINK_BANS:
            for match in banned.finditer(text):
                number = text.count("\n", 0, match.start()) + 1
                failures.append(f"{path.relative_to(ROOT).as_posix()}:{number}: {reason}")
    return failures


def main() -> int:
    failures = []
    for folder, pattern, banned, reason in GUARDS:
        for path in sorted((ROOT / folder).rglob(pattern)):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if banned.search(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: {reason}")
    failures += blink_failures()
    for failure in failures:
        print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

----- R4 changed file: src/server/Coins.luau -----
--!strict
local Players = game:GetService("Players")

local Network = require(script.Parent.Network.Server)

local Coins = {}

local balances: { [Player]: number } = {}

function Coins.get(player: Player): number
	return balances[player] or 0
end

function Coins.add(player: Player, amount: number)
	local balance = Coins.get(player) + amount
	balances[player] = balance
	Network.CoinsChanged.Fire(player, balance)
end

function Coins.start()
	Players.PlayerAdded:Connect(function(player)
		balances[player] = 0
	end)
	Players.PlayerRemoving:Connect(function(player)
		balances[player] = nil
	end)
end

return Coins
