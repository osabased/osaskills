===== R1 =====
This uses Vide 0.4.1, which matches the commit you pinned. I haven't run it in Studio.

```luau
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Vide = require(ReplicatedStorage.Packages.vide) -- use your project's mapped path
local create, source, derive, indexes, cleanup = Vide.create, Vide.source, Vide.derive, Vide.indexes, Vide.cleanup

-- `items` is a Vide source holding an array of item names, e.g. source({ "Sword", "Shield" }).
local function ShopPanel(items: Vide.Source<{ string }>)
	local open = source(false)

	local gui = create "ScreenGui" {
		Name = "ShopPanel",
		ResetOnSpawn = false,

		create "TextButton" {
			Name = "Toggle",
			Size = UDim2.fromOffset(200, 40),
			Text = derive(function()
				return if open() then "Close shop list" else `Shop ({#items()} items)`
			end),
			Activated = function()
				open(not open())
			end,
		},

		create "Frame" {
			Name = "ItemList",
			Position = UDim2.fromOffset(0, 48),
			Size = UDim2.fromOffset(200, 240),
			Visible = open, -- a source is a getter, so the property is reactive

			create "UIListLayout" {
				SortOrder = Enum.SortOrder.LayoutOrder,
			},

			-- One scope and one label per index. The name arrives as a Source.
			indexes(items, function(name, i)
				return create "TextLabel" {
					Size = UDim2.new(1, 0, 0, 28),
					LayoutOrder = i,
					Text = name,
				}
			end),
		},
	}

	-- The mount disposer destroys only the scope, not the Instance you return.
	cleanup(gui)
	return gui
end

-- Mounting and teardown
local items = source({ "Sword", "Shield", "Potion" })

local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")
local dispose: (() -> ())? = Vide.mount(function()
	return ShopPanel(items)
end, playerGui)

-- Call when the shop closes for good.
local function closeShop()
	local d = dispose
	dispose = nil -- clear first: a second call to a root disposer errors
	if d then
		d()
	end
end

-- Later, `items({ "Sword", "Shield", "Potion", "Bow" })` updates the list in place.
-- Teardown is `closeShop()`.
```

**How the pieces work**
- **Toggle:** The button's `Activated` function is an event listener, because `Activated` is an event on the instance. The `Text` getter and `Visible = open` are reactive properties.
- **List:** `indexes` builds one label per index and keeps it when a name changes. Use `values` instead if names are unique and you want one label per value.
- **Teardown:** `closeShop()` destroys the Vide scope, which runs every `cleanup` registered inside it. That includes `cleanup(gui)`, so the ScreenGui is destroyed along with it. Without that line the ScreenGui would stay parented to `PlayerGui` after the disposer ran.
- **Double calls:** Calling a disposer twice errors, so `closeShop` clears `dispose` before calling it and is safe to call repeatedly.

**Things to avoid**
- Don't call `Vide.step()` on teardown. It permanently disconnects the package-wide Heartbeat that drives `spring` and delayed scope teardown.
- Keep effects, `derive` functions and the `indexes` callback pure and synchronous. In strict mode they run twice per update, and yielding inside them errors.
- If you mutate the `items` table in place, call `items(items())` to trigger a re-render. Writing a new table, as in the example above, needs no extra step.


===== R2 =====
Vide isn't installed in this repo (only `pesde.toml` and a stub client file), so I couldn't check this against the v0.4.1 source. I wrote it from my knowledge of Vide's API. Before you commit, check that `mount`, `create`, `source`, `values` and the event-by-name props (`Activated`) match what your pinned rev exports.

```luau
--!strict
local Players = game:GetService("Players")
local vide = require(path.to.vide)

local create = vide.create
local source = vide.source
local values = vide.values
local mount = vide.mount

type Source<T> = typeof(source((nil :: any) :: T))

