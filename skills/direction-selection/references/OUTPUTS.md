# Direction outcomes

Use these contracts for agent/controller handoffs or when the user requests a full record. For ordinary answers, use the presentation guidance in [SKILL.md](../SKILL.md#user-facing-presentation). Keep fields concise; evidence references belong beside deciding claims.

## Applicability Result

Use when comparison never owns a decision:

- **Result:** exit | handoff
- **Reason:** why comparison does not currently apply
- **Owner / next route:** fitting owner or action, or `none`

An applicability probe returns its findings to the router; it does not emit a direction gate.

## Direction Decision

Use for a conventional passing recommendation:

- **Mode:** lightweight | full
- **Governed commitment:** exact direction-dependent commitment supported
- **Chosen direction:** one sentence
- **Why it wins:** decisive reasons under the ordered criteria, with evidence references and material inferences
- **Alternatives / candidate-space result:** serious candidates and decisive losing tradeoffs; `none — no search required`; or `none — required bounded search found no credible alternative`
- **Assumptions / uncertainty:** material items only
- **Reopen if:** concrete evidence or conditions that invalidate the choice
- **Direction Gate:** PASS

## Direction Blocker

Use only after a comparison mode exists and support is insufficient:

- **Mode:** lightweight | full
- **Governed commitment:** what cannot yet proceed
- **Unresolved decision:** the choice still open
- **Blocking condition:** exact evidence, preference, constraint, tie, or support failure
- **Owner / next step:** fitting owner and adequate action, or `none` when no justified action remains
- **Decision effect:** how plausible resolutions could change the result
- **Resume when:** observable condition sufficient to resume, or `none` when no justified condition is known
- **Direction Gate:** NOT PASSED

## Adaptive Direction

Use only when all of these hold:

- The commitment is consequential and worthwhile evidence has been gathered.
- Important uncertainty is structurally unstable or depends on a future event that research cannot settle in time.
- A nominal winner would imply unsupported certainty, and indefinite delay is unjustified.
- A useful bounded commitment can be assessed independently of the unresolved later choice.

Sparse evidence, inconvenient research, or an unknown user preference alone does not establish these conditions.

Return:

- **Mode:** adaptive
- **Current bounded commitment:** what is supported now
- **Why this bounded commitment is supportable now:** decisive support across the conditions it must survive
- **Why a nominal winner is not justified:** concise reason
- **Structurally unstable uncertainty:** material unknowns or futures
- **Optionality preserved:** what remains open or migration-capable
- **Exposure limit:** cap on cost, scope, migration, users, data, or time
- **Adaptation trigger:** observable condition
- **Reopen / branch:** exact decision or direction to revisit
- **Direction Gate:** PASS | NOT PASSED

Adaptive `PASS` requires the same support standard as a conventional decision, applied to the bounded commitment until its exposure limit or adaptation trigger. If a plausible outcome can invalidate that commitment before safe redirection, return `NOT PASSED`. Preserve the unresolved later choice; the bounded gate grants no broader execution authority.

## Return boundary

Return the result and gate to the caller. Discovery supplies evidence to the comparison or applicability router; it never chooses or emits these outcomes itself. Preserve existing authority and still-applicable work when handing off, escalating, or reopening. Neither a passing record nor persistence of it authorizes additional work.
