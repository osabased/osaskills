# Local validation — 2026-10-03

## Vulkan transcription and semantic retrieval — pilot and integration checks

The skill now has a selectable whisper.cpp backend for `prepare` and a separate `semantic.py` retrieval helper. Forty-two Python tests, the Node Premiere host mock, the skill validator and the isolated semantic dependency check pass. Added tests cover millisecond/source-clock conversion, stream identity, actual backend selection, per-stream context construction, long-text preservation, overlap grouping, stale evidence, failed rebuild preservation and changed embedding artifacts.

whisper.cpp v1.9.4 (`927cfce34f31707e17f2bff35c349632fb9e2c3a`) was built with Vulkan using local MSVC/CMake and unpacked LunarG 1.4.357.0 development files. The runtime log confirms the AMD Radeon RX 5700 XT and selection of `Vulkan0`. No driver or system SDK installation was performed. The original long build path exceeded MSBuild's path limit; the build used a shorter folder and the resulting executable/DLLs were copied into the project.

Reusable local runtime and models:

- CLI: `work/whisper-runtime/whisper-cli.exe`
- GGML model: `work/downloads/ggml-small.en-q5_1.bin`
- Semantic Python: `work/semantic-env/Scripts/python.exe`
- Semantic model folder: `work/semantic-model`

These dependencies are not bundled with the skill archive or GitHub copy. Check their presence and recorded hashes before reuse; [speech-search.md](speech-search.md) contains portable setup and commands.

One 40-second Johan sample took 8.55 seconds through Vulkan versus 10.37 seconds through CPU with the same small.en-q5_1 model, including CLI startup: about 1.21x speed. This single sample does not predict whole-session throughput. Both original five-minute copies were prepared into **fresh** folders (`work/valorantsmp-pilot/whisper-johan` and `whisper-josh`). Each completed two overlapping packets; the new Johan preparation resumed with zero packets reprocessed. Its transcript includes opening dialogue absent from the earlier tiny-model output, but names and other wording still differ or are wrong. No human-reference error rate was measured for real footage, and the model/quantization/VAD settings differ from the old pilot.

A generated 14-second video with two actual audio streams recovered both known speech scripts in the first packet. The second packet starts at source second 6 and retains independent stream IDs and source-local times. A non-speech placeholder extending beyond its packet is preserved as invalid evidence. The real pilot's new transcript index similarly flags one tail segment instead of clamping it. Older transcripts and discovery decisions remain available.

Semantic retrieval uses FastEmbed 0.8.1, ONNX Runtime 1.30.0 and the pinned English BGE-small model, with no PyTorch or database server. It indexed 127 valid transcript rows into 250 individual/context passages across the two newly prepared POVs, reused the unchanged index, and ran with model downloads disabled. Four paraphrased/control queries were tested. A query about watching instead of helping retrieved Johan's matching complaint at 261.12 seconds first. Initially, indexing only broad context diluted that query; adding individual statements resolved this example. Every returned hit's text slice, source time, stream and raw segment reference was verified. Queries after the first model load took about 0.3 seconds on this small corpus.

An unrelated spaceship/surgery query still returned nearest passages. Similarity is not calibrated confidence; no score cutoff or automatic event promotion was added. This pilot does not establish full-session recall, broad semantic accuracy, non-English performance, speaker identity or frame-accurate audio/visual sync. Raw ASR and search output do not update approved events or XML by themselves. No Premiere import or full-length VOD discovery was performed.

See `review/whisper-semantic-verification.json` in the pilot output for the measured runs, provenance, query results, synthetic checks and artifact paths.

## Optional audio matching and OCR — bounded pilot

Added `audio_match.py`, a pinned optional Audalign requirements file, and `ocr_frames.ps1`; commands and limits are in [optional-tools.md](optional-tools.md). The core preparation requirements remain unchanged. Thirty-three Python tests, the Node Premiere host mock, the skill validator and isolated Audalign dependency check pass.

