---
name: reconnaissance
description: Gather missing repository or system evidence with the minimum necessary GPT-5.6 Luna scouts when direct inspection would materially consume controller context or independent parallel inspection improves coverage.
---

# Reconnaissance

Gather evidence without taking ownership of the decision. The caller remains the controller: it owns synthesis, consequential judgment, source writes, implementation, and lifecycle decisions.

Use this skill only when delegation is cheaper or safer than having the controller inspect everything itself. A direct lookup is a valid outcome.

## 1. Bound the information need

State the exact question the caller cannot answer reliably from current context.

Prefer direct inspection when one cheap lookup, one small file region, or one obvious command can settle it. Delegate when the target is large or unfamiliar, materially different regions can be inspected independently, omission risk is meaningful, or direct exploration would substantially pollute the controller's context.

Reuse established caller context. Do not re-discover facts already supplied with adequate provenance.

**Complete when:** the missing information is explicit and delegation has a concrete advantage over direct inspection, or the skill returns `DIRECT` with the smallest fitting lookup.

## 2. Partition minimally

Split only genuinely independent information needs. One scout owns one bounded question.

Use **GPT-5.6 Luna** for scouts. Request the exact model when the harness exposes model selection. If Luna is unavailable, prefer the lowest reliable non-Astra model and report the substitution; never spend Astra on reconnaissance.

Start with the minimum scout count. Most runs should use 1–3 scouts. Never exceed 4 scouts in one invocation. If four packets still leave a material gap, return that gap to the caller instead of widening the swarm.

Parallelize only independent assignments. Do not create multiple scouts for the same question unless conflicting evidence or material omission risk gives independent corroboration clear value.

Each scout is read-only with respect to source files. It may use safe inspection and diagnostic commands needed for its assignment.

Give each scout a work order containing:

- **Question:** exact result needed
- **Scope:** included paths, symbols, history, tests, documents, or interactions
- **Known context:** applicable established facts and constraints
- **Evidence bar:** what must be inspected or executed and how provenance should be reported
- **Counterevidence:** what could disprove the suspected explanation
- **Non-goals:** adjacent work left untouched
- **Stop condition:** observable completion or blocker

**Complete when:** every scout has a distinct question, bounded scope, and stop condition, with no duplicated assignment.

## 3. Collect compact packets

Require each scout to return:

### Scout Packet

- **Coverage:** inspected scope and material exclusions
- **Findings:** concise decision-relevant facts
- **Evidence:** paths, symbols, lines, commits, tests, commands, or other provenance
- **Counterevidence:** facts that weaken the apparent explanation
- **Unknowns:** unresolved gaps that could materially change the caller's judgment
- **Next probe:** smallest useful follow-up question, or `none`

Prefer pointers and summarized observations over copied source, raw command output, search logs, or transcript-style narration. `No relevant evidence found` is a valid result.

Treat scout claims as evidence input, not authority. Preserve material disagreement between packets instead of silently choosing a winner.

**Complete when:** every assignment returns a packet or explicit blocker matching its work order.

## 4. Return evidence to the caller

Deduplicate repeated evidence and group directly compatible findings. Flag conflicts, coverage gaps, and material uncertainty. Do not choose architecture, select a consequential direction, write source, or continue into implementation.

Return:

### Reconnaissance Result

- **Question:** original information need
- **Route:** `DIRECT` | `DELEGATED`
- **Coverage:** what was actually inspected
- **Established evidence:** compact supported findings with provenance
- **Conflicts / counterevidence:** material contradictions or weakening evidence
- **Unknowns:** only gaps that could affect the caller's next decision
- **Suggested next probe:** smallest discriminating lookup, or `none`
- **Capability note:** requested scout model and any material substitution

Stop when the caller has enough traceable evidence to resume reasoning. A healthy or uneventful target is completion, not a reason to broaden the search.