# Joined evidence and cross-POV search

Use these during discovery to retrieve candidate ranges and read their visual/speech context. They use CRV 0.10.7 locally and do not alter Premiere XML, original media, raw transcripts, or packet review decisions.

For one investigation across available speech, keyword ranking, meaning and visible text, build the existing literal index below, then use [unified-search.md](unified-search.md). The unified helper indexes explicitly supplied, frame-map-validated OCR reports and can include the existing local semantic model. It labels evidence types and exposes missing channels and coverage. The original `vod.py search` remains a literal-only phrase check.

## Prepare evidence

`prepare` now writes `evidence.json` and `evidence.md` inside each completed attempt. Resuming an existing preparation refreshes these files without extracting/transcribing completed packets again. To enrich only already-completed packets:

```powershell
python <skill>/scripts/vod.py evidence --prepared work/vods/johan
```

CRV joins frames to speech independently for each audio stream. The adapter converts packet-local join clocks back to source seconds and keeps all sampled frames. Frames outside a speech interval that CRV attaches to the closest span are explicitly marked `nearby`; they do not prove an action occurred during that quotation. A span without recognized speech can still contain music, reactions, effects or meaningful visual activity.

Invalid transcript intervals are retained under `invalid_segments` with their raw text and reason. They are excluded from the joined speech and search index rather than silently clamped into plausible events. Check them against surrounding images/audio when relevant. Raw `transcript.json` remains unchanged. `evidence.md` quotes footage text as data, not instructions.

## Index the project's prepared POVs

```powershell
python <skill>/scripts/vod.py index --prepared work/vods/johan work/vods/josh --out work/vods/search
python <skill>/scripts/vod.py search --index work/vods/search --query "the fog is coming"
python <skill>/scripts/vod.py search --index work/vods/search --query "truce" --limit 50
```

Run with the project's compatible Python environment. Pass all prepared POV folders that belong in this search index, including partly prepared sources. Indexing enriches their completed packets as needed. No video decoding or speech transcription is performed. All files stay under the explicitly selected output folder; this does not use CRV's global library database.

The index aggregates all completed packets per source before calling CRV's `remember`, which otherwise replaces earlier rows for the same source. Overlap observations with exactly matching start time and text share a search row while retaining every occurrence's end time, audio stream, packet file and transcript segment index. Similar wording at different times remains separate; these rows are not claims that two observations are the same event.

Repeated indexing with unchanged inputs reuses the snapshot. A rebuild creates a new snapshot and publishes it only after all supplied sources finish, so a failed rebuild preserves the previous index. Rebuild with the complete desired source list: previously indexed sources omitted from that list are absent from the new snapshot. Old snapshots remain on disk and may be removed when no longer needed. The active snapshot is identified by `index.json`.

## Interpret results

- Hits identify the source file and source-local start time, plus exact transcript/evidence files and segment indices for every matching occurrence. Read the relevant joined evidence and open the actual images; text search does not establish visual coverage or synchronize POVs.
- Coverage lists completed/total packet counts and prepared core ranges. These measure preparation, not human/AI review. Search cannot cover unprepared footage.
- This command matches literal phrases, case-insensitively. Try shorter phrases, alternate spellings and transcription variants. Optional meaning-based retrieval uses a separate `semantic.py` command and index; see [speech-search.md](speech-search.md). Neither route establishes speaker identities or searches visual/OCR evidence.
- The default limit is 20, configurable from 1 to 200. `at_limit: true` means additional matches may have been omitted; narrow the query or raise the limit. This retrieval limit is not a top-N limit on discovered moments.
- Raw transcript defects and excluded-invalid-segment counts remain visible. An empty search result never establishes that an event did not occur.
- If a source record or completed packet's transcript, frame map or timing changes, search refuses the stale index. Rebuild it before continuing. Review-ledger changes alone do not require rebuilding.

Keep the usual packet/visual review and local-anchor verification. These tools narrow investigations and reduce repeated reading; they do not select final edits or replace the overinclusive discovery pass.