Audalign 1.3.1 was installed in a separate Python 3.12.14 environment at `work/audalign-env/Scripts/python.exe`. Its pins include NumPy 1.26.4 and SciPy 1.12.0; do not mix it into the main Python 3.13 environment. NumPy import stalled in the restricted sandbox and completed outside it; the exact cause was not established. Bounded local matching runs succeeded outside that sandbox. This observation does not establish that every installation needs broader permissions.

Eighteen method/case trials compared fingerprinting, waveform correlation and spectrogram correlation on three real local windows, unrelated footage, a known +2-second delay, and independent synthetic noise. The delay established offset direction. Fingerprinting and waveform correlation agreed around the truce (+81.652 seconds B minus A) and fight (+82.04175 seconds). The later window, unrelated footage and noise remained unresolved under the helper's pilot heuristics. The thresholds were chosen using these examples, not validated on an independent dataset. Spectrogram correlation assigned the independent noise its top rank and normalized score; it is not included in the helper.

The bundled helper reproduced both real candidates and the unrelated-pair rejection end to end using the five-minute video copies. The final version also verified source size/mtime provenance and analysis WAV hashes. Its output remains a review candidate, not a visually verified anchor. This does not validate whole-VOD drift, shared-music cases, frame-accurate picture sync, or full-session recall.

Windows.Media.Ocr with the installed `en-US` language processed four source-timed detail frames. Kill-notice text was detected at Johan 113 seconds and Josh 195 seconds, absent in the preceding 112/194-second samples. Some names and words were misread; raw text and word rectangles are retained. Source timestamps/image hashes, negative-timestamp rejection and preservation of existing output were checked. The machine's execution policy blocked `-File`; the inspected helper ran as a command block without changing that policy. No native UI control or cloud OCR was used.

`review/tool-trial-verification.json` in the pilot output records the controls, raw-result locations, helper runs and OCR checks. These optional tools do not alter the approved events, marker XML, audio grouping or timeline placements. No new Premiere import or full-session discovery was performed.

## Transcript search and joined evidence — adapter and pilot verification

The skill now reuses CRV 0.10.7 `timeline_lite.build_spans` and `memory.remember/search`. Preparation produces source-timed joined evidence, with independent audio-stream views and explicit nearby-frame labels. A project-local index aggregates all completed packets per VOD before indexing; search preserves exact occurrence references and rejects stale prepared inputs.

Twenty-nine Python tests and the Node host mock pass. New tests exercise nonzero packet starts, simultaneous audio streams, speech gaps, invalid transcript bounds, cross-POV search, overlapping packets, literal punctuation, repeated events, index reuse/rebuild, failed rebuild preservation, and visible result limits. Testing caught CRV's shared frame-dictionary references causing repeated time offsets across audio streams; independent copies fixed the adapter before delivery.

The original five-minute Johan/Josh pilot now has 162 searchable transcript lines and joined evidence for both packets. One Josh transcript segment outside the clip duration is retained and flagged, but excluded from joined speech and search. Searches for `truce`, `kill`, and `Josh` returned source-local references checked against the exact raw segments. `Johan` and `fog` returned no hits in the rough tiny-model transcripts, illustrating why search must supplement visual review. Raw transcripts, frame maps, and review ledgers were unchanged by enrichment. The pilot resumed with zero packets reprocessed. A fresh 12-second generated visual-only source produced three overlapping packets with every frame timestamp retained in joined evidence. See `review/discovery-tools-verification.json` in the pilot output.

No new full-session discovery, model-quality benchmark, alignment validation or Premiere import was performed for this feature. Requirements are unchanged; no additional packages or models are needed.

## Bin organization revision — offline verification

Both XML exporters now organize source masters under `01 Media` with one bin per POV. Parts sharing the same source `pov` value stay together; original filenames remain visible. Layered review timelines go under `02 Sequences`. Empty bins are omitted. The existing clip elements are moved rather than copied, preserving their IDs and references.

Twenty-one Python tests, the Node host mock, and the official skill validator pass. Added checks cover interleaved POV parts, XML escaping, preserved source labels, empty exports, and sequence references after grouping. All three pilot XML exports were regenerated. `review/bin-verification.json` confirms that every master clip and sequence is internally identical to the pre-bin snapshot, including all 22 source markers, timing, enabled states and stereo grouping. `review/Johan-Organized.xml` is a copy of the current layered export for import.

