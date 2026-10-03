# Saved local review queue

Use this when the editor wants to make and resume Keep/Later/Skip decisions outside Premiere. It is optional: ordinary discovery still exports markers directly. The dashboard presents one evidenced moment at a time, short factual copy, individual POV previews, checks, related moments, notes and reversible choices. Do not preselect Keep, hide uncertain candidates, impose a top-N limit, or equate clicking Keep with verifying alignment.

## Build and run

Requires Python 3.10+, FFmpeg and ffprobe on PATH. It uses the existing event and timeline adapters plus browser-native video; there are no npm packages, cloud services or new Python dependencies. Inputs are the complete validated `events.json` and an authored `timeline-plan.json` with stable `event_id` on every alternate. The existing XML constraints apply: one video and at most one mono/stereo audio stream per source, compatible main rates and supported source timecode. Unsupported audio layouts fail before rendering; no streams are silently dropped.

```powershell
python <skill>/scripts/review_queue.py init --events outputs/events.json --plan outputs/timeline-plan.json --out outputs/review-queue
python <skill>/scripts/review_queue.py serve --queue outputs/review-queue --port 8765 --open
```

`init` starts in a new directory and prepares every supplied perspective with three seconds of context on each side, clipped to media bounds. It runs at most two preview encodes concurrently by default; use `--jobs 1` for serial encoding or an explicit positive worker count to suit the machine. Each encode has bounded decoder, encoder and filter threads. Previews use 960-pixel width, 24 fps, H.264 and AAC. Full source times and original media paths remain authoritative. This is preview transcoding, not additional discovery or audio transcription. Runtime/storage grow with the supplied event ranges. Start with a bounded pilot rather than rendering an entire session speculatively.

A failed or interrupted build retains validated previews and a `build.json` checkpoint. It is not serveable until all previews pass validation. Resume with the same inputs and padding:

```powershell
python <skill>/scripts/review_queue.py init --events outputs/events.json --plan outputs/timeline-plan.json --out outputs/review-queue --resume
```

Resume checks input hashes, source paths/size/mtime, saved snapshots and preview settings. Completed previews are reused only when their checksums and validated durations match; missing or damaged previews are rebuilt. Changing `--jobs` is allowed. Changed discovery inputs, media or padding require a new output folder. Builds made before checkpoints were introduced also require a fresh folder after failure. A separate OS lock prevents two processes preparing the same queue. To resume a completed queue, run `serve`; `init --resume` refuses to replace saved review choices.

The URL is `http://127.0.0.1:8765`. The server binds only to loopback and serves registered previews/assets/exports, not arbitrary local files. It requires same-origin authenticated writes, detects conflicting tabs, and holds a process lock on this queue. On Windows launch background helpers with a hidden window and redirected logs. A queue in another folder may use another port. Stopping the server does not erase choices; restart it to continue.

## Editor experience

