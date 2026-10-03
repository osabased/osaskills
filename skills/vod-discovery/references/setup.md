# Setup and reuse

## Components and boundaries

- [claude-real-video 0.10.7](https://github.com/HUANGCHIHHUNGLeo/claude-real-video): MIT, existing FFmpeg frame extraction, timestamp mapping, contact sheets. The adapter imports `core.extract_frames`, `write_frames_json`, and `make_grids`; these internal interfaces are version-pinned. It avoids the high-level `process` function, which copies the full input into each output and applies deduplication/caps. No project code is vendored.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper): local speech recognition, `WhisperModel(..., device="cpu", compute_type="int8")`. The RX 5700 XT does not provide its CUDA backend. Use `small` initially; benchmark quality on overlapping voices. Models download once at no charge. Do not download a huge model just to run a smoke check.
- [FFmpeg](https://ffmpeg.org/): local probing, extraction, and audio decoding. Discover existing installations first.
- [Adobe UXP samples](https://github.com/AdobeDocs/uxp-premiere-pro-samples) and [Markers API](https://developer.adobe.com/premiere-pro/uxp/ppro-reference/classes/markers/): the bundled small panel uses Adobe's documented source-clip marker interface and transaction pattern. It is original integration code, not a fork of the sample app.
- [audalign](https://github.com/benfmiller/audalign): optional free audio fingerprinting when recordings share useful audio. Not installed or required. A global alignment does not establish drifting correspondence; verify anchors around each event.

StoryToolkitAI was considered for footage search, but the chosen preparation component directly supplies images and timestamps to the existing chat without adopting another editing UI. Pymiere was considered; the installed Premiere 2026 has a current UXP API, so an older ExtendScript bridge is not a requirement. These are bounded integration choices, not a benchmark proving best detection accuracy.

## Install in an isolated environment

Use a project-owned environment, or reuse a compatible existing one. Example PowerShell (replace paths as needed):

```powershell
python -m venv work/vod-env
work/vod-env/Scripts/python.exe -m pip install -r <skill>/requirements.txt
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py doctor
```

No API keys. `doctor` must find ffmpeg and ffprobe. Internet access is only needed for packages/models, not media processing. Extracted images/transcripts read in the chat are processed under that existing chat service; there are no additional API charges, but normal account limits still apply.

For this machine's already-tested environment and remaining verification, read [validation.md](validation.md). Reuse it while its files and versions remain valid.

## Prepare and inspect

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py prepare --source 'D:/VODs/alice.mp4' --out work/vods/alice --limit-packets 1
# After the pilot is checked, resume all remaining packets with the same settings:
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py prepare --source 'D:/VODs/alice.mp4' --out work/vods/alice
```

Defaults: 300-second packets, 15-second overlap on both sides, at most roughly five seconds between regular samples (scene changes add frames), 960-pixel image width, `small` CPU transcription, automatic language detection. This is an initial sampling policy, not a promise of exhaustive visual detection. Frame-number sampling can create larger real-time gaps with variable frame rate; packet metadata reports actual gaps. Inspect and refine those gaps. For important small text use larger detail frames. Preserve fast/quiet uncertain candidates for denser review.

All audio streams are transcribed separately and labeled by stream index; inspect duplicate/mixed tracks in the evidence instead of assuming track zero contains every participant. VAD/no-speech results are not proof that no meaningful sound occurred.

`--limit-packets` controls how many newly prepared packets this invocation processes; remove it for the overnight preparation. Each packet writes a completion record only after extraction and requested transcription succeed. A failure retains diagnostic files and is retried into a new attempt folder. Resume requires the same source size/mtime and settings, or use a fresh output directory. Do not claim a partial run is complete.

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py detail --source 'D:/VODs/alice.mp4' --out work/vods/alice-detail-01 --start 3560 --end 3590 --interval 0.5 --width 1440
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py export --events outputs/events.json --out outputs/markers.json
```

`detail` produces images only. Read the surrounding packet transcript or obtain more audio evidence separately. Source seconds are relative to the media playback beginning, not wall-clock time, sequence time, or displayed SMPTE timecode. Never derive seconds by dividing a VFR frame index by an assumed constant frame rate.

## Native XML delivery for a new review project

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/premiere_xml.py --events outputs/events.json --out outputs/source-markers.xml
```

Create a separate Premiere review project, import the XML with File > Import, open a clip in the Source Monitor, and use the Markers panel. Save the checked `.prproj`. No plugin setup is required for this route. The output uses [FCP7 master-clip media tracks](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/Basics/Basics.html); a direct file child alone was silently ignored by Premiere 2026.

Before exporting, author the short visual labels and factual comments described in [events.md](events.md). Names contain only 1–4 words; IDs and review notes belong in comments. The JSON export, source XML, layered timeline XML and optional panel share this presentation. Re-export legacy event files after adding the required display fields; do not shorten them by slicing text. Updated XML does not rename markers inside a previously saved `.prproj`.

After importing, show the **Project panel** with **Shift+1**, expand the imported bin, and open the source clip (or the sequence for a layered export). An empty Markers panel or a timeline saying “no sequences” does not establish import failure: the Project panel may be hidden and the imported sequence may simply be unopened. Check the Project panel before regenerating XML or asking for another import.

This imports **new source clip items**, with duration markers and POV references in their comments. This marker-only command creates no sequence or cuts. For full-main timelines with disabled alternate excerpts, use [timeline.md](timeline.md). Do not repeatedly import into a populated project assuming it updates existing items. Use the optional panel below when markers must attach to existing project items.

The exporter probes the actual media and validates its duration against events. It handles one progressive square-pixel video stream with at most one mono/stereo audio stream, supported nominal integer or 1000/1001 frame rates, and no nonzero embedded timecode. A stereo stream is grouped into one stereo source/timeline audio track, retaining both channels. Multiple audio streams are currently rejected by the XML route; import those natively and retain their actual stream mapping, or extend and live-test the adapter before delivery. Never discard streams. Unsupported layouts fail explicitly; use the panel or validate another integration for them. Marker seconds are rounded to the nearest nominal frame, so verify actual source playback for VFR media and custom interpretations. This is not a whole-VOD sync operation.

The Johan/Josh pilot passed live import and saved-project checks at nominal 60 and 30 fps. All 22 saved start times, durations, names and comments were checked. Premiere's Markers panel sometimes displayed one frame below an exact whole-second saved time; do not add a compensating frame without checking the actual stored time. Premiere stripped literal comment newlines, so XML comments use visible separators. Other frame rates and layouts have only the stated adapter checks, not equivalent host validation.

## Optional source marker panel for existing project items

Requires Premiere Pro 25.6 or newer. Inspect actual compatibility on the user's installed build. Install Adobe's free UXP Developer Tool via Creative Cloud if needed, enable Premiere's UXP developer mode using Adobe's current [first-plugin guide](https://developer.adobe.com/premiere-pro/uxp/plugins/), and add `assets/premiere-panel/manifest.json` in UDT. Load it while Premiere is running. No Node build step or paid extension is needed. Do not change developer settings silently.

1. Import the original VODs into Premiere if not already present.
2. In the Project panel select one original source clip per source included in the marker JSON. Avoid duplicates, subclips, and multicam/merged items.
3. Open the **VOD suggestions** panel and choose `markers.json`.
4. Click **Check selected sources** to inspect source matches and marker count, then **Add source markers**.
5. Open a marked clip in the Source Monitor and verify a known event near both the beginning and end. Reimporting identical suggestions should report skips. Undo reverses a batch.

This is a loadable development panel, not a signed marketplace package. JSON/adapter testing cannot replace testing in Premiere. The panel does not save the project automatically; save after checking the result. Source clip markers may interact with the user's existing XMP metadata preferences, so use a test project and observe Premiere's normal behavior before production use.

Windows FCP XML URLs must use Premiere’s native `file://localhost/C%3a/...` encoding. Bare `file:///C:/...` was misread as a UNC path; adjacent pilot media initially hid this through automatic relinking. Verify absolute media paths in the saved project, especially when originals are outside the project directory.