The user confirmed the preceding short-label import looked fine. This bin revision has been verified at file level only; no Computer Use or native project edits were performed. The user will verify the new bin layout in Premiere. Open the Project panel with Shift+1, then expand `02 Sequences` and open the review sequence. The earlier records below describe the revisions as checked at their respective times.

## Current short-label revision — offline verification

The user requested no Computer Use for this revision and will verify Premiere personally. No `.prproj` was changed or reverified. Previously saved projects and their verification reports below describe the prior marker presentation; the regenerated XML/JSON carries the current names.

All marker paths now use authored 1–4-word labels with factual comments and stable references in comments. The 22 pilot labels are two words, 6–13 characters, with distinct first-ten-character prefixes within each POV. Perspective overrides distinguish a visible fall from its remote death notice. Full analysis/provenance remains in event JSON; source ranges and evidence are preserved.

Eighteen Python tests and the Node host mock pass. Tests cover required authored copy, rejection of legacy metadata-bearing names and mechanical truncation, per-POV labels, preserved uncertainty, XML serialization, short names inside the layered XML, matching comment references, legacy existing-marker detection, repeat imports (including XML comment flattening), duplicate IDs and preservation of human edits. The UXP panel remains mock-tested only. If both its reference and identifying presentation are removed by hand, an existing marker can no longer be reliably associated with its original suggestion.

The six pilot JSON exports and three XML exports were regenerated and checked. `review/naming-verification.json` records all label prefixes and XML hashes. The layered XML is identical to the previous XML apart from marker presentation, including source paths, clip ranges, enabled states and stereo grouping. This is file-level validation, not a new Premiere import test. The previous native Fit to frame step remains in the saved project only.

Follow-up: the user reported that neither XML import showed new items. Their screenshot revealed a hidden Project panel; after being directed to Shift+1, they confirmed this was the issue. Import failure was not established. A diagnostic `Johan-Short-Markers.xml` using native sequence serialization was created during troubleshooting; this does not establish that the original project-wrapper XML was defective or needs replacement. The user has not yet reported a complete marker/timing/audio review of the revised import.

The remaining sections record earlier preparation and Premiere tests.

Pilot Python environment (workspace-relative path; not bundled):

`work/vod-env/Scripts/python.exe`

Pilot model cache (`HF_HOME`, workspace-relative path; not bundled):

`work/model-cache`

The cache contains `tiny` for smoke testing and the first real-footage pilot. The default `small` model is not downloaded or benchmarked. These locations describe the original pilot workspace. Create a local environment and cache as described in setup.md before reuse.

Passing evidence:

- Skill frontmatter and references checked; official skill validator passed.
- Required package installation and `pip check` passed.
- Generated 12-second video: timestamped frames, contact sheets (visually inspected), overlapping packet boundaries, and resume with zero reprocessing.
- A generated file with a 10-second container timestamp offset: detail frames retained playback-relative 4.0–7.5-second timestamps.
- Generated Windows speech, processed with faster-whisper `tiny`, CPU/int8: correctly recovered the boss-defeat and next-area sentences; overlapping packet transcript timestamps stayed source-relative.
- Six deterministic exporter tests: uncertain candidates retained, separate source clocks, invalid intervals/NaN, unknown sources, duplicate paths/IDs, required estimate uncertainty.
- Node test with mocked Premiere host: selected source path matching, marker-owner identity, locked transactions, exact numeric times, repeat import, and preservation of human edits.
- Three XML adapter tests: master-source marker placement and audio file references, escaping and readable comments, bounded fractional frame-rate quantization, and rejection of unsupported layouts/timecode.

The real speech test found PyAV 19 incompatible with faster-whisper 1.2.1 (`metadata_errors` was removed); pinning PyAV 16.0.1 fixed it. Preserve the tested constraint until revalidated.

Run reusable checks with:

```powershell
python -m unittest discover -s <skill>/tests -v
node <skill>/tests/test_panel.js
```

## Real-footage pilot

