# Cross-agent synthesis

Use after independent review passes exist, when sharing a specific result could change another perspective's conclusion.

1. **Preserve the first passes.** Retain each perspective's original scope, target, evidence, conclusion, and uncertainty before sharing results.
2. **Send deciding evidence.** Send the affected perspective only the evidence and provenance that could change its finding, cause, disposition, or visibility gap. Name the assumption or conclusion being rechecked.
3. **Let the owner recheck.** Return `CONFIRMED` for a changed or added conclusion, `REFUTED` when the signal does not change it, `RELATED` for support already covered, or `UNRESOLVED` with the exact missing evidence. Each disposition needs its evidentiary basis; agreement alone is insufficient.
4. **Reconcile once.** Apply the parent review's evidence and finding rules. Group symptoms of one failed control, preserve independent failures, and retain real evidence conflicts with the check needed to resolve them. Keep each conclusion with its qualified owner.

Another signal round requires materially new evidence or a conflict that could change the result. Return findings and remaining gaps to `system-review`; synthesis does not start a separate remediation or review process.

**Complete when:** every retained signal has an evidence-backed disposition or a specific unresolved check, and the original and revised conclusions remain distinguishable.