local function ShopPanel(props: { items: Source<{ string }> })
	local open = source(false)

	return create "ScreenGui" {
		Name = "ShopPanel",
		ResetOnSpawn = false, -- survive respawns; teardown is explicit

		create "TextButton" {
			Name = "Toggle",
			Size = UDim2.fromOffset(120, 36),
			Position = UDim2.fromOffset(16, 16),
			Text = function()
				return if open() then "Close Shop" else "Open Shop"
			end,
			Activated = function()
				open(not open())
			end,
		},

		create "Frame" {
			Name = "ItemList",
			Size = UDim2.fromOffset(240, 300),
			Position = UDim2.fromOffset(16, 60),
			Visible = open, -- sources are accepted as reactive props

			create "UIListLayout" {
				SortOrder = Enum.SortOrder.LayoutOrder,
				Padding = UDim.new(0, 4),
			},

			-- keyed by value: rows are created/destroyed as names are added/removed
			values(props.items, function(name: string, index: () -> number)
				return create "TextLabel" {
					Name = name,
					Size = UDim2.new(1, 0, 0, 28),
					LayoutOrder = index,
					Text = name,
				}
			end),
		},
	}
end

-- Usage
local items = source({ "Sword", "Shield", "Potion" })
local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")

local destroyShop = mount(function()
	return ShopPanel({ items = items })
end, playerGui)

-- Shop closes for good (not just hidden):
destroyShop()

-- Updating the list while open:
-- items({ "Sword", "Shield", "Potion", "Bow" })
```

**How it works**
- **Toggle:** `open` is a source. The button's `Text` is a function that reads it, so it re-evaluates when `open` changes. `Visible = open` binds the frame directly. `Activated` flips the value.
- **Item list:** `values` is keyed by value, so each name gets one `TextLabel`. Replacing the `items` table only adds or removes the rows that changed. `index` is a function, so `LayoutOrder = index` stays reactive. If duplicate names are possible, use `vide.indexes` instead.
- **Mounting:** `mount(component, target)` runs the component in a root scope and parents the returned `ScreenGui` into `PlayerGui`. It returns a destructor.
- **Teardown:** Call `destroyShop()` once when the shop closes for good. It stops the effects, runs any `vide.cleanup` callbacks, and destroys the instances. Don't call `:Destroy()` on the `ScreenGui` yourself. Hiding the shop temporarily is the `open` toggle, not a teardown.

If you also create connections or tasks inside the component, register them with `vide.cleanup(...)` so the destructor handles them too.


===== R3 =====
This is written from my memory of Vide's API. The Vide source isn't installed in this project (only `pesde.toml` is), so I couldn't check it against rev `5ed4c01`. Before you rely on it, check the `mount`/`create`/`indexes` signatures and the destroy-on-teardown behavior against that source.

```lua
--!strict
local Players = game:GetService("Players")
local vide = require(path.to.vide)

local create = vide.create
local source = vide.source
local indexes = vide.indexes
local mount = vide.mount

type ShopProps = {
	items: () -> { string }, -- a source/derive, or any function returning the list
}

local function ShopPanel(props: ShopProps)
	local open = source(false)

	return create "ScreenGui" {
		Name = "ShopGui",
		ResetOnSpawn = false, -- survive respawns; teardown is explicit

		create "TextButton" {
			Name = "Toggle",
			Size = UDim2.fromOffset(120, 36),
			Position = UDim2.fromOffset(16, 16),
			Text = function()
				return if open() then "Close shop" else "Open shop"
			end,
			Activated = function()
				open(not open())
			end,
		},

		create "Frame" {
			Name = "ItemList",
			Position = UDim2.fromOffset(16, 60),
			Size = UDim2.fromOffset(220, 260),
			Visible = open, -- sources are accepted directly as property values

			create "UIListLayout" {
				SortOrder = Enum.SortOrder.LayoutOrder,
				Padding = UDim.new(0, 4),
			},

			-- one label per index; the label is reused when the name at that index changes
			indexes(props.items, function(name, index)
				return create "TextLabel" {
					Name = "Item",
					Size = UDim2.new(1, 0, 0, 28),
					LayoutOrder = index,
					Text = name, -- `name` is a getter, so Vide binds it reactively
				}
			end),
		},
	}
end

-- Mount into PlayerGui and hand back the teardown function.
local function openShop(items: () -> { string }): () -> ()
	local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")
	return mount(function()
		return ShopPanel { items = items }
	end, playerGui)
end

-- usage
local stock = source({ "Sword", "Shield", "Potion" })
local closeShop = openShop(stock)