Output directory: `outputs/valorantsmp-pilot`.

First five minutes of JohanFootage/1800johan_part1.mp4 and JoshFootage/Josh_Pov.mp4, copied with FFmpeg without overwriting originals. All 157 overview frames, 19 detail frames, and both rough transcripts were inspected. Review ledgers distinguish supplied-evidence review from continuous video coverage. Result: 17 candidate/context/uncertain events, five with matched POV coverage, 22 markers (Johan 10, Josh 12).

A shared Mesaakk kill notice was absent/present at Johan 112/113 seconds and Josh 194/195 seconds, establishing a local offset of about +82 seconds, with one-second sampling uncertainty. This is evidence for this event, not a drift curve or a global offset. Other matches use their own source intervals. Johan's later complaint about Josh watching is retrospective; Josh's activity during Johan's death is a separate conversation and death notice, not a verified reaction.

Native XML was imported into installed Premiere Pro 2026. Both source monitors displayed the correct footage and source markers. Josh's matching kill notice was checked at 03:15. The saved `VOD Discovery Pilot.prproj` was inspected read-only: both source marker owners, counts, names, start times, durations, comments and file paths were compared to the export. No sequence was created. The XML adapter is the proven pilot delivery route; the UXP panel is still mock-tested only.

Quality limitations: tiny missed Johan's opening speech, garbled some names/goals, and gave a Josh tail segment an end beyond the recording duration. Those defects are retained in the raw transcript and noted in the review; marker intervals remain within media duration. Sampled frames do not establish exhaustive recall. The first five minutes do not test long-run drift, hours of preparation, or general event quality across genres.

Still unverified: live UXP panel behavior, subclips/modified timecodes, full multi-audio workloads, fractional rates in Premiere, long-run speed/storage, and full-session recall. Do not generalize the pilot to these cases.

## Concise presentation revision

The editor found the first descriptions too long. The revised `VOD Discovery - concise.prproj` puts short event titles first and moves raw evidence out of marker comments. Comment copy fell from 1,303 to 241 words across the same 22 markers. All original event IDs, intervals, status, rationale and evidence remain in the event JSON. A linked earlier Josh event now appears explicitly on Johan's later complaint.

Eleven Python tests and the host mock pass, including independent source clocks, related-event resolution, retained analysis evidence, preserved checks, and both old/new marker-ID positions. The revised project was imported and saved in Premiere; source names, owners, marker names, exact times, durations and concise comments were verified against the export. The shorter Johan comments were visually checked in Premiere's Markers panel. The original project and the user's sequence were left open separately.

## Factual markers, layered timeline, and stereo audio revision

`VOD Discovery - layered review.prproj` uses the original full Johan part 1 and part 2 on V1/A1, in filename order. Five locally placed Josh excerpts occupy V2/A2, with both their picture and stereo audio disabled. All 22 source markers now describe observed actions rather than editorial purpose. Review remains limited to the opening five minutes of two sources; the full main duration does not imply further discovery coverage. Local placement uncertainty is 1–5 seconds. Earlier Josh spectator footage remains linked to Johan’s later complaint, not moved to that later time.

The previous XML split a stereo stream into two mono groups. Grouped FCP channel records now produce one Premiere stereo group with source channels 0 and 1. A native New Sequence From Clip test produced one populated A1 track with A2 empty. Multi-stream XML remains unsupported and fails explicitly; it must never discard real additional streams.

The layered import exposed two integration faults, now corrected: Windows URLs must follow Premiere’s `file://localhost/C%3a/...` encoding; sequence In/Out values use sequence-rate frames for mixed-rate sources. The first bad timeline import was moved into the work folder. The corrected project imported its three original source paths without a relink prompt. Fifteen Python tests pass. Saved-project checks verify marker owners/copy/times, complete main parts, exact alternate source and timeline ranges, disabled states, and one stereo group per source with L/R retained.

In the final native project, all five 720p Josh clips were fitted to the 1080p sequence using **Fit to frame**. Enabling the truce alternate displayed Josh full-frame; returning it to disabled restored Johan. Brief playback showed Johan and active stereo meters. The saved project, not raw XML alone, includes this native framing step; see timeline.md.

