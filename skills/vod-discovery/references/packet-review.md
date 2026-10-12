# Packet review

`prepare` splits each source into overlapping packets (default 300 s plus 15 s on each side). Each completed packet folder holds `complete.json`, which names its attempt folder, and a `review.json` ledger. The attempt folder holds `packet.json`, `frames.json`, `frames/raw_*.jpg`, `grids/grid_*.jpg` (3×3 contact sheets), `transcript.json`, `evidence.json` and `evidence.md`. The output root holds `source.json`.

## Review one packet

1. Read `source.json`, `packet.json`, `frames.json`, `transcript.json` and `evidence.md`.
2. View every `grids/grid_*.jpg` with the Read tool. Each cell is labelled with its frame filename (`raw_00012.jpg`); look the filename up in `frames.json` for its source seconds. Open full-size `frames/raw_*.jpg` when a cell is too small.
3. Look for changes in goals, attempts, failures, discoveries, relationships, stakes, outcomes, decisions and reactions. Speech is one signal; use the pictures even when nobody talks. A summary alone is not a discovery result.
4. Record candidates as separate linked moments when the evidence supports it. For a boss kill, keep the kill, relevant attempts or setbacks, and the reactions as separate candidates.
5. Update `review.json` before opening the next packet, so context limits or interruptions lose nothing.

`evidence.md` is a chronological reading aid: frames and speech joined separately for each audio stream. A frame marked `nearby` lies outside the quoted speech interval, and its own timestamp stays authoritative. Transcript intervals that fail validation are listed under `invalid_segments` in `evidence.json`; the raw transcript is unchanged.

Check transcript times against the packet and source duration. Recognition can omit speech or emit segments past the end of the recording. Keep the rough transcript as evidence, flag the defect, and verify affected candidates with other evidence. Never extend a marker past the source or treat an invalid timestamp as observed timing. A span with no transcribed speech is not proof of silence or inactivity.

## Across packets

- Carry short factual state notes forward, and revisit earlier packets when a later payoff shows their significance.
- Merge duplicate observations from overlapping packets, keeping all evidence. Do not merge similar repeated attempts unless they are demonstrably the same event.
- For unclear, fast or important events, run `detail` on a narrow interval with denser frames and a larger width, for example `$PY <skill>/scripts/vod.py detail --source <video> --out work/vods/alice-detail-01 --start 3560 --end 3590 --interval 0.5 --width 1440`. Expand before and after until the cause is understandable, then view the new images. `detail` makes images only; read the surrounding packet transcript for speech.
- Never reject a moment only because transcription failed, was empty or sounds uninteresting. Keep the uncertainty when evidence stays thin.
- Visible text can be read directly from detail frames. The optional OCR helper in [optional-tools](optional-tools.md) only adds searchable text reports.

## `review.json` schema

`prepare` seeds this ledger once per packet and never overwrites it.

```json
{
  "schema": "vod-packet-review/v1",
  "status": "partial",
  "attempt": "attempt-1c096a9a",
  "inspected_sheets": ["grid_01.jpg", "grid_02.jpg"],
  "inspected_frames": ["raw_00031.jpg"],
  "transcript_status": "read",
  "event_ids": ["event-004", "event-005"],
  "notes": ["1712.0 s: Alice and Bob agree to a truce at the bridge."],
  "questions": ["1840 s: who opens the gate is unclear; check Bob's POV."]
}
```

- `status`: `unreviewed`, `partial` or `reviewed`. Mark `reviewed` only after viewing every sheet and reading the transcript.
- `transcript_status`: `unread`, `read`, `defects-flagged`, `empty` or `not-transcribed`.
- `notes`: short factual progression notes with source seconds.
- `questions`: unresolved checks, including suspected cross-POV leads.

Record supplied-evidence coverage (which sheets and frames were inspected) separately from continuous coverage. Sampled stills cannot prove that nothing happened between them.

## Image budget and subagents

At the defaults one packet yields roughly 66 or more frames, about 8 contact sheets of 1440 px. That is about 80 sheets per POV-hour, or roughly 130k image tokens. A four-hour, four-POV session holds well over a thousand sheets: more than one context can review.

For anything beyond a few packets, delegate packet ranges to subagents:

1. Split the work into ranges of about 4–8 packets for one source. Small ranges keep each subagent's images within budget.
2. Give each subagent the packet folder paths, the project's scope and naming notes, this file, and the event-ID prefix to use (for example `alice-p012-`).
3. Each subagent reviews its packets as above, writes each packet's `review.json`, and writes its candidates to `work/candidates/<source>-<first>-<last>.json` using the `events.json` event shape from [events](events.md).
4. Each subagent returns only a short summary: packets reviewed, candidate IDs with one-line descriptions, cross-POV leads, and open questions.
5. The main agent merges the fragments into `events.json`, removes duplicates from overlapping packets, follows cross-POV leads, and checks disputed dialogue or timing directly.

Assign bounded investigations (one event, one range, one question) the same way during cross-POV linking. A fixed agent hierarchy and exhaustive re-review are not defaults.
