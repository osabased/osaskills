# Event interchange

Times are finite seconds from each original media file's playback start. Retain source IDs from `source.json`. IDs identify editorial events across POVs; keep them stable across reruns. Each event has one interval per source; use another event ID for a separate moment in that same source.

```json
{
  "schema_version": 1,
  "sources": [
    {"id": "alice", "path": "D:/VODs/alice.mp4", "label": "Alice", "pov": "Alice", "duration_sec": 7400},
    {"id": "bob", "path": "D:/VODs/bob.mp4", "label": "Bob", "pov": "Bob", "duration_sec": 7500}
  ],
  "events": [
    {
      "id": "event-001",
      "title": "Boss finally defeated",
      "marker_title": "Boss Defeated",
      "marker_summary": "Alice defeats the boss after repeated attempts.",
      "status": "candidate",
      "why": "Resolves the repeated attempts; earlier setbacks may supply context.",
      "perspectives": [
        {
          "source_id": "alice", "start_sec": 3574.2, "end_sec": 3598.1,
          "role": "action", "alignment": "observed", "uncertainty_sec": 0,
          "evidence": "alice packet 11 frames raw_00021 and raw_00024; inspected detail interval 3570–3600"
        },
        {
          "source_id": "bob", "start_sec": 3611.8, "end_sec": 3624.0,
          "role": "reaction", "alignment": "estimated", "uncertainty_sec": 3,
          "marker_title": "Victory Cheer",
          "marker_summary": "Bob cheers after Alice defeats the boss.",
          "evidence": "Shared dialogue near the event; reaction window checked but exact shared-event alignment remains uncertain"
        }
      ]
    }
  ]
}
```

This is an illustrative schema example, not a real finding. Valid status values: `candidate`, `context`, `uncertain`. Role is free text so useful viewpoints need not fit a fixed category. Alignment is `observed` or `estimated`; estimated requires positive uncertainty. Zero uncertainty on an observed interval means no additional cross-POV search uncertainty is being asserted, not that sampled boundaries are frame accurate. Describe boundary limits in evidence when material.

Keep partial/unresolved links in analysis notes without inventing a perspective. Exporter preserves all supplied events, including uncertain ones, and adds links to all other listed perspectives in each comment. It validates IDs, paths, source bounds, status, evidence, and uncertainty before writing any marker export.

## Compact marker presentation

Keep `title`, `why`, `evidence`, source IDs, and timing fields as the full analysis record. Author these display fields when preparing the editor-facing export:

- Source `label`: a short unambiguous POV label, such as `Bob` (or `Bob part 2` when needed).
- Source `pov`: shared human-readable bin name for all recordings/parts from that POV. For example, `label: "Alice part 2"` and `pov: "Alice"` keeps the part-specific marker links while grouping both parts under `01 Media/Alice`. XML falls back to `label` when `pov` is omitted. Set `pov` explicitly for multipart recordings; do not infer identity by stripping words from filenames. This field affects project organization, not marker names, IDs or timestamps.
- Event `marker_title` (required): a 1–4-word visual label answering “What moment is this?” Front-load the distinguishing event/action for the first 10–15 visible characters. No IDs, POV/source metadata, confidence, review flags, explanations or provenance. Omit the current POV's redundant name; retain another participant's name when it distinguishes the moment. `Gear Up`, `Spawn Attack`, `Truce Talk`, `Bob's Offer` are examples. Do not truncate a sentence or add an ellipsis.
- Event `marker_summary` (required): one short factual sentence saying who did what and the observed outcome. Keep the editorial rationale in `why`; do not substitute "setup", "payoff", or "progression" for the actual action/dialogue.
- Perspective `marker_title`: overrides the label when this POV depicts a different aspect (`Fatal Fall` on the falling player's POV, `Death Notice` on another POV). It follows the same visual-label rules.
- Perspective `marker_summary`: overrides the event summary when this POV contributes something different, such as only a death notice during unrelated conversation.
- Perspective `marker_type` and `marker_role`: a useful link label and a short contribution, for example `ALT` and `watches the fight`. Use `REACTION` only for an evidenced reaction.
- Event `review_note`: a specific unresolved issue, for example `Exact resource/goal is unclear.` It produces a `CHECK` comment, never a name suffix. Uncertain events without a specific note still receive a review reminder in comments.

Example marker display:

```text
Winning Hit
Alice defeats the opponent at spawn.
ALT Bob 03:10–03:22 — watches the fight (±1s)
Ref [VOD:event-008]
```

Name contains only the authored label; Comment starts with the factual explanation, then POV links/review notes, then the stable reference. Comments omit the current source's repeated range and raw evidence. The detailed event JSON remains the provenance record. Missing display fields fail with an actionable error rather than falling back to long analysis titles or editorial rationale. JSON, XML and panel imports use the same presentation. The XML writer also validates direct marker input, so callers cannot bypass the label/reference contract.

Review the labels in source-time order, including their first 10 and 15 characters. Length alone does not prove scanability: distinguish neighboring events, retain semantic uncertainty (use a neutral label when needed), and avoid repeated generic openings. The exporter enforces clean 1–4-word labels; semantic quality and redundant POV names require authored review. Ten to fifteen characters is a visibility assumption, not a mechanical cutoff.

For non-simultaneous connections, use an event's `related_events` list:

```json
{"event_id":"event-008", "source_id":"bob", "relationship":"earlier"}
```

Allowed relationships: `earlier`, `later`, `setup`, `payoff`, `related`. The referenced event and perspective must exist. The exporter resolves its source range and labels the relationship explicitly; it makes no synchronization claim between these separate events. Keep speculative/unresolved connections in analysis notes.

The resulting marker file uses schema `vod-source-markers/v1`. Each marker has a stable key, name, comments, and source-local start/end. Its Comment contains exactly one `[VOD:key]` token; the JSON source object retains the source ID/path. New panel inputs require the short-name/comment-reference format; re-export older marker files. For existing Premiere markers, the panel recognizes references in comments and legacy references in names. This prevents a naming migration from silently duplicating a suggestion. Identical suggestions are skipped, including XML's flattened comment separators. Changed content under an existing key still fails explicitly so a rerun cannot silently override human review. For revised copy, create a separate review project unless updating existing markers has been explicitly scoped and safely implemented.