- Default order: main POV chronology, then independent secondary moments in their own source order. This is not a combined synchronized clock.
- Default keys: `1` Keep, `2` Later, `3` Skip, `U` Undo. Left/right arrows change moments; Shift + left/right seeks five seconds. `P` cycles available POVs; Shift + P cycles backwards. Space plays/pauses. **Keys** changes each binding, rejects duplicates and restores defaults. Bind letters, numbers, navigation or punctuation keys, optionally with Shift; browser control combinations and Escape are reserved. Hints update with the saved bindings. Shortcuts do not intercept note entry, select/range controls or the key editor. Each choice saves before moving forward.
- Keep means potentially useful. Later preserves uncertainty. Skip is recoverable and deletes neither discoveries nor footage. No decision is made from playback completion or preview failure.
- Auto-save preserves each moment's note, chosen preview, playback position and current moment. Playback position saves approximately every five seconds and on pause/navigation. Wait for **Saved** before closing. A crashed browser may lose the last few seconds of position or an unconfirmed note, not previously confirmed choices.
- Position and note saves leave the moment list intact. Navigation reuses existing rows, retaining keyboard focus and list scroll; decision and filter changes update the relevant list contents.
- POV buttons and `P` translate the current source timestamp through that event's authored local anchor, then subtract the destination preview's source start. They do not use stale saved alternate positions. Translation is allowed only inside each traversed anchor's authored excerpt and the destination preview's bounds; unavailable buttons are disabled. Missing anchors and earlier/later related events do not produce simultaneous switching. Offsets are event-specific, never a whole-VOD drift correction. Switching between two alternatives can use their shared main anchor, conservatively summing uncertainty. The UI displays the plan's timing uncertainty; synchronized navigation does not improve underlying timing precision.
- Moment navigation and successful POV switches autoplay, including after a pause. On initial browser autoplay rejection, playback starts muted with an **Enable sound** button; user interaction enables audio. Ordinary pausing and seeking do not force playback. Each POV plays its own audio in the browser; Premiere exports keep the main picture/audio enabled and alternative picture/audio disabled.
- The selected **B** layout places a large player on the left and a timeline/moment list on the right. The neutral dark interface keeps notes and help behind buttons. On narrow screens, **Timeline** opens the sidebar. Current source time, brief factual description, uncertainty and material review checks remain visible.
- The overview spans the complete main chronology, including subsequent source parts; part origins use the exporter's frame rounding. The detail view supports zoom, pan, Full VOD and Moment. Relevant alternatives appear in separate lanes above the main. Clicking a clip seeks to that main-timeline position and switches to its POV; Enter/Space on a focused clip starts its excerpt. Source-local clocks remain separately visible. Clips without a supported local anchor stay in the moment list without a false timeline placement. Timing uncertainty is available on clip tooltips and the player.
- The browser plays prepared moment previews only. Clicking an unprepared timeline range pauses playback, covers the previous picture, and disables decisions until returning to a prepared moment. The full VOD bar is context, not evidence that its whole duration has been reviewed. Zoom in when clips or targets are too small to choose accurately.
- Filter to Later to revisit unresolved choices. Related-event buttons navigate to the earlier/later event without moving its media to a false simultaneous position.
- Undo restores the last decision, including after restart, while preserving notes and playback positions. The complete history and all candidates remain in the queue folder.

## Save and export contract

Sync links and timeline geometry are derived at runtime from the validated snapshots. Existing queue manifests and state hashes remain unchanged, so upgrading the interface preserves choices, notes, history and positions without re-encoding previews or migrating decisions.

Keyboard settings are shared across queues and localhost ports on this computer. Windows stores them at `%LOCALAPPDATA%/vod-discovery/keybinds.json`; other systems use `$XDG_CONFIG_HOME/vod-discovery/keybinds.json` or `~/.config/vod-discovery/keybinds.json`. Opening Keys refreshes settings from other projects; returning focus to the browser refreshes them too. Writes use an atomic replacement, a separate OS file lock and an independent revision to prevent concurrent projects overwriting changes. Settings never modify queue decisions. For isolated testing, `serve --preferences <temporary-profile.json>` overrides the shared path. Do not use the editor's real profile or queue for automated decision tests.

`queue.json` contains the preview manifest and input identities; `state.json` holds choices independently from discovery/alignment status. Snapshot events, placement plan and probes stay beside them. Writes replace the state atomically after validation; revision conflicts stop the second tab instead of overwriting the first tab's changes. Reload after a conflict. Preserve the whole folder for portability together with access to the original media; file-path changes need explicit remapping, not silent identity reuse.

**Export kept moments** filters source markers and authored alternate excerpts to Keep decisions. It retains the complete main VOD chronology, the original source clocks, media/POV bins, disabled alternate picture/audio and grouped stereo. Independent secondary-only kept moments remain available as source markers in their POV bin; they are not placed at invented main times. Related references can still point to unselected events by source time, without selecting their markers. **Export all moments**, under Review coverage, includes every discovery regardless of review choices.

Each export creates a new `exports/review-r<revision>-<unique>/` containing `review.xml`, `decisions.json` and `selection.json`. Notes remain in the saved decisions, not marker names. Export validates original media size/mtime and discovery snapshot/input hashes first. Changed inputs require a new queue; automatic decision migration is not implemented. The same queue can export repeatedly without overwriting past exports or a Premiere project.

Download/import the XML into a new Premiere review project. Use Shift+1, expand `02 Sequences`, and open the sequence. Reimport is not a live update of an existing timeline. Mixed-resolution alternate fitting and actual Premiere playback still need the checks in [timeline.md](timeline.md); this dashboard does not operate Premiere.

## Assess whether it helps

The fatigue benefit is a hypothesis until the editor tries it. A useful first trial is five to ten existing moments, a break/restart, then revisiting Later. Ask whether it avoided rewatching/re-finding footage, whether the context was sufficient, and whether the extra handoff was worthwhile. No completion target or forced daily quota is needed. If the extra application increases friction, retain direct Premiere markers and use the queue only when helpful.
