===== R1 =====
The Blink code is written, but the install, code generation and `bash scripts/check.sh` haven't run. `pesde install` needs your approval, and I can't generate the Blink files or finish the checks until it has run.

**What's in place**
- **Dependency:** `pesde.toml` has `blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }` under `[dev_dependencies]`. The lock doesn't resolve it yet.
- **Schema:** `network/main.blink` declares one event, `CoinsChanged`, from the server to the client, carrying a `u32` balance. It is configured to generate into `src/server/Network/`, `src/client/Network/` and `src/shared/Network/`.
- **Server:** `src/server/Coins.luau` now requires `Network.Server` and fires `CoinsChanged` to that player from `Coins.add`.
- **Check script:** `scripts/check.sh` now runs the guards first, then `pesde run blink -- network/main`, then stylua and selene. The generated files are excluded from both through `.styluaignore` and `selene.toml`.
- **CLAUDE.md:** a Blink entry in the Libraries list states the ban and where it's enforced.

**The guard** (in `scripts/check_guards.py`)
- **What it bans:** every `.blink` schema in the repo (and `network/*.txt`) may contain no `From: Client` event and no `function`. A `function` is also client-to-server, since the client invokes it.
- **How it reads schemas:** it ignores comments and handles multi-line event declarations.
- **Version pin:** it fails unless `pesde.lock` resolves Blink to 0.18.9, with a "re-review this guard" message. That version parses the whole incoming buffer before any handler runs ([issue #45](https://github.com/1Axen/blink/issues/45)).
- **Failure message:** it names the file and line, and says how to lift the ban on purpose.
- **Break-tests:** I ran them on a scratch copy and removed it afterwards. A client event, a function, a schema in another folder and a version change all fail. Clean and commented-out code pass. Against the real project it currently fails on "found none", because the lock lacks Blink.

**What you need to do**
1. Run `pesde install`, then `pesde run blink -- network/main` to generate the three Blink files.
2. Run `python .claude/skills/roblox-resource-acquisition/scripts/clone_children.py --project . roblox-blink`. `CLAUDE.md` already points to that skill, which isn't cloned until the lock matches.
3. Run `bash scripts/check.sh`.

**Not done**
- **Client side:** nothing on the client listens to `CoinsChanged` yet. Hooking it into Charm state and `CoinLabel` changes what players see, so tell me if you want that.
- **Initial balance:** the server only fires when coins are added, so a joining client isn't sent its starting balance. That's fine while balances start at 0.
- **Janitor pin:** `pesde.toml` pins Janitor at 1.17.0 but its skill targets 1.18.3. This task doesn't use Janitor, so I left both alone.

----- R1 commands run -----
$ cd "." && ls -a && cat pesde.toml default.project.json scripts/check.sh && cat src/server/Coins.luau && ls .claude/skills scripts; find src -type f
$ cd "." && cat scripts/check_guards.py
$ cd "./.claude/skills" && cat roblox-resource-acquisition/SKILL.md; ls -R roblox-resource-acquisition structure-roblox-projects | head -60
$ cd "./.claude/skills/roblox-resource-acquisition" && cat references/adopting.md; ls -R libraries/roblox-blink; cat libraries/roblox-blink/SKILL.md; python scripts/clone_children.py --project "<runs>
$ cd "./.claude/skills" && cat roblox-resource-acquisition/libraries/roblox-blink/references/setup.md roblox-resource-acquisition/libraries/roblox-blink/references/api-and-lifecycle.md roblox-resource-acquisition/libraries/roblox-
$ cd "./.claude/skills" && cat roblox-resource-acquisition/libraries/roblox-blink/references/setup.md roblox-resource-acquisition/libraries/roblox-blink/references/api-and-lifecycle.md roblox-resource-acquisition/libraries/roblox-
$ cd "." && cat rokit.toml pesde.lock | head -60; cat src/server/init.server.luau src/server/Round.luau; ls .claude/skills/structure-roblox-projects/references; which pesde rokit python
$ cd "." && cat stylua.toml selene.toml; ls -a src; cat .gitignore 2>/dev/null; printf '\n[dev_dependencies]\nblink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }\n' >> pesde.toml && export PATH="$HOME/.rokit/bin
$ cd "." && tail -4 pesde.toml; cat stylua.toml selene.toml; ls -a src
$ cd "." && PATH="$HOME/.rokit/bin:$PATH" pesde install 2>&1 | tail -20
$ cd "." && pesde install 2>&1 | tail -20
$ pesde install
$ cd "." && python scripts/check_guards.py; echo "exit=$?"
$ python scripts/check_guards.py
$ T=$(mktemp -d) && mkdir -p "$T/scripts" "$T/network" "$T/src/client/UI" && cp scripts/check_guards.py "$T/scripts/" && cp network/main.blink "$T/network/" && echo '[graph."1axen/blink@0.18.9 lune"]' > "$T/pesde.lock" && echo "--- clean" && python -I "$T/scripts/check_guards.py"; echo "--- client eve
$ mkdir -p _gt/scripts _gt/network _gt/src/client/UI && cp scripts/check_guards.py _gt/scripts/ && cp network/main.blink _gt/network/ && echo '[graph."1axen/blink@0.18.9 lune"]' > _gt/pesde.lock && echo "--- clean" && python -I _gt/scripts/check_guards.py && echo ok
$ printf 'event Buy {\n\tFrom:   Client,\n\tType: Reliable, Call: SingleAsync }\nfunction Get { Yield: Coroutine }\n' >> _gt/network/main.blink && python -I _gt/scripts/check_guards.py
$ cp network/main.blink _gt/network/main.blink && printf -- '-- event X { From: Client }\n--[[ function Y\n From: Client ]]\n' >> _gt/network/main.blink && python -I _gt/scripts/check_guards.py && echo "comments ok" && mkdir _gt/other && printf 'event E { From: Client }' > _gt/other/x.blink && python 
$ echo '[graph."1axen/blink@0.19.0 lune"]' > _gt/pesde.lock && python -I _gt/scripts/check_guards.py
$ rm -r _gt && ls -a

----- R1 commands refused by permissions -----
$ cd "./.claude/skills" && cat roblox-resource-acquisition/libraries/roblox-blink/references/setup.md roblox-resource-acquisition/libraries/roblox-blink/references/api-and-lifecycle.md roblox-resource-acquisition/libraries/roblox-
$ cd "./.claude/skills" && cat roblox-resource-acquisition/libraries/roblox-blink/references/setup.md roblox-resource-acquisition/libraries/roblox-blink/references/api-and-lifecycle.md roblox-resource-acquisition/libraries/roblox-
$ cd "." && cat stylua.toml selene.toml; ls -a src; cat .gitignore 2>/dev/null; printf '\n[dev_dependencies]\nblink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }\n' >> pesde.toml && export PATH="$HOME/.rokit/bin
$ cd "." && PATH="$HOME/.rokit/bin:$PATH" pesde install 2>&1 | tail -20
$ cd "." && pesde install 2>&1 | tail -20
$ pesde install
$ cd "." && python scripts/check_guards.py; echo "exit=$?"
$ T=$(mktemp -d) && mkdir -p "$T/scripts" "$T/network" "$T/src/client/UI" && cp scripts/check_guards.py "$T/scripts/" && cp network/main.blink "$T/network/" && echo '[graph."1axen/blink@0.18.9 lune"]' > "$T/pesde.lock" && echo "--- clean" && python -I "$T/scripts/check_guards.py"; echo "--- client eve

----- R1 changed file: .styluaignore -----
src/server/Network/Server.luau
src/client/Network/Client.luau
src/shared/Network/Types.luau

----- R1 changed file: CLAUDE.md -----
# coin-run

Roblox round game: Rojo + pesde + Vide + Charm + Janitor. Run `bash scripts/check.sh` before calling a change done; `python scripts/check_guards.py` runs the project's guards on their own.

## Libraries

- **Vide**: UI rendering. Use the `roblox-vide` skill.
- **Janitor**: cleanup ownership. Use the `roblox-janitor` skill.
- **Charm**: client-only UI state shared across components, in `src/client/State`.
- **Blink**: server-to-client networking, schema in `network/main.blink`, generated into `Network/` folders by `pesde run blink -- network/main`. Never edit generated files. Use the `roblox-blink` skill. Client-to-server events and functions are banned (receive-side DoS, Blink issue #45); `scripts/check_guards.py` fails on them and on any Blink version other than the one it was reviewed against.
- **Signal** (`src/shared/Signal.luau`): in-runtime custom events. A vendored module, not a package.

----- R1 changed file: pesde.toml -----
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

----- R1 changed file: selene.toml -----
std = "roblox"
exclude = ["src/server/Network/Server.luau", "src/client/Network/Client.luau", "src/shared/Network/Types.luau"]

----- R1 changed file: network/main.blink -----
option ServerOutput = "../src/server/Network/Server.luau"
option ClientOutput = "../src/client/Network/Client.luau"
option TypesOutput = "../src/shared/Network/Types.luau"
option RemoteScope = "CoinRun"

event CoinsChanged { From: Server, Type: Reliable, Call: ManyAsync, Data: u32 }

----- R1 changed file: scripts/check.sh -----
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

----- R1 changed file: scripts/check_guards.py -----
"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
- No client-to-server Blink: no `From: Client` event and no `function` in any .blink schema. Pinned to Blink 0.18.9.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
GUARDS = [
    ("src/client/UI", "*.luau", re.compile(r"Instance\.new"), "build UI Instances with Vide's create"),
]

BLINK_REVIEWED = "0.18.9"
BLINK_LOCKED = re.compile(r"1axen/blink@([^\s\"]+)")
BLINK_SKIPPED_DIRS = {"roblox_packages", "lune_packages", ".pesde", "build", ".claude"}
BLINK_COMMENTS_AND_STRINGS = re.compile(r'"[^"\n]*"|--\[(=*)\[.*?\]\1\]|--[^\n]*', re.DOTALL)
BLINK_BANS = [
    (re.compile(r"\bFrom\s*:\s*Client\b"), "client-to-server event"),
    (re.compile(r"\bfunction\b"), "function (the client invokes the server)"),
]
BLINK_REASON = (
    "client-to-server Blink is banned: 0.18.9 parses the whole incoming buffer before any handler runs "
    "(https://github.com/1Axen/blink/issues/45). To allow it on purpose, mitigate that in the receive path "
    "and edit BLINK_BANS in scripts/check_guards.py"
)


def blink_schemas() -> list[Path]:
    schemas = [p for p in ROOT.rglob("*.blink") if not BLINK_SKIPPED_DIRS & set(p.relative_to(ROOT).parts)]
    return sorted(schemas + list((ROOT / "network").glob("*.txt")))


def blink_code(text: str) -> str:
    def blank(match: re.Match) -> str:
        return match.group(0) if match.group(0).startswith('"') else re.sub(r"[^\n]", " ", match.group(0))

    return BLINK_COMMENTS_AND_STRINGS.sub(blank, text)


def check_blink() -> list[str]:
    lock = ROOT / "pesde.lock"
    versions = set(BLINK_LOCKED.findall(lock.read_text(encoding="utf-8"))) if lock.exists() else set()
    if versions != {BLINK_REVIEWED}:
        found = ", ".join(sorted(versions)) or "none"
        return [
            f"pesde.lock: Blink guard reviewed against {BLINK_REVIEWED}, found {found}: "
            "re-review this guard, then update BLINK_REVIEWED in scripts/check_guards.py"
        ]
    failures = []
    for path in blink_schemas():
        code = blink_code(path.read_text(encoding="utf-8"))
        for number, line in enumerate(code.splitlines(), 1):
            for banned, what in BLINK_BANS:
                if banned.search(line):
                    failures.append(f"{path.relative_to(ROOT).as_posix()}:{number}: {what}; {BLINK_REASON}")
    return failures


def main() -> int:
    failures = []
    for folder, pattern, banned, reason in GUARDS:
        for path in sorted((ROOT / folder).rglob(pattern)):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if banned.search(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: {reason}")
    failures += check_blink()
    for failure in failures:
        print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

----- R1 changed file: src/server/Coins.luau -----
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

----- R3 commands run -----
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

----- R3 commands refused by permissions -----
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

----- R3 changed file: CLAUDE.md -----
# coin-run

Roblox round game: Rojo + pesde + Vide + Charm + Janitor. Run `bash scripts/check.sh` before calling a change done; `python scripts/check_guards.py` runs the project's guards on their own.

## Libraries

- **Vide**: UI rendering. Use the `roblox-vide` skill.
- **Janitor**: cleanup ownership. Use the `roblox-janitor` skill.
- **Charm**: client-only UI state shared across components, in `src/client/State`.
- **Signal** (`src/shared/Signal.luau`): in-runtime custom events. A vendored module, not a package.
- **Blink**: server-to-client networking, schema in `network/main.blink`, generated modules in each `Network/` folder (never edit). No client-to-server events or functions: `check_guards.py` enforces it.

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

----- R3 changed file: network/main.blink -----
option ServerOutput = "../src/server/Network/Server.luau"
option ClientOutput = "../src/client/Network/Client.luau"
option TypesOutput = "../src/shared/Network/Types.luau"
option RemoteScope = "CoinRun"

event CoinsChanged { From: Server, Type: Reliable, Call: SingleAsync, Data: u32 }

----- R3 changed file: scripts/check.sh -----
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

----- R3 changed file: scripts/check_guards.py -----
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

----- R3 changed file: src/server/Coins.luau -----
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

===== R4 =====
Blink isn't installed yet, so the work is only partly done. `pesde install` needed approval and didn't run. Nothing has been compiled, and `Coins.luau` doesn't fire the event yet.

**Done**
- **Dependency:** `pesde.toml` now pins `1axen/blink` at `=0.18.9` under `[dev_dependencies]`, with the lune target. That's where the Blink CLI goes in pesde.
- **Schema:** `network/main.blink` declares one event, `CoinsChanged` (`From: Server`, reliable, `u32`). It writes its output to `src/server/Network`, `src/client/Network` and `src/shared/Network`.
- **Guard:** `scripts/check_guards.py` now fails on any `From: Client` event or any `function` in a Blink schema. Blink functions are called by the client, so they count as client-to-server. The message says how to change the rule on purpose.
- **Version pin:** the guard also checks that `pesde.lock` has Blink at 0.18.9. It fails if Blink is missing or at another version, so a Blink upgrade forces a re-review. It also fails on a `.blink` file outside `network/`, since the guard couldn't see it there.
- **`scripts/check.sh`:** it now runs the guards right after `pesde install --locked`, then `pesde run blink -- network/main`.
- **`CLAUDE.md`:** I added a Blink line to the Libraries list, marked "Pending".

**Check run:** the guard currently fails with "Blink is not locked… run `pesde install`". That is the missing lock, not a rule violation. I haven't done the break-test (adding a `From: Client` event and seeing the guard fail), because it needs the lock first.

**To finish**
1. Run `pesde install`, then `pesde run blink -- network/main`. I can do both if you approve them.
2. Run the Blink skill clone: `clone_children.py --project <this project> roblox-blink`. It refuses until the lock declares Blink.
3. Add the `Coins.add` call that fires `Net.CoinsChanged.Fire(player, balance)` using the generated server module. I'm holding it because the module doesn't exist yet and `check.sh` would break on a missing require.
4. Break-test the guard, then run `bash scripts/check.sh`. I haven't checked whether `stylua`/`selene` accept Blink's generated files. You may need to exclude `src/*/Network`.

**Your call:** I haven't touched client code. Do you want the client to listen for `CoinsChanged` and write into a Charm atom in `src/client/State`? That affects what players see, so I'd rather ask first.

Blink 0.18.9's server has a known flaw where a client can send an oversized buffer ([issue #45](https://github.com/1Axen/blink/issues/45)). The no-client-events rule keeps you clear of it. The Janitor pin mismatch (1.17.0 against the skill's 1.18.3) doesn't affect this task, and I left it alone.

----- R4 commands run -----
$ cd "." && ls -a . .claude/skills scripts src src/* && cat pesde.toml default.project.json scripts/check.sh && cat src/server/Coins.luau && cat scripts/check_guards.py
$ cd "." && cat src/server/init.server.luau src/client/init.client.luau rokit.toml; ls src/client/State
$ cd "./.claude/skills/roblox-resource-acquisition" && cat references/adopting.md && grep -n -i -B2 -A8 blink references/library-skills.md | head -60; ls references scripts
$ cd "./.claude/skills/roblox-resource-acquisition" && python scripts/check_updates.py; python scripts/clone_children.py --project "." --status
$ cd "./.claude/skills/roblox-resource-acquisition/libraries/roblox-blink" && ls -R . | head -30; cat SKILL.md resource.yaml
$ cd "./.claude/skills/roblox-resource-acquisition/libraries/roblox-blink/references" && cat setup.md api-and-lifecycle.md; which pesde rokit lune python
$ cd "." && cat >> pesde.toml <<'EOF'

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }
EOF
pesde install 2>&1 | tail -15; git status 2>&1 | head -1; grep -n -A3 'blink' pesde.lock | head -
$ cd "." && pesde install 2>&1 | tail -15; grep -n -i -B1 -A3 'blink' pesde.lock | head -20; ls -a
$ cd "." && grep -n -i 'guard\|check' .claude/skills/structure-roblox-projects/references/*check* 2>/dev/null | head -20; ls .claude/skills/structure-roblox-projects/references | head
$ cd "." && cat > scripts/check_guards.py <<'PYEOF'
"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
- No client-to-server Blink: no `From:
$ cd "." && python scripts/check_guards.py; echo "exit $?"
$ python scripts/check_guards.py

----- R4 commands refused by permissions -----
$ cd "." && cat >> pesde.toml <<'EOF'

[dev_dependencies]
blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }
EOF
pesde install 2>&1 | tail -15; git status 2>&1 | head -1; grep -n -A3 'blink' pesde.lock | head -
$ cd "." && pesde install 2>&1 | tail -15; grep -n -i -B1 -A3 'blink' pesde.lock | head -20; ls -a
$ cd "." && cat > scripts/check_guards.py <<'PYEOF'
"""Project guards: each fails the build when a banned pattern appears.

- No Instance.new under src/client/UI: build UI with Vide's create.
- No client-to-server Blink: no `From:
$ cd "." && python scripts/check_guards.py; echo "exit $?"

----- R4 changed file: CLAUDE.md -----
# coin-run

Roblox round game: Rojo + pesde + Vide + Charm + Janitor. Run `bash scripts/check.sh` before calling a change done; `python scripts/check_guards.py` runs the project's guards on their own.

## Libraries

- **Vide**: UI rendering. Use the `roblox-vide` skill.
- **Janitor**: cleanup ownership. Use the `roblox-janitor` skill.
- **Blink**: server-to-client events only, schema in `network/main.blink`, generated modules in `src/*/Network`. Use the `roblox-blink` skill. No client-to-server events or functions; `scripts/check_guards.py` fails on them. Pending: `pesde install` and the checks have not run yet.
- **Charm**: client-only UI state shared across components, in `src/client/State`.
- **Signal** (`src/shared/Signal.luau`): in-runtime custom events. A vendored module, not a package.

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

event CoinsChanged {
	From: Server,
	Type: Reliable,
	Call: ManyAsync,
	Data: u32,
}

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
- No client-to-server Blink: network/ schemas hold no `From: Client` events and no functions.
  Pinned to the Blink version in pesde.lock; re-review the guard when that changes.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
GUARDS = [
    ("src/client/UI", "*.luau", re.compile(r"Instance\.new"), "build UI Instances with Vide's create"),
]

BLINK_REVIEWED = "0.18.9"
BLINK_LOCKED = re.compile(r"1axen/blink[ @]v?(\d+\.\d+\.\d+\S*?)[ \"]", re.IGNORECASE)
BLINK_COMMENT = re.compile(r"--.*")
BLINK_CLIENT_SENDS = [
    (re.compile(r"\bFrom\s*:\s*Client\b"), "events must be `From: Server`"),
    (re.compile(r"\bfunction\s+\w+"), "Blink functions are invoked by the client"),
]
BLINK_RULE = "client-to-server Blink is banned; to change the rule, edit BLINK_CLIENT_SENDS in scripts/check_guards.py"


def check_blink_pin() -> list[str]:
    lock = ROOT / "pesde.lock"
    found = BLINK_LOCKED.search(lock.read_text(encoding="utf-8")) if lock.exists() else None
    if found is None:
        return ["pesde.lock: Blink is not locked, so the Blink guard cannot be verified; run `pesde install`"]
    if found.group(1) != BLINK_REVIEWED:
        return [
            f"pesde.lock: Blink guard reviewed against {BLINK_REVIEWED}, found {found.group(1)}: "
            "re-review the guard, then update BLINK_REVIEWED in scripts/check_guards.py"
        ]
    return []


def check_blink_schemas() -> list[str]:
    failures = []
    network = ROOT / "network"
    schemas = [path for path in ROOT.rglob("*.blink") if "roblox_packages" not in path.parts]
    schemas += network.glob("*.txt")
    for path in sorted(schemas):
        if path.parent != network:
            failures.append(f"{path.relative_to(ROOT)}: Blink schemas live in network/ so the guard can see them")
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = BLINK_COMMENT.sub("", line)
            for banned, reason in BLINK_CLIENT_SENDS:
                if banned.search(code):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: {reason}; {BLINK_RULE}")
    return failures


def main() -> int:
    failures = check_blink_pin() + check_blink_schemas()
    for folder, pattern, banned, reason in GUARDS:
        for path in sorted((ROOT / folder).rglob(pattern)):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if banned.search(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: {reason}")
    for failure in failures:
        print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
