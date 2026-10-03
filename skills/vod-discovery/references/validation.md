# Local validation — 2026-10-03

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
