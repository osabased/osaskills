# Sonnet with/without-skill comparison (2026-10-11)

Headless Claude Code (`claude -p`, model `sonnet`) ran in a small Rojo + Wally + pesde project ([scaffold](scaffold/)). Each config dir was isolated. Bash, web search and subagents were disabled, so each answer reflects the model's own knowledge plus whatever the skill supplied. In the "with" condition all skills sat in `.claude/skills/` and could trigger on their own. Run it with `python harness.py <cases.json> <case-id>` from this folder.

## Triggering (24 prompts, 1 run each)

- **Positive prompts (18):** the expected skill loaded in all 18. In 17 it loaded through the Skill tool. In the Rojo glob case the model found and read `rojo.md` directly instead.
- **Negative prompts (4):** a TweenService animation, Luau types, a React package, and a rename. No skill loaded.
- **User-only skills:** vod-discovery, then-what and motion-studies did not load automatically, which is correct. An explicit `/then-what` produced its format.

## Quality (7 tasks × with/without × 2 runs, graded blind by Opus against verified ground truth)

| Task | Rubric with | Rubric without | Overall with | Overall without | Cost with | Cost without |
|---|---|---|---|---|---|---|
| Vide component + teardown | 12/12 | 10/12 | 9.0 | 4.5 | $0.07 | $0.07 |
| Blink schema + generated API | 14/14 | 10/14 | 8.5 | 6.0 | $0.07 | $0.05 |
| Janitor + LemonSignal lifetime | 14/14 | 12/14 | 8.5 | 6.5 | $0.09 | $0.08 |
| Rojo globIgnorePaths | 12/12 | 12/12 | 8.0 | 7.5 | $0.07 | $0.04 |
| Client entrypoint placement | 7/10 | 10/10 | 6.0 | 6.5 | $0.12 | $0.06 |
| Checkout flow review | 11/12 | 10/12 | 8.0 | 7.0 | $0.07 | $0.04 |
| "Add a signal library" | 8/10 | 8/10 | 7.0 | 6.5 | $0.20 | $0.07 |
| **Total** | **78/84 (93%)** | **72/84 (86%)** | **7.9** | **6.4** | $0.10 | $0.06 |

What the skills changed:

- **Library guides gave the biggest gains.**
  - **Vide:** without the skill, both runs said the mount disposer destroys the ScreenGui. It doesn't, so the GUI leaks.
  - **Blink:** without it, one run invented `SetCallback`, and neither run mentioned validation or the parser DoS issue.
  - **Janitor:** without it, runs missed that a throwing cleanup leaves the janitor permanently stuck, or made up rules about default methods.
- **system-review** mostly added closure tests ("Close when") and a verdict. The core reasoning was similar.
- **Rojo globs:** both conditions did well. Only the skill run explained why `**/Preview/**` alone leaves the init module.

Fixed after this run:

- **Entrypoint (with skill, 1 of 2 runs):** the run claimed `init.client.luau` builds a RunContext Client `Script` by default. It mixed up Script Sync suffixes with Rojo's. SKILL.md and `rojo.md` now state the Rojo 7 rule, checked against a real 7.7.0 build: `*.client.luau` becomes a `LocalScript` unless `"emitLegacyScripts": false`. After the fix, both re-runs caught the dead `LocalScript` in `ReplicatedStorage` (`results/q-entry-with-*-v2.json`).
- **Add a signal library:** with the skill, the model read the adoption references and reported on records and `CLAUDE.md`, at about 3× the cost. SKILL.md now checks the manifests first and stops when an existing dependency covers the request. Re-runs cost about 40% less and read no adoption references (`results/q-addsignal-with-*-v2.json`).

Limits:

- There are only 1–2 runs per cell, and everything ran on one model.
- Disabling the web removed the baseline's chance to look things up.
- The prompts are fairly direct, so triggering on vaguer wording is untested.
- vod-discovery and motion-studies quality wasn't measured, because both need media or a runtime.
- `grading/key.json` maps the blind labels back to run ids.
