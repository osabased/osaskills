# Finding where POVs overlap

Run this once per alternate before hunting for individual anchors. It answers "where does this POV overlap the main POV, and at what offset?" from evidence the preparation already holds, so the editor does not search POV by POV. Every result is a lead until someone has looked at it.

## 1. Screen text, when POVs share some

Chat, kill and death notices, advancement messages and scoreboards are drawn on every POV at the same moment, and a streamer can be silent for minutes. Read that text with a fixed crop:

1. View one frame from each POV and pick the region that holds the shared text. The crop differs by resolution and UI scale, so choose it per source: `WIDTH:HEIGHT:X:Y` in that source's pixels.
2. Run, once per source:

```sh
"$PY" <skill>/scripts/region_text.py --source /media/vods/alice.mp4 --prepared work/vods/alice --name chat --crop 820:260:0:800
```

It samples a real frame every 3 seconds (`--every-sec`), reads each upscaled crop with the [Windows OCR helper](optional-tools.md#windows-ocr-find-notices-and-other-visible-text), and merges the same on-screen line across samples. The result is `region-text/<name>.json` inside the prepared folder; the chunk files stay beside it. A crop is not a frame map: the timestamps come from the extraction itself. Chunks of 10 minutes (`--chunk-sec`) make a long source resumable. Windows only; without it, continue with speech.

## 2. Find the offsets

```sh
"$PY" <skill>/scripts/pov_alignment.py --main work/vods/main --alt work/vods/bob --alt work/vods/carol --out outputs/alignment.json
```

Run it once per main part, with that part's prepared folder as `--main`. Shared rare phrases from transcripts and region text vote for an offset; the strongest agreeing groups become spans. Each span states `alt = main + offset`, the main interval its evidence covers, the quiet gaps inside it, and its score against the best score that randomly re-timed speech reaches.

- `candidate_needs_review`: beats the chance score. Look at it on a pair sheet before accepting.
- `weak_lead`: does not beat chance. Look only if nothing better exists; an unrelated stretch can match by luck.
- No span means no shared text was found. It does not mean no overlap: voice chat is often proximity-based, so POVs far apart share little speech.
- Several candidate spans for one alternate can be a real discontinuity (a restart) or noise. Rank them by score and check each.
- The resolution is a few seconds, from transcript segments and the sampling interval. Treat the offset as a search interval; use `vod.py detail` and local anchors for tighter timing.

## 3. Look at it

```sh
"$PY" <skill>/scripts/pov_pairs.py --main-source main.mp4 --alt-source bob.mp4 --offset-sec 12.5 --main-times 400,900,1500,2100 --out work/pairs-bob
```

Each row puts the main frame beside the alternate frame at main time plus the offset, with both times printed. View the sheets. Choose times near the span's edges and, if the offset must hold across a quiet gap, inside it. Accept only when the same event, item, notice or chat line appears in both columns; matching scenery proves nothing. Reject or re-search when a time disagrees, and treat a restart between two good times as a new offset.

## 4. Place the alternates

```sh
"$PY" <skill>/scripts/plan_alternates.py --events outputs/events.json --alignment outputs/alignment.json --plan outputs/timeline-plan.json --accept <alt-source-id>:0 --covered <alt-source-id>=1200-1500 --note "pair sheets: work/pairs-bob" --out outputs/timeline-plan-alts.json
```

`--accept` takes the span index you confirmed. For every main block that the span's evidence covers, the plan gets one disabled alternate excerpt over the same stretch, translated by the offset. A block outside the evidence is listed in the `.report.json` as unchecked instead of placed; confirm it on a pair sheet and pass the range with `--covered`. A block the alternate recording does not reach is skipped, and a partly covered one is clipped. Blocks use the same status and gap settings as `review_timeline.py`; pass the same `--label-status` and `--close-gaps-sec` to both. Run it again for the next main part with the previous output as `--plan`.

The alternates carry `uncertainty_sec` from the span, so the clip name shows its sync allowance. Record the same link in `events.json` only when an observed local anchor supports it; see [cross-POV linking](cross-pov.md).

## What this has and has not shown

One Minecraft SMP session, one main POV and five alternates, 20-minute slices. Speech alone was tried on three alternates: it cleared the chance score for one, ranked the true offset first but below chance for another, and missed the third. Adding chat text put all five above chance, one of them overlapping only the last eight minutes of the main slice. Pair sheets confirmed three of them; the other two matched offsets an earlier hand review had verified. That is a development check on one cast and one game. It establishes no recall on other footage, and chat layouts, languages and OCR quality will differ. Voice-chat audio matching (Audalign) failed to find these POVs at the one window tried, which fits proximity voice chat; its role stays as in [optional-tools](optional-tools.md).
