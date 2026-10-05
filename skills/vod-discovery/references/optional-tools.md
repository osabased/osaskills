# Optional local audio matching and frame OCR

Use these when an investigation needs them, after transcript/image evidence narrows the question. They produce review evidence, not accepted events or timeline edits. They do not run automatically on every packet. Core preparation and speech search keep their existing dependencies.

## Audalign: find a possible local correspondence

[Audalign 1.3.1](https://github.com/benfmiller/audalign) is MIT licensed and runs locally with FFmpeg. Its pinned dependencies have been tested in a separate Python 3.12 environment; isolate them from core preparation dependencies rather than assuming the project's main Python version is compatible. Reuse a compatible environment when present. Windows PowerShell example:

```powershell
uv venv --python 3.12 work/audalign-env
uv pip install --python work/audalign-env/Scripts/python.exe -r <skill>/requirements-audio.txt
$env:MPLCONFIGDIR = Join-Path $PWD 'work/audalign-cache'
work/audalign-env/Scripts/python.exe <skill>/scripts/audio_match.py --source-a 'D:/VODs/alice.mp4' --start-a 65 --end-a 95 --source-b 'D:/VODs/bob.mp4' --start-b 140 --end-b 185 --out work/audio-truce
```

Make ffmpeg and ffprobe available on PATH. No account, API key, paid model or media upload is needed. If Python 3.12 is missing, provision a separate runtime with the available environment manager; preserve the main environment. If `uv` is unavailable, use the fallback in [setup.md](setup.md). Installation requires network access, matching does not.

Choose short windows, such as 30–45 seconds, likely to contain the same distinctive sound or shared voice chat. Allow extra room in the comparison window for timing uncertainty. Do not compare entire hours-long VODs as a shortcut. On multi-audio sources, explicitly select `--stream-a` and `--stream-b` using the absolute ffprobe stream indices; these are not Premiere track numbers. The helper infers the index only when the source has exactly one audio stream. Its mono analysis WAV copies do not alter source media or Premiere audio grouping.

The helper runs fingerprinting at accuracy 3 and waveform correlation, with multiprocessing disabled. Each fresh output folder contains the two analysis WAVs, raw results/logs, and `candidate.json`. Preserve that folder as evidence. Source windows and stream indices are recorded. Existing evidence is not overwritten.

The sign convention is explicit:

`B source seconds = A source seconds + candidate_offset_b_minus_a_sec`

The source offset is `B window start - A window start + Audalign local offset`. A generated +2-second delay control verified the sign. Source playback seconds are used, not sequence timecode or wall-clock time.

`candidate_needs_review` means both methods suggest a compatible offset with a sufficiently distinct peak under **pilot-only heuristics**. These require at least 30 fingerprint matches, a 2:1 ratio against the strongest separate peak, and method agreement within 0.15 seconds. Peaks within 0.25 seconds are treated as neighbors. These settings are recorded in the result; they are not calibrated confidence, a claim of 0.15-second visual accuracy, or a reason to discard an event. `unresolved` keeps raw results and explains the ambiguity without selecting an offset.

Inspect the shared sound and nearby image evidence before authoring a local anchor. Both methods can match a common song or sound effect that is not the same event. Voice-chat latency can differ from visible action timing. Keep visual timing uncertainty separate from the numerical audio offset. Record correspondence only for the supported local event, investigate other windows independently, and never stretch media, infer a global drift curve, or write placements from this JSON alone. With no usable shared audio, continue with visual and transcript evidence.

### Validation limits

The thresholds were chosen using bounded development footage and synthetic controls, not an independent accuracy benchmark. Revalidate candidates on the current footage; no offset, event correspondence or hours-long drift behavior transfers between projects.

Spectrogram correlation was tried but is not used by the helper: it assigned independent synthetic noise its top rank and normalized score. An upstream field called `confidence`, a top rank, or a normalized maximum of 1.0 is not a probability of a correct correspondence.

## Windows OCR: find notices and other visible text

The optional `scripts/ocr_frames.ps1` uses the installed [Windows OCR API](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine.recognizeasync?view=winrt-26100). It runs locally in Windows PowerShell 5.1, requires an installed OCR language, and needs no Python package, external model or computer-control skill. It reads images only.

Use selected, sufficiently large detail frames when a notice, scoreboard, quest update or other text might answer a specific question. Create a JSON array by copying the exact source ID, source-local timestamp and absolute image path from the preparation metadata/frame map:

```json
[
  {"source_id":"alice-source-id", "timestamp_sec":113.0, "file":"D:/project/work/alice-detail/frames/raw_00004.jpg"}
]
```

Do not calculate timestamps from filenames or image order. The helper validates the manifest's types and paths but cannot establish whether a supplied timestamp truly belongs to that image. The caller must preserve the frame-map relationship.

```powershell
powershell.exe -NoProfile -File <skill>/scripts/ocr_frames.ps1 -Manifest work/ocr-input.json -Out work/ocr-results.json
```

If the machine's script execution policy blocks `-File`, the locally inspected helper can be invoked as a command block in a Windows PowerShell session without changing the execution policy:

```powershell
$ocrScript = [IO.File]::ReadAllText('<skill>/scripts/ocr_frames.ps1')
& ([scriptblock]::Create($ocrScript)) -Manifest work/ocr-input.json -Out work/ocr-results.json
```

Use a fresh output path. The result records the engine language, image and manifest hashes, source timestamps, raw text, lines, and word rectangles in the input image's pixels. It does not silently correct names or give recognition confidence. Oversized images fail explicitly; prepare a smaller frame or a documented crop while retaining its source timestamp. Missing language support is a reason to skip this optional aid and inspect the images directly.

OCR can miss text and misspell names or other words. Use approximate phrases and spelling variants to find leads, then read the actual image before writing a factual event or cross-POV link. Absence of OCR text never proves absence of an event.

Supply this report to `unified_search.py index` to retrieve visible text alongside speech and optional semantic leads; read [unified-search.md](unified-search.md). The unified index verifies image hashes and exact frame-map clocks and requires an explicit source mapping when OCR aliases differ from preparation IDs. It retains the raw OCR and report references. `vod.py search` remains speech-only, and OCR is never collected automatically from arbitrary folders. OCR does not replace contact-sheet review, denser sampling of fast events, or human-readable factual marker comments.
