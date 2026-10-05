# Layered discovery timeline

Use the same factual events/source markers plus a separate, evidence-authored placement plan. Full main sources remain chronological; alternates are trimmed suggestions on upper video tracks, with one corresponding audio track per actual stream. Both alternate video and audio clips start disabled.

Take `main_sources`, part order, identities and coverage from the current project. If no main POV is designated and that choice matters, resolve it before building this layout; source-marker discovery does not require one. The format example below is illustrative, not a default source mapping or a claim about reviewed footage. Alternate references must use the current event/source IDs and reviewed anchors.

## Moment cuts and clip colors

Every included main-source moment adds an edit at its start and end in both video and linked audio. Its timeline sections use the **Mango** clip label; surrounding footage keeps its normal/default label. Alternate excerpts also use Mango and remain disabled. For a moment at 1:48–1:59, the main becomes `[0:00–1:48 default] [1:48–1:59 Mango] [1:59–end default]`. Nothing is removed or moved. Preview padding and added browser context do not change these cuts.

Cuts use the same validated, frame-quantized source marker boundaries. Overlapping and nested moments retain every distinct boundary, without overlapping or duplicating main footage. Adjacent moments keep their shared edit even though both are Mango. Whole-source moments need no empty edge clips; unmarked main parts remain complete clips with no label override. Source markers retain individual names and explanations for overlapping moments. Independent secondary-only moments remain source markers unless a reviewed local anchor supports placement.

Both the direct timeline command and queue exports use this behavior. **Export kept** includes only Keep moments' cuts/colors, markers and alternate excerpts; **Export all** includes every discovered moment. Skipped, deferred and unreviewed main footage still remains in place. The source-marker-only exporter does not create or cut a sequence.

Mango labels are written on moment video/audio clip instances as `labels/label2`, not on the shared source master. Surrounding footage has no `labels` element, so the exporter does not force a replacement for Premiere's normal/default label. Color is a visual locator, not confidence or proof that surrounding footage is uninteresting. Exact swatches depend on Premiere's label preferences; confirm the contrast after import. The format supports [clip labels](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/Elements/Elements.html), and Premiere permits [custom label colors and names](https://helpx.adobe.com/premiere/desktop/get-started/preferences-and-settings/labels-preferences.html). Do not claim host color validation from XML parsing alone.

The XML places source items in `01 Media/<POV>` and the timeline in `02 Sequences`. All main parts share their POV bin through the source `pov` field. Bins change project organization only: the sequence keeps references to the same source masters, including when input order interleaves multiple POVs. After import, show the Project panel with Shift+1, expand `02 Sequences`, and open the review timeline.

```powershell
python <skill>/scripts/review_timeline.py --events outputs/events.json --plan outputs/timeline-plan.json --out outputs/discovery-timeline.xml
```

Import into a new Premiere review project. If an alternate has a different resolution, select its timeline clips and use Premiere’s **Fit to frame** command before delivery, then verify at an overlapping moment. The XML preserves native media dimensions and does not yet write scaling effects; a 720p alternate otherwise appears smaller over a 1080p main. Keep the fitted alternate clips disabled and save the verified `.prproj`. Importing again can create duplicate items; this is not an update operation. Preserve the editor's existing project and sequences.

Plan format:

```json
{
  "title": "Main POV with suggested alternatives",
  "main_sources": ["main-part1", "main-part2"],
  "coverage_note": "Only the first five minutes of part 1 and the alternate were reviewed.",
  "alternates": [{
    "source_id": "alternate",
    "main_source_id": "main-part1",
    "event_id": "event-08",
    "name": "Alternate view of the winning hit",
    "source_start_sec": 190,
    "source_end_sec": 200,
    "source_anchor_sec": 194.5,
    "main_anchor_sec": 112.5,
    "uncertainty_sec": 1,
    "evidence": "Matching kill notice absent/present at main 112/113 and alternate 194/195; midpoint anchors."
  }]
}
```

All times are local playback seconds. Main part offsets are accumulated from their full nominal frame durations. Alternate placement uses the difference between the two local anchor times; its duration stays unchanged. Main parts must share a nominal rate. Each alternate source gets its own upper layer. Overlapping excerpts on the same layer are rejected: merge or trim reviewed windows explicitly, without dropping events. Unmarked main parts remain in the timeline but are not claimed as reviewed.

Do not generate anchors from broad marker range starts. Use matching evidence, record uncertainty from both views, and inspect the local span for discontinuities. Keep earlier/later editorial connections in source marker links rather than relocating footage to fabricate simultaneity. The sample aligns a local event only, never a whole drifting VOD.

## Import details that affect correctness

- A stereo stream is two FCP channel records but **one Premiere stereo group**. The XML uses exploded-track metadata and linked audio `groupindex` values. Removing the second channel record would lose right-channel audio. Source patching/track targeting is not a substitute for correct channel mapping.
- The current XML adapter supports one mono/stereo audio stream per source. It fails on multiple streams so none are silently lost. For real multi-stream sources, retain native stream mappings or extend and host-test the exporter before claiming support.
- Sequence clipitem In/Out values use **sequence-rate frames**, even with 30 fps alternate media in a 60 fps sequence. The master/file declaration retains native frame rate. Source-rate In/Out incorrectly imported half the intended source seconds in Premiere 2026.
- On Windows use Premiere's own `file://localhost/C%3a/...` path encoding. Verify all resolved source paths; automatic relinking can mask malformed URLs.

## Verify the saved result

Check actual source paths, marker names/comments/times, full main-part order and duration, every alternate source In/Out and timeline position, and that only genuine audio streams have timeline clips. Verify cuts and contrasting labels around included moments, with matching video/audio boundaries and no gaps, duplicate frames or extra audio tracks. Verify both stereo channels in each group. Confirm alternate video and audio are disabled and main clips enabled. Check an overlapping moment in Program Monitor; audition an alternate and return it to disabled before saving. Saved-project XML may be inspected read-only to corroborate the host state; do not author or patch `.prproj` internals.

Source marker names use the same short-label rules as the marker-only XML; see [events.md](events.md). Judge their first 10–15 characters at timeline scale. Detailed descriptions, POV links, checks and stable references stay in marker comments. Alternate clip names describe excerpts and are separate from source marker names.

State coverage separately from timeline length. A full-length timeline with five-minute suggestions is not a completed full-VOD discovery pass.
