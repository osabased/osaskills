# Editing defaults and the layered review timeline

## Editing defaults

Apply these on every project unless the current request overrides them. Keep project-specific exceptions in the project's notes; source identities, main POV, chronology and hardware always come from the current project.

- The editor discovers and assembles together. Make useful footage easy to select and edit immediately, and reduce repeated viewing, context reconstruction and decision switching. The review queue stays optional; do not require a separate selection pass before assembly.
- There is no fixed final runtime. The video is as long as its material earns. The complete review timeline is source material, not a recommendation for the final edit's length.
- With an established main POV, the default Premiere delivery is the complete review timeline below plus source clip markers with POV links in comments. Source markers alone remain available on request or while the main POV is unresolved.
- Import one timeline audio clip per actual audio stream. Keep genuine stereo grouped with both channels; do not duplicate or split it because A1/A2 are enabled or targeted. Probe the real stream count. The current XML exporters accept at most one mono or stereo stream per source; for more, see [premiere](premiere.md#supported-media).
- Preserve source markers and organized media and POV bins.

## Layout

The exporter builds a complete chronological review timeline, not an automatic selects assembly. Its inputs are the same `events.json` plus a separate placement plan authored from reviewed evidence; no POV is hardcoded.

- The plan's `main_sources` stay complete and in plan order on the base video track, with their audio below. Take `main_sources`, part order and identities from the current project. Resolve the main POV before building this layout; source-marker discovery does not need one.
- Main video and linked audio are cut at each included moment's start and end. Moment sections get the **Mango** clip label; surrounding footage gets no label element, so Premiere shows its normal default. Every frame appears exactly once, including unmarked footage. Overlapping and nested moments keep every distinct boundary without duplicating footage; adjacent moments keep their shared edit.
- For a moment at 1:48–1:59 the main becomes `[0:00–1:48 default] [1:48–1:59 Mango] [1:59–end default]`. Nothing is removed or moved.
- Relevant alternate excerpts sit on upper video tracks, one layer per alternate source, with their audio on separate higher tracks. **Main picture and audio play by default; alternate video and audio start disabled.** Alternates also use Mango.
- Labels are visual locators, not confidence ratings, and do not mean surrounding footage is uninteresting.
- Secondary-only moments stay as source markers unless a reviewed local anchor supports placing them.
- Earlier setup and later reactions keep their true time relationship; never stack them as simultaneous because they are editorially related.

If the editor asks for a different assembly, settle it explicitly instead of treating this review layout as the requested edit.

## Build

```sh
"$PY" <skill>/scripts/review_timeline.py --events outputs/events.json --plan outputs/timeline-plan.json --out outputs/discovery-timeline.xml
```

Add `--path-map LOCAL=HOST` when the media is mounted at a different path than on the editor's machine, and `--force` to replace an existing `--out`. Import into a new Premiere review project, then follow the import checks in [premiere](premiere.md#after-import) and open the sequence in `02 Sequences`.

If an alternate has a different resolution, the editor selects its timeline clips and uses Premiere's **Fit to frame** before delivery, then checks an overlapping moment. The XML keeps native dimensions and writes no scaling effects, so a 720p alternate otherwise appears smaller over a 1080p main. Keep fitted alternates disabled and save the verified `.prproj`.

## Plan format

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

This example is illustrative, not a default mapping. All times are local playback seconds. Main part offsets accumulate from full nominal frame durations, and main parts must share a nominal rate. An alternate is placed by the difference between its two local anchor times; its duration never changes. Overlapping excerpts on one layer are rejected: merge or trim the reviewed windows explicitly without dropping events. `event_id` is required for review-queue use.

Derive anchors from matching evidence per [cross-POV linking](cross-pov.md), never from broad marker range starts. Record uncertainty from both views and check the local span for discontinuities. Keep earlier/later connections as source-marker links rather than moving footage to fake simultaneity.

## XML details that affect correctness

- Labels are written as `labels/label2` on moment clip instances, not on the shared source master. Exact swatches depend on the editor's [label preferences](https://helpx.adobe.com/premiere/desktop/get-started/preferences-and-settings/labels-preferences.html); XML parsing cannot confirm displayed colors.
- A stereo stream is two FCP channel records but **one Premiere stereo group**, using exploded-track metadata and linked audio `groupindex`. Removing the second record loses the right channel. Track targeting is not a substitute for correct channel mapping.
- Sequence clip In/Out values use **sequence-rate frames**, even for 30 fps alternates in a 60 fps sequence; the master keeps its native rate. Source-rate In/Out imported half the intended seconds in Premiere 2026.

## Verify the saved result

The editor (or you, with access to Premiere) checks:

- source paths, marker names, comments and times;
- main part order and duration, and every alternate's In/Out and position;
- cuts and contrasting labels around included moments, with matching video and audio boundaries, no gaps, no duplicate frames and no extra audio tracks;
- both channels in each stereo group;
- alternates disabled and mains enabled; audition an alternate at an overlapping moment, then disable it again before saving.

Source marker names follow [events](events.md); alternate clip names describe the excerpt and are separate. Report coverage separately from timeline length: a full-length timeline with five minutes of suggestions is not a full-VOD discovery pass. Keep a requested fast test bounded to its agreed scope.