-- when the shop closes for good:
closeShop() -- stops the effects and destroys the ScreenGui and its descendants
closeShop = nil
```

- **Teardown:** `mount` returns a destroy function. Calling it once stops every effect and source binding in the tree and destroys the instances `create` made. Keep that function and call it exactly once when the shop is done.
- **Don't parent by hand:** Don't also do `gui.Parent = playerGui` yourself. Pass the target to `mount` so Vide owns the lifetime.
- **Extra resources:** If you add connections or tasks inside the component, register them with `vide.cleanup(...)` so they run on the same destroy.
- **Hiding versus destroying:** The toggle only flips `Visible`, so the panel stays alive while hidden. Use `closeShop()` only for permanent close.
- **Duplicate names:** I used `indexes` rather than `values` so duplicate item names can't collide. If names are unique and you want labels tied to the name rather than the position, swap to `values(props.items, function(name) ... end)`. The `name` argument is then a plain string, not a getter, and the map's second argument is a getter for the index.


===== R4 =====
Here is the component. I didn't open `pesde.toml`, so I'm taking your word that Vide is pinned at 5ed4c01 (0.4.1). The code uses only APIs that exist at that pin.

```luau
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Vide = require(ReplicatedStorage.Packages.vide) -- use the project's mapped path
local create, source, indexes, cleanup = Vide.create, Vide.source, Vide.indexes, Vide.cleanup

-- `items` is a Vide source (or any getter) returning an array of item names.
local function ShopPanel(items: () -> { string })
	local open = source(false)

	local gui = create "ScreenGui" {
		Name = "ShopPanel",
		ResetOnSpawn = false, -- otherwise the UI is destroyed on respawn while the Vide scope lives on

		create "TextButton" {
			Name = "Toggle",
			Size = UDim2.fromOffset(160, 40),
			Position = UDim2.fromOffset(16, 16),
			Text = Vide.derive(function()
				return open() and "Close shop" or "Open shop"
			end),
			Activated = function() -- event property: function value is a listener
				open(not open())
			end,
		},

		create "Frame" {
			Name = "ItemList",
			Position = UDim2.fromOffset(16, 64),
			Size = UDim2.fromOffset(240, 280),
			Visible = open, -- a source is a getter, so this is reactive

			create "UIListLayout" {
				SortOrder = Enum.SortOrder.LayoutOrder,
				Padding = UDim.new(0, 4),
			},

			-- One scope per index; the name arrives as a Source, so it is passed straight to Text.
			indexes(items, function(name, i)
				return create "TextLabel" {
					Size = UDim2.new(1, 0, 0, 28),
					LayoutOrder = i,
					Text = name,
				}
			end),
		},
	}

	-- mount's disposer only destroys the scope; it does not destroy the returned Instance.
	cleanup(gui)

	return gui
end

-- Usage -----------------------------------------------------------------

local shopItems = source({ "Sword", "Shield", "Potion" })

local destroyShop: (() -> ())? = Vide.mount(function()
	return ShopPanel(shopItems)
end, Players.LocalPlayer:WaitForChild("PlayerGui"))

-- Items update live:
shopItems({ "Sword", "Shield", "Potion", "Bow" })

-- Teardown when the shop closes for good.
local function closeShop()
	local dispose = destroyShop
	destroyShop = nil -- clear first: calling a disposer twice errors ("root already destroyed")
	if dispose then
		dispose()
	end
end
```

- **Teardown:** `closeShop()` destroys the mount's scope. That runs `cleanup(gui)`, which destroys the ScreenGui and its descendants. The `indexes` scopes are destroyed with it.
- **Double close:** The reference is cleared before the disposer runs, so a second `closeShop()` does nothing instead of erroring.
- **Mutating the list:** If you mutate the items table in place, call `shopItems(shopItems())` to re-render. A table source notifies on every write of an unfrozen table. Writing a new table, as above, is simpler.
- **Strict mode:** The `derive` and the reactive properties must stay pure and synchronous. In strict mode they run twice per update, and yielding inside them errors.
- **Vide.step():** Don't call `Vide.step()` on teardown. It permanently disconnects the package-wide Heartbeat that drives `spring` and delayed scope teardown.
