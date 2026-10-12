# Blink 0.18.9 schema syntax

Checked against `docs/pages/language/*.mdx` and `src/Lexer.luau` at tag `v0.18.9`. Comments use `--` and `--[[ ... ]]`; `#` is not a comment.

## Options

Options go at the top of the file, before any declaration (a later `option` is a compile error): `option Name = value`.

| Option | Default | Meaning |
| --- | --- | --- |
| `ServerOutput`, `ClientOutput`, `TypesOutput` | | Output file paths, relative to the schema file. |
| `RemoteScope` | `""` | Prefix for remote names (`<SCOPE>_BLINK_RELIABLE_REMOTE`, ...). Use a unique value per Blink setup. |
| `Casing` | `Pascal` | `Pascal`, `Camel` or `Snake`. Controls the generated method names. |
| `Typescript` | `false` | Also emit `.d.ts` files next to the outputs. |
| `UsePolling` | `false` | Give every event a polling API. |
| `ManualReplication` | `false` | Turn off automatic end-of-frame sending and expose `StepReplication()`. |
| `WriteValidations` | `false` | Check primitive types when firing. Useful in development; costs performance. |
| `SyncValidation` | `true` | Detect yields in sync handlers. |
| `FutureLibrary`, `PromiseLibrary` | | Require paths, e.g. `"ReplicatedStorage.Packages.Promise"`, for `Yield: Future`/`Promise`. |

## Types

- Numbers: `u8`, `u16`, `u32`, `i8`, `i16`, `i32`, `f16`, `f32`, `f64`. Bound them with a range: `u8(0..100)`, `f64(..1000)`, `u8(5)`.
- `string(3..20)`, `buffer(..900)`, `vector`, `vector<i16>`, `vector(0..1)`, `CFrame`, `CFrame<i16, f16>`, `boolean`, `BrickColor`, `Color3`, `DateTime`, `DateTimeMillis`.
- `Instance` or `Instance(Player)`. Subclasses are accepted. A `nil` result on the receiving side raises a deserialization error unless the field is optional.
- `unknown`: uses Roblox serialization. Use it sparingly.
- Optional: `T?`, placed after the whole type. Arrays: `T[]`, `T[1..50]`.

## Declarations

```blink
type Health = u8(0..100)

struct Entity {
	Health: Health,
	Position: vector,
	Tags: string[..8],
	Anim: struct { First: u8?, Second: u8 },
}

enum Status = { Idle, Walking, Running } -- unit enum
enum Shape = "Kind" { -- tagged enum: { Kind = "Circle", Radius = ... }
	Circle { Radius: f32 },
	Rect { Size: vector },
}

map Scores = { [string]: u32 } -- no size bound at 0.18.9; the entry count is a u16
map Pair<K, V> = { [K]: V } -- generics, also on tagged enums
set Flags = { FeatureA, FeatureB } -- { [string]: true }

scope Combat { -- referenced as Combat.Hit; the generated API nests the same way
	event Hit { From: Client, Type: Unreliable, Call: SingleAsync, Data: (u16, vector) }
}

import "./shared" as "Shared" -- a sibling file becomes scope Shared

export struct Snapshot { Tick: u32 } -- generates Read/Write functions for the type
```

Structs can merge another struct: `struct B { ..A, Extra: u8 }`. Exports don't support `Instance` or `unknown`.

## Events and functions

```blink
event Name {
	From: Client,        -- or Server
	Type: Reliable,      -- or Unreliable (at most 1000 bytes)
	Call: SingleAsync,   -- SingleSync | ManySync | SingleAsync | ManyAsync | Polling
	Data: (u8, string)   -- optional; a type pack sends several values
}

function Name {
	Yield: Coroutine,    -- or Future / Promise (needs the matching *Library option)
	Data: u32,           -- optional
	Return: string       -- optional
}
```

`Single*` allows one listener; `Many*` allows several. `*Sync` handlers must not yield or error. `Polling` events are read with `Iter()`.
