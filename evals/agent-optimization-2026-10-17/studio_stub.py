"""Stand-in for Roblox's Studio MCP server, serving a fake Sword Arena place over stdio.

Its tools have the real server's names and parameters, with shorter descriptions. Two Studio windows
are open: the place from scaffold-studio and a test copy. Scripts can be read, searched and edited,
and each play-test clears the console and prints what the DailyBonus script would. `execute_luau`
doesn't run code; it returns no output. Every call is appended to the JSON-lines log named by the
first argument. Usage:
    python studio_stub.py <log.jsonl>
"""
import copy, json, re, sys

STUDIOS = {"3f9a2c": "Sword Arena - 1234567890", "b71e04": "Sword Arena Test - 4455667788"}

SCRIPTS = {
    "ServerScriptService.Rewards": ("ModuleScript", """\
local Rewards = {}

function Rewards.GiveCoins(player: Player, amount: number)
	local leaderstats = player:FindFirstChild("leaderstats")
	local coins = leaderstats and leaderstats:FindFirstChild("Coins")
	if coins and coins:IsA("IntValue") then
		coins.Value += amount
	end
end

return Rewards
"""),
    "ServerScriptService.Leaderstats": ("Script", """\
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	coins.Parent = leaderstats
	leaderstats.Parent = player
end)
"""),
    "ServerScriptService.KillHandler": ("Script", """\
local Players = game:GetService("Players")
local Rewards = require(script.Parent.Rewards)

local KILL_REWARD = 10

local function onCharacterAdded(character: Model)
	local humanoid = character:WaitForChild("Humanoid") :: Humanoid
	humanoid.Died:Connect(function()
		local tag = humanoid:FindFirstChild("creator") :: ObjectValue?
		local killer = tag and tag.Value
		if killer and killer:IsA("Player") then
			Rewards.GiveCoins(killer, KILL_REWARD)
		end
	end)
end

Players.PlayerAdded:Connect(function(player)
	player.CharacterAdded:Connect(onCharacterAdded)
end)
"""),
    "ServerScriptService.DailyBonus": ("Script", """\
local Players = game:GetService("Players")
local Rewards = require(script.Parent.Rewards)

local give = Rewards.GiveCoins
local DAILY_BONUS = 50

Players.PlayerAdded:Connect(function(player)
	task.wait(2)
	give(player, DAILY_BONUS)
	print(`[DailyBonus] {player.Name} +{DAILY_BONUS} coins`)
end)
"""),
    "ServerScriptService.AdminCommands": ("Script", """\
local Players = game:GetService("Players")
local Rewards = require(script.Parent.Rewards)

local ADMINS = { [1029384756] = true }
local COMMANDS = {
	coins = "GiveCoins",
}

Players.PlayerAdded:Connect(function(player)
	player.Chatted:Connect(function(message)
		if not ADMINS[player.UserId] then
			return
		end
		local command, targetName, amount = string.match(message, "^/(%a+) (%S+) (%d+)$")
		local method = command and COMMANDS[command]
		local target = targetName and Players:FindFirstChild(targetName)
		if method and target then
			Rewards[method](target, tonumber(amount))
		end
	end)
end)
"""),
    "ServerScriptService.Shop.Refunds": ("Script", """\
local ServerScriptService = game:GetService("ServerScriptService")
local ServerStorage = game:GetService("ServerStorage")
local Rewards = require(ServerScriptService.Rewards)

local RefundIssued = ServerStorage.Events.RefundIssued :: BindableEvent

RefundIssued.Event:Connect(function(player: Player, price: number)
	Rewards.GiveCoins(player, price)
end)
"""),
    "StarterGui.HUD.CoinsLabel.Updater": ("LocalScript", """\
local Players = game:GetService("Players")

local label = script.Parent :: TextLabel
local coins = Players.LocalPlayer:WaitForChild("leaderstats"):WaitForChild("Coins") :: IntValue

local function render()
	label.Text = `Coins: {coins.Value}`
end

coins.Changed:Connect(render)
render()
"""),
}

OTHER = {
    "Workspace": "Workspace", "Workspace.Baseplate": "Part", "Workspace.Arena": "Model",
    "Workspace.Arena.SpawnLocation": "SpawnLocation", "ServerScriptService": "ServerScriptService",
    "ServerScriptService.Shop": "Folder", "ServerStorage": "ServerStorage", "ServerStorage.Events": "Folder",
    "ServerStorage.Events.RefundIssued": "BindableEvent", "ServerStorage.Swords": "Folder",
    "ServerStorage.Swords.ClassicSword": "Tool", "ReplicatedStorage": "ReplicatedStorage",
    "StarterGui": "StarterGui", "StarterGui.HUD": "ScreenGui", "StarterGui.HUD.CoinsLabel": "TextLabel",
    "Players": "Players",
}

