# Architecture Improvement Outcomes

Use for agent/controller handoffs or a user-requested full record. Ordinary user answers use the parent [Output](../SKILL.md#output) guidance.

## Architecture Improvement

- **Scope:** bounded target and revision
- **Disposition:** `IMPROVED` | `NO CHANGE` | `LOCAL HANDOFF` | `PLANNING HANDOFF` | `BLOCKED`
- **Reconnaissance:** direct/delegated coverage, capability profiles actually used, and material limits or assignment mismatches
- **Evidence:** decisive repository evidence
- **Intervention Gate:** pass or decisive failure by condition
- **Objective:** selected architecture change, local correction boundary, planning target, or `none`
- **Work completed:** changed behavior and structure, or `none`
- **Verification:** checks/scenarios actually run and blocked checks
- **Residuals:** task-related residue, or `none`
- **Reopen if:** concrete evidence or conditions changing the disposition

For `NO CHANGE`, distinguish no credible candidate from a candidate rejected for a decisive gate failure. Exclude non-authorizing observations.

For `PLANNING HANDOFF`, include the supported objective, causal structure, affected behavior, constraints, stabilization, migration boundary/order, first executable slice, verification obligations, and retirement conditions needed by `to-spec` or `to-tickets`.

`EXECUTE` is an internal route, not a completed outcome. Return `IMPROVED` only after [EXECUTION.md](EXECUTION.md) completes. An incomplete objective or blocked required verification must retain its exact residuals and return `BLOCKED`.