## Saved review queue

The local browser pilot contains all 17 existing moments and 22 separate POV previews, with three-second context handles where media bounds allow. No additional footage discovery or new alignment was inferred. Decisions are saved separately from evidence and remain initially unreviewed for the editor.

Nine queue tests cover persisted choices/positions/notes, Undo after reload, conflicting revisions, invalid writes preserving previous state, selected/all XML exports, unselected related-event references, unchanged full main chronology, disabled alternate video/audio, stereo grouping, changed-media rejection, unique export snapshots, HTTP byte ranges, request/path restrictions and occupied-port rejection. Together with existing adapters, the Python suite contains 51 passing tests. The Premiere panel mock and skill validator also pass. Nine browser checks passed on a disposable copy of the actual pilot queue: media playback, note entry, navigation/reload, Keep/Later/Skip/Undo, alternate-view resume, revisiting Later, XML handoff, conflicting tabs and narrow layout. The editor's queue is not populated with test choices.

This adds a review interface, not measured proof of lower fatigue or full-session recall. The new selected XML is checked structurally; its actual Premiere import is left to the editor. The previous XML adapter's host verification remains the basis for layout/audio behavior.

The compact dark playback revision adds bounded local-anchor POV switching, P/Shift+P cycling, arrow-key moment navigation, Shift-arrow seeking and autoplay with a muted fallback when browser policy blocks sound. The Python suite now has 52 passing tests; Node playback checks cover reversible clocks, event-specific offsets, missing anchors, non-overlap and multiple alternatives. Eleven browser checks passed against disposable real-footage previews, including Johan 80.00s to Josh 162.91s using the truce anchor, reverse switching, independent fight timing, saved note/choice preservation, autoplay fallback (simulated policy rejection), export and desktop/narrow layout. This validates clock translation, not more accurate underlying sync than the existing ±1–5s anchors. Runtime playback metadata leaves queue/state files unchanged.

The editor selected prototype B, with timeline and moment navigation beside the player. The production version adds stacked local alternate clips, full-main overview, zoom/pan and click-to-seek/POV switching. Editable shortcuts persist across projects through a shared profile rather than port-specific browser storage. The Python suite has 55 passing tests, including exported part-origin rounding, no invented placement for independent moments, profile validation, conflicting revisions and cross-instance OS locks. The existing Node suites pass. Seventeen browser checks passed on disposable real-footage queues and a temporary keyboard profile: prior playback/decision/export behavior, sidebar responsiveness, stacked clip seeking, no-preview ranges disabling decisions, unanchored moments, duplicate shortcut rejection, remapping/reload, and a second project on another port reading and resetting the same profile. Desktop, narrow and key-editor renders were inspected. These checks leave original discovery evidence and the editor's decisions untouched; they do not establish additional footage coverage or measured fatigue reduction.

## Review queue optimizations (2026-10-03)

Preview builds now use two concurrent encodes by default, with bounded FFmpeg decoder/encoder/filter threads and configurable `--jobs`. Per-preview checksums and validated durations allow `init --resume` to reuse successful work after a failure. Resume rejects changed inputs, media, snapshots or preview settings, repairs damaged previews, holds an OS build lock and refuses completed queues. Validated files replace temporary encodes atomically; `queue.json` is published after initial state. Interruption cancels encodes that have not started. Existing completed manifests and saved choices require no migration.

The server caches the immutable manifest hash and preview filename registry and groups playback links by event in one pass. The browser skips list work on position/note saves, reuses list rows across navigation/filtering and indexes cards for lookups. The Python suite has 62 passing tests in the existing VOD environment. The Node UI, playback and Premiere panel checks pass; the 500-row UI fixture verifies no new list nodes or list replacement during autosave, retained row identity/focus on navigation, decision/filter updates and restored state.

