# Saved local review queue

Use this when the editor wants to make and resume Keep/Later/Skip decisions outside Premiere. It is optional: ordinary discovery still exports markers directly. The dashboard presents one evidenced moment at a time, short factual copy, individual POV previews, checks, related moments, notes and reversible choices. Do not preselect Keep, hide uncertain candidates, impose a top-N limit, or equate clicking Keep with verifying alignment.

## Build and run

Requires Python 3.10+, FFmpeg and ffprobe on PATH. It uses the existing event and timeline adapters plus browser-native video; there are no npm packages, cloud services or new Python dependencies. Inputs are the complete validated `events.json` and an authored `timeline-plan.json` with stable `event_id` on every alternate. The existing XML constraints apply: one video and at most one mono/stereo audio stream per source, compatible main rates and supported source timecode. Unsupported audio layouts fail before rendering; no streams are silently dropped.

```powershell
python <skill>/scripts/review_queue.py init --events outputs/events.json --plan outputs/timeline-plan.json --out outputs/review-queue
python <skill>/scripts/review_queue.py serve --queue outputs/review-queue --port 8765 --open
```

`init` requires a new directory and prepares every supplied perspective with three seconds of context on each side, clipped to media bounds. Previews use 960-pixel width, 24 fps, H.264 and AAC. Full source times and original media paths remain authoritative. This is preview transcoding, not additional discovery or audio transcription. Runtime/storage grow with the supplied event ranges. Start with a bounded pilot rather than rendering an entire session speculatively. A failed build leaves its partial files for diagnosis and is not serveable; use a fresh output directory after correcting it. To resume a completed queue, run `serve`, not `init`.

The URL is `http://127.0.0.1:8765`. The server binds only to loopback and serves registered previews/assets/exports, not arbitrary local files. It requires same-origin authenticated writes, detects conflicting tabs, and holds a process lock on this queue. On Windows launch background helpers with a hidden window and redirected logs. A queue in another folder may use another port. Stopping the server does not erase choices; restart it to continue.

## Editor experience

- Default order: main POV chronology, then independent secondary moments in their own source order. This is not a combined synchronized clock.
- `1` Keep, `2` Later, `3` Skip, `U` Undo. Space plays/pauses; arrows seek five seconds. Shortcuts do not intercept note entry. Each choice saves before moving forward.
- Keep means potentially useful. Later preserves uncertainty. Skip is recoverable and deletes neither discoveries nor footage. No decision is made from playback completion or preview failure.
- Auto-save preserves each moment's note, chosen preview, playback position and current moment. Playback position saves approximately every five seconds and on pause/navigation. Wait for **Saved on this computer** before closing. A crashed browser may lose the last few seconds of position or an unconfirmed note, not previously confirmed choices.
- POV buttons play separate, source-local excerpts with that POV's audio. They are not a synchronized angle switcher; they show timing uncertainty. Premiere exports keep the main picture/audio enabled and the alternative picture/audio disabled.
- Filter to Later to revisit unresolved choices. Related-event buttons navigate to the earlier/later event without moving its media to a false simultaneous position.
- Undo restores the last decision, including after restart, while preserving notes and playback positions. The complete history and all candidates remain in the queue folder.

## Save and export contract

`queue.json` contains the preview manifest and input identities; `state.json` holds choices independently from discovery/alignment status. Snapshot events, placement plan and probes stay beside them. Writes replace the state atomically after validation; revision conflicts stop the second tab instead of overwriting the first tab's changes. Reload after a conflict. Preserve the whole folder for portability together with access to the original media; file-path changes need explicit remapping, not silent identity reuse.

**Export kept moments** filters source markers and authored alternate excerpts to Keep decisions. It retains the complete main VOD chronology, the original source clocks, media/POV bins, disabled alternate picture/audio and grouped stereo. Independent secondary-only kept moments remain available as source markers in their POV bin; they are not placed at invented main times. Related references can still point to unselected events by source time, without selecting their markers. **Export all moments**, under Review coverage, includes every discovery regardless of review choices.

Each export creates a new `exports/review-r<revision>-<unique>/` containing `review.xml`, `decisions.json` and `selection.json`. Notes remain in the saved decisions, not marker names. Export validates original media size/mtime and discovery snapshot/input hashes first. Changed inputs require a new queue; automatic decision migration is not implemented. The same queue can export repeatedly without overwriting past exports or a Premiere project.

Download/import the XML into a new Premiere review project. Use Shift+1, expand `02 Sequences`, and open the sequence. Reimport is not a live update of an existing timeline. Mixed-resolution alternate fitting and actual Premiere playback still need the checks in [timeline.md](timeline.md); this dashboard does not operate Premiere.

## Assess whether it helps

The fatigue benefit is a hypothesis until the editor tries it. A useful first trial is five to ten existing moments, a break/restart, then revisiting Later. Ask whether it avoided rewatching/re-finding footage, whether the context was sufficient, and whether the extra handoff was worthwhile. No completion target or forced daily quota is needed. If the extra application increases friction, retain direct Premiere markers and use the queue only when helpful.