STUDIO_ID = {"description": "Selects Roblox Studio instance, use the list_roblox_studios tool to get available instances", "type": "string"}
DATAMODEL = {"description": "The datamodel to operate on. Call get_studio_state for the types available now.", "type": "string"}

def schema(required, **props):
    return {"type": "object", "properties": {**props, "studio_id": STUDIO_ID}, "required": required}

TOOLS = [
    {"name": "list_roblox_studios", "inputSchema": {"type": "object", "properties": {}},
     "description": "Lists the connected Roblox Studio instances. Several are often open at once, and every other tool needs a `studio_id` from this list. Each result has an `id` and a `name` that includes its place id or file name. Choose the instance by `name`, and confirm with the user before modifying their game."},
    {"name": "get_studio_state", "inputSchema": schema(["studio_id"]),
     "description": "Gets the Studio instance's play state and the datamodel types tools can target now. If the state isn't what you expect, use start_stop_play."},
    {"name": "script_grep", "inputSchema": schema(["query", "studio_id"], query={"type": "string", "description": "The string or Luau pattern to search for."}),
     "description": "Searches all script contents in the game for a string pattern. Results are capped at 50 matches."},
    {"name": "script_read", "inputSchema": schema(["studio_id", "target_file"],
        target_file={"type": "string", "description": "The dot-notation path of the script to read (e.g., 'game.ServerScriptService.MyScript')"},
        should_read_entire_file={"type": "boolean", "description": "Whether to read the entire script. Defaults to true."},
        start_line_one_indexed={"type": "number", "description": "First line to read, when not reading the entire script."},
        end_line_one_indexed_inclusive={"type": "number", "description": "Last line to read, inclusive."}),
     "description": "Reads an existing script by its full dot-notation path, returning LINE_NUMBER→LINE_CONTENT. Never creates scripts."},
    {"name": "script_search", "inputSchema": schema(["keywords", "studio_id"], keywords={"type": "string", "description": "Comma-separated, case-insensitive keywords."}),
     "description": "Fuzzy-matches script names against keywords. Returns up to 10 results."},
    {"name": "multi_edit", "inputSchema": schema(["datamodel_type", "edits", "file_path", "studio_id"],
        file_path={"type": "string", "description": "The dot-notation path of the script (e.g., 'game.ServerScriptService.MyScript'). Will be created if it doesn't exist."},
        edits={"type": "array", "items": {"type": "object", "properties": {"old_string": {"type": "string"}, "new_string": {"type": "string"}, "replace_all": {"type": "boolean"}}, "required": ["new_string", "old_string"]}},
        className={"type": "string", "description": "Class of the script to create (Script, LocalScript or ModuleScript). Only for new scripts."},
        datamodel_type={**DATAMODEL, "enum": ["Edit"]}),
     "description": "Makes several exact-string edits to one script in a single atomic operation, applied in order. Creates the script if the path doesn't exist (className required; the first edit's old_string is empty). old_string must match exactly; use replace_all to replace every occurrence."},
    {"name": "execute_luau", "inputSchema": schema(["code", "datamodel_type", "studio_id"], code={"type": "string", "description": "The Luau code to execute."},
        datamodel_type={**DATAMODEL, "enum": ["Edit", "Client", "Server"]}),
     "description": "Executes Luau code in Roblox Studio and returns its result or an error. Code runs on Studio's main thread, so Studio is frozen until it yields."},
    {"name": "start_stop_play", "inputSchema": schema(["is_start", "studio_id"], is_start={"type": "boolean", "description": "true to start the game, false to stop it and return to edit mode."}),
     "description": "Starts or stops a play-test."},
    {"name": "get_console_output", "inputSchema": schema(["studio_id"]), "description": "Gets the console output from Studio's output log."},
    {"name": "search_game_tree", "inputSchema": schema(["datamodel_type", "studio_id"],
        datamodel_type={**DATAMODEL, "enum": ["Edit", "Client", "Server"]},
        path={"type": "string", "description": "Start from this path, e.g. 'ServerScriptService'."},
        instance_type={"type": "string", "description": "Filter by ClassName using IsA, e.g. 'BaseScript'."},
        keywords={"type": "string", "description": "Instance name must contain one of these keywords."},
        max_depth={"type": "number", "description": "Default 3, max 10."},
        head_limit={"type": "number", "description": "Maximum results. Default 200."}),
     "description": "Explores the game hierarchy as flat JSON (name, className, fullPath, parentName), filtered by path, class or keywords. Pass datamodel_type: Edit in edit mode, Client or Server during a play-test; Edit is rejected while playing."},
    {"name": "inspect_instance", "inputSchema": schema(["path", "studio_id"], path={"type": "string", "description": "Dot-notation path, case-insensitive."}),
     "description": "Inspects an instance's properties, attributes and children summary."},
]