An actual FFmpeg trial used two generated 18-second 1080p60 sources with stereo audio, four synthetic moments and eight previews. Serial baseline preparation took 6.52 seconds; the optimized two-job build took 5.72 seconds. These are single measurements with the baseline first, so cache/order and synthetic content limit generalization. A real failed build resumed while retaining verified preview mtimes. Queue manifests, initial saved state and kept Premiere XML were identical to the baseline. This is file-level export validation, not another Premiere host test.

On a synthetic 2,000-moment/two-POV queue, seven-run median state reads fell from 13.75 to 2.27 milliseconds and playback metadata generation from 217.51 to 34.04 milliseconds. Those are isolated backend operations, not end-to-end user latency. Browser checks on a disposable generated-media queue and temporary keyboard profile verified playback, timeline seeking, local-anchor POV switching, notes, Later/Undo, empty/All filters, keyboard navigation and reload persistence. The browser reported no console errors and the rendered queue was inspected. No original footage, editor queue decisions or shared keyboard profile was changed.

## Processing caches and benchmark harness (2026-10-04)

Preparation now caches frames/contact sheets, decoded audio, and each stream's transcript independently. Stage snapshots are checksum-verified, published atomically under an OS lock, and copied into attempts. Failed/corrupt snapshots retain diagnostics; source changes prevent publication. A separate effective-ASR identity record prevents a resumed partial output from mixing speech models. Existing completed packet/review formats remain intact. Older partial faster-whisper outputs lack effective model provenance and need a fresh output; existing fully completed folders still resume without model loading. Semantic builds cache exact passage text under model/policy/recipe identities, validate normalized vectors, and refresh source/stream/occurrence references even when vectors are reused.

The existing VOD environment passes 103 Python tests, including 20 preparation/cache tests, 15 semantic tests and 12 benchmark tests. They cover failed-stream retries, corrupt stages, model/settings invalidation, effective weights changing between packets, quiet/visual-only paths, retained reviews, copied diagnostics, interrupted embedding batches, stale judgments, duplicates/repeated attempts, wrong POV links, pending judgments and partially reviewed candidates. The existing Node UI/playback/Premiere panel checks and skill validator pass. Independent review caught and verified fixes for model mixing and premature benchmark miss lists.

A bounded real-tool trial used the existing 6.898-second spoken software fixture in two overlapping packets, CRV/FFmpeg, the verified whisper.cpp Vulkan runtime and its English model. One ordered baseline run took 12.66 seconds; a new cold cached preparation took 12.24 seconds; a fresh output using all six cached stages took 0.88 seconds. Changing Whisper thread settings regenerated both transcripts while reusing both frame and audio stages. Source-local frame, packet and transcript values matched the baseline; completed review notes were retained. A deliberately damaged cached JPEG rebuilt only its visual stage while both audio/transcript stages remained reusable. These single tiny-fixture measurements do not establish full-VOD throughput or discovery recall; checksum/copy costs and retained caches add storage.

Real semantic inference produced five passage embeddings from the fixture. Rebuilding the literal index against a different prepared output reused all five vectors and emitted current transcript references. Cold semantic indexing took 4.33 seconds and the cached rebuild 1.55 seconds in these ordered trials; model initialization remained. Existing local search still returned exact source/stream/segment references. No new model downloads or production evidence changes were needed.

`benchmark.py` scaffolds reviewed references and explicit observation/POV judgments, scores only adjudicated results, and records externally measured wall time plus enumerated artifact storage excluding original media. Pending observations and partial reviewed coverage suppress definitive miss/recall fields. The tests are synthetic software fixtures. A local pending reference was seeded from the existing 17-moment sampled Johan/Josh pilot for future authoring; no new discovery run was judged and no real discovery-quality score is claimed. Add independently reviewed quiet setup, repeated attempts and misleading POV cases before using it as a quality benchmark. Real process termination, hours-long cache costs and full-session recall remain unmeasured.

## Persistent inference workers (2026-10-04)

Three alternating-order trials compared fresh inference processes with resident models on the existing local pilot. Four semantic queries over the two-POV five-minute transcript index took a median 6.70 seconds through separate CLI processes and 1.82 seconds with one JSON-lines worker, including its startup (73% less elapsed time). Worker query latency after readiness had a median 0.085 seconds. All complete result objects, including ranking scores and exact evidence references, were identical in all trials. Strict input/model/artifact validation still runs for every query.

