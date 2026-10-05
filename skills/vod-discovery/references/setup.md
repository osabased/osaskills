# Setup and reuse

## Components and boundaries

- [claude-real-video 0.10.7](https://github.com/HUANGCHIHHUNGLeo/claude-real-video): MIT, existing FFmpeg frame extraction, timestamp mapping, contact sheets, joined frame/transcript spans, and local transcript search. Adapters reuse `core.extract_frames`, `write_frames_json`, `make_grids`, `timeline_lite.build_spans`, and `memory.remember/search`; these interfaces are version-pinned. They avoid the high-level `process` function, which copies the full input into each output and applies deduplication/caps. No project code is vendored.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper): local speech recognition. The bundled preparation route uses `WhisperModel(..., device="cpu", compute_type="int8")` and defaults to multilingual `small` with automatic language detection. Select settings for the actual footage; inspect quality on overlapping voices. Models download once at no charge. Do not download a huge model just to run a smoke check.
- [FFmpeg](https://ffmpeg.org/): local probing, extraction, and audio decoding. Discover existing installations first.
- [Adobe UXP samples](https://github.com/AdobeDocs/uxp-premiere-pro-samples) and [Markers API](https://developer.adobe.com/premiere-pro/uxp/ppro-reference/classes/markers/): the bundled small panel uses Adobe's documented source-clip marker interface and transaction pattern. It is original integration code, not a fork of the sample app.
- [Audalign 1.3.1](https://github.com/benfmiller/audalign): optional free local audio matching, tested on short pilot windows using fingerprinting and waveform correlation. Its pinned dependencies use a separate Python 3.12 environment, not the core preparation environment. Read [optional-tools.md](optional-tools.md) for setup and the bundled helper. A candidate requires local evidence review; a global alignment does not establish drifting correspondence.
- Windows' installed OCR engine: optional local text extraction from selected detail frames, with raw text and source timestamps retained. The bundled PowerShell helper needs no extra Python packages or computer-control skill; see [optional-tools.md](optional-tools.md). OCR errors must be checked against the images.
- [whisper.cpp](https://github.com/ggml-org/whisper.cpp): optional native Vulkan or CPU transcription. Its executable, runtime libraries and local GGML model are separate from Python dependencies. Inspect hardware and verify actual backend selection before using acceleration. See [speech-search.md](speech-search.md) for the pinned build and `prepare` flags; faster-whisper CPU remains the default.
- [FastEmbed](https://github.com/qdrant/fastembed): optional local semantic speech retrieval using ONNX Runtime and a small English model. Use its separate requirements/environment and pinned model download as described in [speech-search.md](speech-search.md). No vector-database service is needed.

The bundled workflow supplies images and timestamps to the existing chat, a local review queue and Premiere adapters. These are integration choices, not a benchmark proving best detection accuracy. Inspect the current host's Premiere version before selecting the optional UXP route.

## Install in an isolated environment

Use a project-owned environment, or reuse a compatible existing one. Prefer `uv` when available. All commands below are PowerShell examples: replace sample paths with current project paths, and use the environment's `bin/python` equivalent on other systems. Windows-specific OCR and Premiere host behavior have separate compatibility limits; examples do not establish cross-platform host validation.

```powershell
uv venv work/vod-env
uv pip install --python work/vod-env/Scripts/python.exe -r <skill>/requirements.txt
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py doctor
```

No API keys. `doctor` must find ffmpeg and ffprobe. Internet access is only needed for packages/models, not media processing. Extracted images/transcripts read in the chat are processed under that existing chat service; there are no additional API charges, but normal account limits still apply.

If `uv` is unavailable, use `python -m venv` and that environment's `python -m pip`. See [validation.md](validation.md) for compatibility boundaries and checks. This skill does not bundle a working environment, model cache or media; discover existing compatible installations and record their locations in project-owned local notes.

## Prepare and inspect

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py prepare --source 'D:/VODs/alice.mp4' --out work/vods/alice --limit-packets 1
# After the pilot is checked, resume all remaining packets with the same settings:
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py prepare --source 'D:/VODs/alice.mp4' --out work/vods/alice
```

Defaults: 300-second packets, 15-second overlap on both sides, at most roughly five seconds between regular samples (scene changes add frames), 960-pixel image width, `small` CPU transcription, automatic language detection. This is an initial sampling policy, not a promise of exhaustive visual detection. Frame-number sampling can create larger real-time gaps with variable frame rate; packet metadata reports actual gaps. Inspect and refine those gaps. For important small text use larger detail frames. Preserve fast/quiet uncertain candidates for denser review.

All audio streams are transcribed separately and labeled by stream index; inspect duplicate/mixed tracks in the evidence instead of assuming track zero contains every participant. VAD/no-speech results are not proof that no meaningful sound occurred.

`--limit-packets` controls how many newly prepared packets this invocation processes; omit it to process all remaining packets within the authorized scope and time budget. Each packet writes a completion record only after extraction and requested transcription succeed. A failure retains diagnostic files and is retried into a new attempt folder. Frames/contact sheets, analysis audio, and each stream's transcript are cached independently: a failed speech stream can retry while reusing completed visual/audio work and successful other streams. Checksums verify cached artifacts before copying them into an attempt; corrupt entries are rebuilt. Completed packets and their review decisions are retained. Do not claim a partial run is complete.

Resume requires the same source size/mtime and settings. Use a fresh output directory when changing them, with a shared `--cache-dir` to reuse stages whose inputs still match. The default cache belongs to the output folder. Cache keys include source identity and window, stage settings/versions, audio stream, and the selected speech runtime/model; a speech model change reuses matching frames and audio, while a frame width change rebuilds visual artifacts. A no-transcription pilot never supplies a speech cache result. Source size/mtime checks are practical identity checks, not a full hash of a many-hour VOD; use a new cache if media was replaced while preserving those attributes.

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py prepare --source 'D:/VODs/alice.mp4' --out work/vods/alice-small --cache-dir work/vods/stage-cache --model small --limit-packets 1
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py prepare --source 'D:/VODs/alice.mp4' --out work/vods/alice-other --cache-dir work/vods/stage-cache --model <local-model-folder> --limit-packets 1
```

Keep the cache local and project-owned. It contains extracted images, audio and transcripts, adds storage, and has no automatic eviction. Attempts receive independent copies so reviewing or editing an attempt does not alter shared cache artifacts. Compare processing time and storage with the reviewed benchmark workflow in [benchmark.md](benchmark.md); cache hits establish reuse, not discovery quality.

New speech preparations record effective runtime/model hashes separately in `asr-runtime.json`. Extending a partial preparation rejects changed weights even if the model argument is unchanged. Fully completed older folders resume without loading a model. An older partial faster-whisper folder lacks that identity record, so use a fresh output rather than combining transcripts with unverifiable model provenance. Local faster-whisper models need their own `tokenizer.json` for a complete cache identity; aliases resolve to the actual downloaded snapshot.

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py detail --source 'D:/VODs/alice.mp4' --out work/vods/alice-detail-01 --start 3560 --end 3590 --interval 0.5 --width 1440
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py export --events outputs/events.json --out outputs/markers.json
```

`detail` produces images only. Read the surrounding packet transcript or obtain more audio evidence separately. Source seconds are relative to the media playback beginning, not wall-clock time, sequence time, or displayed SMPTE timecode. Never derive seconds by dividing a VFR frame index by an assumed constant frame rate.

After preparation, index the supplied POV folders for local phrase search; see [discovery-tools.md](discovery-tools.md). Joined evidence is generated automatically for new and resumed packets. These additions reuse the pinned package and SQLite, with no new dependencies or model downloads.

## Native XML delivery for a new review project

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/premiere_xml.py --events outputs/events.json --out outputs/source-markers.xml
```

Create a separate Premiere review project, import the XML with File > Import, open a clip in the Source Monitor, and use the Markers panel. Save the checked `.prproj`. No plugin setup is required for this route. The output uses [FCP7 master-clip media tracks](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/Basics/Basics.html); a direct file child alone was silently ignored by Premiere 2026.

Before exporting, author the short visual labels and factual comments described in [events.md](events.md). Names contain only 1–4 words; IDs and review notes belong in comments. The JSON export, source XML, layered timeline XML and optional panel share this presentation. Re-export legacy event files after adding the required display fields; do not shorten them by slicing text. Updated XML does not rename markers inside a previously saved `.prproj`.

Both XML exporters organize imported project items into bins. `01 Media` contains one bin per source `pov` (falling back to its display label); `02 Sequences` contains review timelines when present. Keep all parts of the same POV together by authoring the same `pov` value. Source filenames, one-master-per-file identity and markers remain intact. No empty music, graphics or sequence bins are generated. These are Premiere project bins; files on disk are not moved.

After importing, show the **Project panel** with **Shift+1**, expand the imported bin, and open the source clip (or the sequence for a layered export). An empty Markers panel or a timeline saying “no sequences” does not establish import failure: the Project panel may be hidden and the imported sequence may simply be unopened. Check the Project panel before regenerating XML or asking for another import.

This imports **new source clip items**, with duration markers and POV references in their comments. This marker-only command creates no sequence or cuts. For full-main timelines with disabled alternate excerpts, use [timeline.md](timeline.md). Do not repeatedly import into a populated project assuming it updates existing items. Use the optional panel below when markers must attach to existing project items.

The exporter probes the actual media and validates its duration against events. It handles one progressive square-pixel video stream with at most one mono/stereo audio stream, supported nominal integer or 1000/1001 frame rates, and no nonzero embedded timecode. A stereo stream is grouped into one stereo source/timeline audio track, retaining both channels. Multiple audio streams are currently rejected by the XML route; import those natively and retain their actual stream mapping, or extend and live-test the adapter before delivery. Never discard streams. Unsupported layouts fail explicitly; use the panel or validate another integration for them. Marker seconds are rounded to the nearest nominal frame, so verify actual source playback for VFR media and custom interpretations. This is not a whole-VOD sync operation.

Bounded historical host checks covered nominal 60 and 30 fps media in Premiere 2026. They do not establish coverage or compatibility for a new project. The Markers panel sometimes displayed one frame below an exact whole-second saved time; do not add a compensating frame without checking the actual stored time. Premiere stripped literal comment newlines, so XML comments use visible separators. Other frame rates and layouts have only the stated adapter checks, not equivalent host validation.

## Optional source marker panel for existing project items

Requires Premiere Pro 25.6 or newer. Inspect actual compatibility on the user's installed build. Install Adobe's free UXP Developer Tool via Creative Cloud if needed, enable Premiere's UXP developer mode using Adobe's current [first-plugin guide](https://developer.adobe.com/premiere-pro/uxp/plugins/), and add `assets/premiere-panel/manifest.json` in UDT. Load it while Premiere is running. No Node build step or paid extension is needed. Do not change developer settings silently.

1. Import the original VODs into Premiere if not already present.
2. In the Project panel select one original source clip per source included in the marker JSON. Avoid duplicates, subclips, and multicam/merged items.
3. Open the **VOD suggestions** panel and choose `markers.json`.
4. Click **Check selected sources** to inspect source matches and marker count, then **Add source markers**.
5. Open a marked clip in the Source Monitor and verify a known event near both the beginning and end. Reimporting identical suggestions should report skips. Undo reverses a batch.

This is a loadable development panel, not a signed marketplace package. JSON/adapter testing cannot replace testing in Premiere. The panel does not save the project automatically; save after checking the result. Source clip markers may interact with the user's existing XMP metadata preferences, so use a test project and observe Premiere's normal behavior before production use.

Windows FCP XML URLs must use Premiere’s native `file://localhost/C%3a/...` encoding. Bare `file:///C:/...` was misread as a UNC path; adjacent pilot media initially hid this through automatic relinking. Verify absolute media paths in the saved project, especially when originals are outside the project directory.