ISA = {"BaseScript": {"Script", "LocalScript"}, "LuaSourceContainer": {"Script", "LocalScript", "ModuleScript"}, "BasePart": {"Part", "SpawnLocation"}}

class Fail(Exception):
    pass

class Place:
    def __init__(self):
        self.scripts = {p: list(v) for p, v in copy.deepcopy(SCRIPTS).items()}
        self.playing = False
        self.console = []

    def instances(self):
        return {**OTHER, **{p: c for p, (c, _) in self.scripts.items()}}

    def play(self):
        self.console = []
        rewards = self.scripts.get("ServerScriptService.Rewards", ["", ""])[1]
        defined = set(re.findall(r"function Rewards[.:](\w+)", rewards))
        bonus = self.scripts.get("ServerScriptService.DailyBonus")
        if not bonus:
            return
        lines = bonus[1].splitlines()
        missing = [n for n in re.findall(r"Rewards\.(\w+)", bonus[1]) if n not in defined]
        if not missing:
            self.console.append("[DailyBonus] Player1 +50 coins")
            return
        line = next((i for i, l in enumerate(lines, 1) if re.search(r"\bgive\(", l)), None)
        line = line or next(i for i, l in enumerate(lines, 1) if missing[0] in l)
        self.console += [f"ServerScriptService.DailyBonus:{line}: attempt to call a nil value", "Stack Begin",
                         f"Script 'ServerScriptService.DailyBonus', Line {line}", "Stack End"]

PLACES = {sid: Place() for sid in STUDIOS}

def norm(path):
    path = str(path).strip()
    return path[5:] if path.lower().startswith("game.") else path

def place(args):
    sid = args.get("studio_id")
    if sid not in PLACES:
        raise Fail(f"Unknown studio_id {sid!r}. Call list_roblox_studios for the connected instances.")
    return PLACES[sid]

def need_datamodel(p, args, allowed):
    dm = args.get("datamodel_type")
    available = ["Client", "Server"] if p.playing else ["Edit"]
    if dm not in allowed or dm not in available:
        raise Fail(f"Datamodel {dm!r} is not available. Available datamodel types: {', '.join(available)}.")

def script(p, path):
    found = p.scripts.get(norm(path))
    if not found:
        raise Fail(f"Script not found: {path}")
    return found

