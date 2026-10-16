# coin-run

Roblox round game: Rojo + pesde + Vide + Charm + Janitor. Run `bash scripts/check.sh` before calling a change done; `python scripts/check_guards.py` runs the project's guards on their own.

## Libraries

- **Vide**: UI rendering. Use the `roblox-vide` skill.
- **Janitor**: cleanup ownership. Use the `roblox-janitor` skill.
- **Charm**: client-only UI state shared across components, in `src/client/State`.
- **Signal** (`src/shared/Signal.luau`): in-runtime custom events. A vendored module, not a package.