The final whisper.cpp worker adapter processed an A/B/A request group of 40-, 45- and 40-second English Johan/Josh audio windows. Its median group time was 23.76 seconds versus 31.52 seconds for separate CLI processes (25% less elapsed time), including worker startup, runtime checks, response conversion/logging and shutdown. Both used the same model and runtime DLLs with Vulkan confirmed in logs. Server defaults differ from the CLI, so the adapter explicitly matches beam/best-of, temperature, context and segment-timestamp settings. Normalized transcript text and source-offset timestamps matched exactly for every request across all three trials; repeating A after B produced the same result. The input WAVs were standardized to the preparation pipeline's mono 16 kHz PCM16 format before timing.

A separate preparation integration check covered the first 61 seconds of the existing Johan pilot in three overlapping packets. CLI and worker packet/frame/transcript values matched. Switching transport reused all three frame and audio stages and computed separately identified worker transcripts. A fresh fully cached worker run reused all nine stages without starting a server. The owned server exited after preparation, and the earlier output's review note remained intact. This was an equivalence/lifecycle check, not another discovery pass.

The Python suite has 117 passing tests. New cases cover warm model reuse, stale raw evidence and vectors, refreshed index references, changed model rejection, invalid/oversized worker requests, transcript bounds/stream conversion, audio/runtime compatibility, lazy startup, process cleanup and failed-request diagnostics. The three existing Node suites and skill validator pass. `search-many` also matched the standalone real search results. Measurements use this machine and bounded inputs; model residency retains memory during a run, and no hours-long throughput, independent discovery recall, or forced-parent-termination recovery claim is made. Performance/storage records use the benchmark harness; original media, discovery evidence, review decisions and Premiere files remain untouched.

## Unified evidence search and AMD preview trial (2026-10-04)

The standalone `unified_search.py` now indexes the existing literal aggregates and explicitly supplied OCR reports using local SQLite FTS5. Exact and ranked keyword results combine with optional existing semantic speech results through reciprocal rank fusion. Hits retain source clocks, audio streams or sampled frame points, raw text, exact segment/report/map references and hashes. OCR aliases require explicit mappings to the indexed source path, and image clocks must match a prepared or selected detail frame map. Query batches reuse one semantic session. Missing optional channels, limits, OCR preparation coverage and invalid transcript exclusions remain visible; stale inputs and requested channel failures reject the search. Index snapshots publish through unique temporary files and queries revalidate their captured snapshot before returning.

The existing VOD environment passed 138 Python tests, including 21 new unified-search cases; the three Node suites and skill validator passed. Independent review found and verified fixes for concurrent rebuilds returning stale hits, competing pointer writes, and evidence references pointing to another source. Tests also cover distinct streams and repeated speech, overlap provenance, integer/float clock identity, OCR point timing and aliases, empty OCR, limits, unavailable channels, changed evidence and semantic-session reuse.

A read-only integration trial used the existing two-POV five-minute English transcript/semantic index and four selected Windows OCR frames. Searches for a truce, a raw OCR notice and an off-screen spectator idea exercised all indexed channels. Visible-text hits preserved their exact 112/113 and 194/195-second clocks, image/map/report references and misspellings; speech hits were checked against their original transcript segments and audio streams. The first query initialized the local model, and subsequent queries reused it. No new models, OCR runs, discovery annotations or production evidence changes were required. This validates retrieval and provenance; it does not establish independently measured discovery recall or lower investigation fatigue.

An actual RX 5700 XT/AMF trial compared the current libx264 veryfast CRF 25 previews with AMF quality/CQP I/P/B 22/25/27. Three 18-second original gameplay clips (two Johan 1080p60 ranges and one Josh 720p/~30fps range) were rendered at 960x540/24fps with the same software decode/scale and stereo AAC. Three interleaved individual runs per backend had summed clip medians of 8.39 seconds CPU and 7.89 seconds AMF. Three interleaved two-worker encode/probe/checksum batches had medians of 6.63 and 5.70 seconds, respectively. AMF files were 1.81 times larger and had higher SSIM; the profiles were not quality-equivalent. Selected HUD/chat/notice text remained readable in both in three frame spot checks. GOP/scene-cut and B-frame behavior differed, so seek cost cannot be attributed to the encoder alone.