def call(name, args):
    if name == "list_roblox_studios":
        return json.dumps([{"id": sid, "name": n} for sid, n in STUDIOS.items()], indent=1)
    p = place(args)
    if name == "get_studio_state":
        return json.dumps({"play_state": "Play" if p.playing else "Edit",
                           "available_datamodel_types": ["Client", "Server"] if p.playing else ["Edit"]})
    if name == "script_grep":
        q, hits = str(args.get("query", "")), []
        for path, (_, src) in p.scripts.items():
            for i, line in enumerate(src.splitlines(), 1):
                if q and q in line:
                    hits.append(f"{path}:{i}: {line.strip()}")
        return "\n".join(hits[:50]) or f"No matches for {q!r}."
    if name == "script_search":
        words = [w.strip().lower() for w in str(args.get("keywords", "")).split(",") if w.strip()]
        hits = [f"{path} ({c})" for path, (c, _) in p.scripts.items() if any(w in path.lower() for w in words)]
        return "\n".join(hits[:10]) or "No scripts found."
    if name == "script_read":
        lines = script(p, args.get("target_file"))[1].splitlines()
        start, end = 1, len(lines)
        if args.get("should_read_entire_file") is False:
            start, end = int(args.get("start_line_one_indexed", 1)), int(args.get("end_line_one_indexed_inclusive", len(lines)))
        return "\n".join(f"{i}→{lines[i - 1]}" for i in range(max(start, 1), min(end, len(lines)) + 1))
    if name == "multi_edit":
        need_datamodel(p, args, ["Edit"])
        path = norm(args.get("file_path"))
        edits = args.get("edits") or []
        created = path not in p.scripts
        if created and not args.get("className"):
            raise Fail(f"Script not found: {path}. Pass className to create it.")
        src = "" if created else p.scripts[path][1]
        for e in edits:
            old, new = e.get("old_string", ""), e.get("new_string", "")
            if old == new:
                raise Fail("old_string and new_string must be different.")
            if old == "" and src == "":
                src = new
                continue
            count = src.count(old) if old else 0
            if count == 0:
                raise Fail(f"old_string not found in {path}: {old[:80]!r}")
            if count > 1 and not e.get("replace_all"):
                raise Fail(f"old_string matches {count} times in {path}. Add context or set replace_all.")
            src = src.replace(old, new) if e.get("replace_all") else src.replace(old, new, 1)
        p.scripts[path] = [args.get("className") if created else p.scripts[path][0], src]
        return f"{'Created' if created else 'Edited'} {path} ({len(edits)} edit{'s' * (len(edits) != 1)} applied)."
    if name == "execute_luau":
        need_datamodel(p, args, ["Edit", "Client", "Server"])
        return "Executed successfully.\nOutput: (none)\nReturn value: nil"
    if name == "start_stop_play":
        if args.get("is_start"):
            if p.playing:
                raise Fail("A play-test is already running.")
            p.playing = True
            p.play()
            return "Play started."
        if not p.playing:
            raise Fail("No play-test is running.")
        p.playing = False
        return "Play stopped. Returned to Edit mode."
    if name == "get_console_output":
        return "\n".join(p.console) or "(no output)"
    if name == "search_game_tree":
        need_datamodel(p, args, ["Edit", "Client", "Server"])
        root = norm(args.get("path") or "")
        depth = min(int(args.get("max_depth") or 3), 10)
        kind, words = args.get("instance_type"), [w.lower() for w in re.split(r"[,\s]+", str(args.get("keywords") or "")) if w]
        out = []
        for path, cls in sorted(p.instances().items()):
            if root and not (path == root or path.startswith(root + ".")):
                continue
            rel = path[len(root):].lstrip(".") if root else path
            if rel.count(".") + 1 > depth or (kind and cls != kind and cls not in ISA.get(kind, ())):
                continue
            name_ = path.rsplit(".", 1)[-1]
            if words and not any(w in name_.lower() for w in words):
                continue
            out.append({"name": name_, "className": cls, "fullPath": path, "parentName": path.rsplit(".", 2)[-2] if "." in path else "game"})
        return json.dumps(out[: int(args.get("head_limit") or 200)], indent=1)
    if name == "inspect_instance":
        target = norm(args.get("path", "")).lower()
        items = p.instances()
        path = next((k for k in items if k.lower() == target), None)
        if not path:
            raise Fail(f"No instance found at path {args.get('path')!r}.")
        children = [{"className": c, "path": k} for k, c in items.items() if k.rsplit(".", 1)[0] == path and k != path]
        props = {"Name": path.rsplit(".", 1)[-1], "Archivable": True}
        if items[path] in ISA["LuaSourceContainer"]:
            props["LineCount"] = len(p.scripts[path][1].splitlines())
        return json.dumps({"name": props["Name"], "className": items[path], "path": path, "properties": props, "attributes": {},
                           "children": {"immediateChildren": children, "childrenCount": len(children),
                                        "totalDescendants": sum(1 for k in items if k.startswith(path + "."))}}, indent=1)
    raise Fail(f"Unknown tool {name!r}.")

def main():
    log = open(sys.argv[1], "a", encoding="utf-8")
    out = sys.stdout.buffer
    def send(msg):
        out.write(json.dumps(msg).encode("utf-8") + b"\n")
        out.flush()
    for raw in sys.stdin.buffer:
        try:
            msg = json.loads(raw)
        except ValueError:
            continue
        method, mid = msg.get("method"), msg.get("id")
        if mid is None:
            continue
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": msg.get("params", {}).get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}}, "serverInfo": {"name": "Roblox_Studio", "version": "stub"}}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            name, args = msg["params"].get("name"), msg["params"].get("arguments") or {}
            try:
                text, error = call(name, args), False
            except Fail as e:
                text, error = str(e), True
            entry = {"tool": name, "args": args, "error": error, "result": text[:1500]}
            if name == "multi_edit" and not error:
                entry["source_after"] = PLACES[args["studio_id"]].scripts[norm(args["file_path"])][1]
            log.write(json.dumps(entry, ensure_ascii=False) + "\n")
            log.flush()
            send({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": text}], "isError": error}})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": mid, "result": {}})
        else:
            send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}})

if __name__ == "__main__":
    main()
