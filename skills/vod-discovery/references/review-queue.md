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
- **← 15s** and **15s →** add context to the current POV without leaving the moment. Defaults are `[` and `]`, configurable in **Keys**. Each request expands the prepared interval by up to fifteen source seconds, clipped to media bounds. Preparation runs locally with the existing FFmpeg recipe and at most two workers; you can keep watching, writing notes or navigating while it runs. The player resumes at its source timestamp when the new file becomes ready, preserving whether it was paused. A small pending/error message accompanies the controls; retrying a failed request does not add a second increment. Longer previews never expand the event boundaries, export ranges or verified anchor excerpts.
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

Older keyboard profiles retain every customized binding. The two context actions receive unused bindings, preferring their defaults and then Shift variants. Reading an old profile does not rewrite it; the next explicit settings save persists the complete profile. Restart the server and refresh the browser after installing an update that adds backend actions.

`queue.json` contains the preview manifest and input identities; `state.json` holds choices independently from discovery/alignment status. Snapshot events, placement plan and probes stay beside them. Writes replace the state atomically after validation; revision conflicts stop the second tab instead of overwriting the first tab's changes. Reload after a conflict. Preserve the whole folder for portability together with access to the original media; file-path changes need explicit remapping, not silent identity reuse.

On-demand previews publish only after duration, checksum and input/media checks. `context.json` is a separate cache manifest bound to the immutable queue hash; earlier registered preview URLs stay available to other tabs. Failures retain the last completed preview and do not change choices. Startup checksum-checks current context files and repairs missing/damaged files before serving, so a shorter fallback cannot overwrite a source position in added context. A failed repair leaves decisions intact and can be retried by restarting the server. Playback saves use optional `source_positions` in original source seconds; legacy relative `positions` remain readable. An extension does not change `queue.json` or its state binding. Cache files add storage as context grows; retain them with the queue when preserving playback positions in added context.

**Export kept moments** filters source markers and authored alternate excerpts to Keep decisions. It retains the complete main VOD chronology, the original source clocks, media/POV bins, disabled alternate picture/audio and grouped stereo. Independent secondary-only kept moments remain available as source markers in their POV bin; they are not placed at invented main times. Related references can still point to unselected events by source time, without selecting their markers. **Export all moments**, under Review coverage, includes every discovery regardless of review choices.

Each export creates a new `exports/review-r<revision>-<unique>/` containing `review.xml`, `decisions.json` and `selection.json`. Notes remain in the saved decisions, not marker names. Export validates original media size/mtime and discovery snapshot/input hashes first. Changed inputs require a new queue through the update workflow below. The same queue can export repeatedly without overwriting past exports or a Premiere project.

Download/import the XML into a new Premiere review project. Use Shift+1, expand `02 Sequences`, and open the sequence. Reimport is not a live update of an existing timeline. Mixed-resolution alternate fitting and actual Premiere playback still need the checks in [timeline.md](timeline.md); this dashboard does not operate Premiere.

## Update discoveries without losing review choices

Keep event IDs stable across discovery revisions. Stop the old queue server after **Saved**, then create a sibling output folder:

```powershell
python <skill>/scripts/review_queue.py update --from-queue outputs/review-queue --events outputs/events-v2.json --plan outputs/timeline-plan-v2.json --out outputs/review-queue-v2
python <skill>/scripts/review_queue.py serve --queue outputs/review-queue-v2 --port 8765 --open
```

The previous folder, choices, history, previews and exports stay intact. The new folder contains `migration.json` and byte-preserved previous queue/state/evidence/plan/probe/context snapshots under `migration/previous/`. On subsequent updates, older snapshots carry forward under `migration/ancestors/<queue-hash>/`; archived changed choices never reactivate through that history. The report records the donor revision and hash, matches, change reasons and removed IDs. A failed update retains its preview checkpoint; repeat `update` with `--resume` and the same donor, inputs, map and padding. Changed donor decisions or context require a fresh output so resumed work cannot silently miss newer review choices. An active previous server or changed snapshot refuses migration; revised external input files and media can be compared against the preserved old snapshots.

- **Unchanged:** a matching stable ID and unchanged editing material retain Keep/Later/Skip, notes, selected POV, source positions and applicable Undo history. Requested context also carries forward. Perspective order and integer/float representations of the same clock do not cause a new review.
- **Changed:** source path/size/mtime or playback layout, footage ranges, authored descriptions/rationale/checks, freeform evidence prose, roles/alignment/uncertainty, local anchors/excerpts, relevant related-moment references or main placement changes return the moment to **Not reviewed**. Its prior note remains available; the dashboard shows **Reconsider · Previously Keep/Later/Skip** with reasons. The old choice and history stay archived. Compatible source positions are retained; positions outside the revised preview or in changed media remain in the previous snapshot.
- **Operational evidence updates:** additional/reorganized structured `evidence_refs`, `frame_refs`, `transcript_refs`, `packet_refs`, `provenance`, preparation/review locator metadata, project title and coverage text alone do not reset a choice. Freeform evidence prose can change the interpretation and is conservatively material. Unknown authored fields are compared rather than silently ignored.
- **New/removed:** a new ID starts unreviewed; a removed ID stays in the old queue and archived history. Title/time similarity never transfers a decision. Identical repeated material under several old IDs is flagged as ambiguous with possible previous IDs and receives no prior choice.

For deliberately renamed IDs, supply `--event-map path/to/map.json` with explicit one-to-one matches:

```json
{"schema":"vod-review-event-map/v1","matches":[{"event_id":"new-id","previous_id":"old-id"}]}
```

The map establishes identity only; material changes still require reconsideration. It cannot map one previous moment to multiple revised events. Relocated media is considered changed by this workflow; matching a filename or label does not establish original-media identity. The update prepares previews for the revised queue and does not update an existing Premiere project.

## Assess whether it helps

The 2026-10-04 AMD trial confirmed `h264_amf` can encode on the RX 5700 XT. Three actual 18-second gameplay clips, three repeats per backend, and three two-worker batches compared the current libx264 veryfast CRF 25 recipe with AMF quality/CQP 22/25/27. Median encode/probe/checksum batch time fell from 6.63 to 5.70 seconds, but AMF files were 1.81 times larger with higher measured SSIM; these are not equal-quality settings. Both formats passed browser playback and seeking. Keep libx264 as the current default; the helper does not expose an AMF selection flag. A future switch should compare size/quality, readable text and the whole preparation path on representative clips. See [validation.md](validation.md) for the measured scope; an encoder listing alone is insufficient.

The fatigue benefit is a hypothesis until the editor tries it. A useful first trial is five to ten existing moments, a break/restart, then revisiting Later. Ask whether it avoided rewatching/re-finding footage, whether the context was sufficient, and whether the extra handoff was worthwhile. No completion target or forced daily quota is needed. If the extra application increases friction, retain direct Premiere markers and use the queue only when helpful.
