# Direction Outcomes

Read for agent/controller handoffs, user-requested full records, or an adaptive commitment. Ordinary user answers use [User-facing presentation](../SKILL.md#user-facing-presentation). The parent Support threshold and Direction Gate scope govern every outcome.

## Applicability Result

Use only when comparison never becomes the owner:

- **Result:** exit | handoff
- **Reason:** why no comparison currently owns the decision
- **Owner / next route:** fitting owner or action, or `none`

## Direction Decision

- **Mode:** lightweight | full
- **Governed commitment:** exact direction-dependent commitment supported by this gate
- **Chosen direction:** one sentence
- **Why it wins:** decisive reasons under the ordered criteria, evidence references, and material inferences
- **Alternatives / candidate-space result:** serious candidates and decisive losing tradeoffs; `none — no search required`; or `none — required bounded search found no credible alternative`
- **Assumptions / uncertainty:** material items only
- **Reopen if:** concrete conditions invalidating the choice
- **Direction Gate:** PASS

## Direction Blocker

Use only after a comparison mode exists and its gate cannot pass:

- **Mode:** lightweight | full
- **Governed commitment:** what cannot yet proceed
- **Unresolved decision:** choice still open
- **Blocking condition:** exact evidence, preference, constraint, tie, or support failure
- **Owner / next step:** fitting owner and smallest proportionate action, or `none` when none is justified
- **Decision effect:** how plausible resolutions could change the result
- **Resume when:** observable sufficient condition, or `none` when none is known
- **Direction Gate:** NOT PASSED

## Adaptive Direction

Use only for a consequential commitment after worthwhile evidence gathering, when important uncertainty is structurally unstable rather than under-researched, an overall winner would create false certainty, indefinite delay is unjustified, and a bounded robust or adaptive commitment can itself be justified.

- **Mode:** adaptive
- **Current bounded commitment:** what this decision and gate support now
- **Why this bounded commitment is supportable now:** support across the plausible conditions it must survive
- **Why a nominal winner is not justified:** concise reason
- **Structurally unstable uncertainty:** material unknowns or futures
- **Optionality preserved:** what remains open or migration-capable
- **Exposure limit:** cap on cost, scope, migration, users, data, or time
- **Adaptation trigger:** observable condition
- **Reopen / branch:** exact decision or direction to revisit
- **Direction Gate:** PASS | NOT PASSED

Adaptive `PASS` requires the bounded commitment to satisfy the parent Support threshold until its exposure limit or adaptation trigger. Residual uncertainty may affect later branches. If a plausible outcome could invalidate this commitment before safe redirection, return `NOT PASSED`. Adaptive handling neither establishes an overall winner nor grants project-wide authority.

## Return and presentation

Keep one concise local record. The caller/controller owns project persistence and execution; this skill does not require persisting every decision.

For user-facing adaptive `PASS`, lead with **Bounded next step** and retain the commitment, support, reason no overall winner is justified, uncertainty, preserved options, exposure limit, and adaptation/reopen trigger. For adaptive `NOT PASSED`, additionally make the exact blocker, owner, next action, and resume condition clear. A missing justified next action must remain explicit.