All six representative files played to completion in the browser and passed 18 seeks at 1.25, 8.25 and 15.25 seconds within one output frame. A disposable HTTP byte-range server matched the dashboard's streaming behavior; an initial server lacking ranges was excluded. These are playback compatibility checks rather than comparative browser latency measurements. The batch excludes queue initialization, checkpoint publication and atomic preview renames, and the active machine/small clip set limit generalization. Keep libx264 as the default until a broader size/quality and whole-workflow comparison supports switching. The benchmark did not change drivers, original media, Premiere projects or real queue decisions; its temporary browser tab and server were closed.

## On-demand context and review migration (2026-10-04)

The queue now adds fifteen seconds of preview context per side through compact controls and configurable shortcuts. It keeps source-clock positions, current moment, notes and choices while encoding, and preserves playing/paused state when replacing the preview. Context metadata stays separate from the immutable queue and saved decision binding. Cached files publish atomically after validation; matching concurrent requests coalesce, retries use the original requested bounds, and other requests remain bounded by two workers. Previous URLs stay registered. Restart checks and repairs missing/damaged current context before serving it. Expanded playback ranges never expand authored local-anchor windows or Premiere exports.

`update` builds a separate revised queue from a frozen prior decision snapshot. Stable IDs or explicit one-to-one rename maps establish a match; source identity/layout, authored content and evidence prose, ranges, roles, uncertainty, anchors, related references and main placement determine whether prior review still applies. Only unchanged material carries decisions; changed material keeps the note but requires reconsideration. Structured evidence locators and operational coverage/title metadata alone do not reset review. New and ambiguous IDs receive no previous decision; removed choices remain archived. Prior snapshots retain their exact bytes/hash bindings, and ancestor snapshots carry through subsequent updates without reactivating changed decisions. Matching selected POV/source positions and requested context survive on unchanged material. Revised-input and media checks, active-server locks and donor-state checks protect fresh and resumed updates.

The existing local VOD environment passed 167 Python tests, including 29 new outcome/compatibility cases; the three Node suites and skill validator passed. Cases cover old queues and customized keyboard profiles, source positions in added context, unchanged export bytes, bounded/coalesced requests, encoder/publication/source-change failures, cache repair, HTTP restrictions, changed versus unchanged material, new/removed/repeated moments, explicit-map collisions, revised external inputs, active donors, failed-update resume, exact archives and repeated-update history. The server acquires its process lock before startup cache repair; a second server cannot write context before refusing. Node playback checks exercise rebasing and legacy resume while retaining strict authored anchor bounds.

A generated-media integration trial used two 90-second 30fps VODs, each with one actual stereo audio stream. Twelve browser checks exercised local FFmpeg extensions, a note changed during encoding, paused and playing replacement, reload at an added source position, shortcut configuration/duplicate rejection, failed-request retry, media bounds, anchor-limited POV switching, selected XML export, real queue migration and visible reconsideration. Desktop/narrow layouts were inspected and the browser reported no script errors. This is software behavior validation on isolated media, queues and preferences; the editor's real choices, shared profile, originals and Premiere project were not used for writes. No new model or dependency was installed. Live Premiere verification and any fatigue/discovery-quality benefit remain unmeasured.

Workspace-based automated trials also encountered external suspension of the actual Python interpreter. An independent diagnostic pass found its main and worker threads in the Windows `Suspended` wait state after a state save had completed; heartbeat and thread dumps stopped together. The same backend passed the complete browser workflow with generated queues in the temporary directory. The responsible software and behavior under the editor's normal launch remain unidentified. Those stalled workspace trials are not counted as passes. Saves and context requests now have bounded HTTP waits; a Node outcome check verifies an unanswered save exposes recovery and retains confirmed state rather than showing Saving indefinitely. This surfaces a stopped server; it does not resume an externally suspended process.
