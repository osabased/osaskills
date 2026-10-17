# Compatibility and verification

This file states what the bundled adapters have been checked against. It is not a project configuration, a list of installed runtimes, or evidence that any footage was reviewed. Keep project findings, machine paths, local benchmarks and saved-project checks with that project's outputs, and recheck prerequisites on a new host.

## Processing and search

- Core preparation: Python 3.11+ (3.13 tested), the pins in `requirements.txt`, FFmpeg and ffprobe. Before processing long sources, verify source duration, audio streams, sample timing and transcript bounds on a representative interval.
- whisper.cpp: verified baseline v1.9.4, explicit local runtime and model paths, and a check that Vulkan was actually selected. Historical English trials do not establish multilingual quality or throughput elsewhere. See [speech-search](speech-search.md).
- Semantic retrieval: the pinned English BGE model only. Literal search and transcript navigation work without it.
- Audalign: development heuristics that need evidence review. OCR: Windows PowerShell 5.1 with an installed OCR language. Both are optional; see [optional-tools](optional-tools.md).
- POV alignment, region text and pair sheets: unit tests with synthetic transcripts and generated video, plus one development check on a single session; see [alignment](alignment.md#what-this-has-and-has-not-shown). Region OCR needs Windows and has no automated test.
- Caches validate inputs and artifacts. A cache hit proves reuse, not review completeness or discovery quality.

## Premiere delivery

- XML: bounded host checks with 60 and 30 fps media in Premiere 2026 on Windows. Other supported rates have adapter tests only, and macOS media paths are untested. Limits on streams, timecode and pixel shape are listed in [premiere](premiere.md#supported-media).
- Labels: serialized labels and passing XML tests do not establish the colors shown in the host; the editor's label preferences change swatches.
- Mixed-rate timelines: sequence clip In/Out uses sequence-rate frames while masters keep native rates.
- UXP panel: mock tests only; it needs a live check in the editor's installed build.

Host checks after import are in [premiere](premiere.md#after-import) and [timeline](timeline.md#verify-the-saved-result).

## Review queue

The queue has Python and Node tests plus earlier browser interaction checks on bounded fixtures and a development pilot. No full-session recall or fatigue benefit has been established. On a new host or after changing the implementation, exercise a representative queue: playback and seeking, an alternate POV switch, a decision plus Undo and reload, and an export. When relevant, also check transcript navigation outside moment previews, context expansion, aid-cache recovery and migration. Use a temporary `--preferences` profile and a copy of the queue so the editor's keyboard settings and choices stay untouched.

## Checks for changes

Install `requirements.txt` into a scratch environment first; about a quarter of the Python tests import claude-real-video. Then run from the repository root:

```sh
"$PY" -m unittest discover -s skills/vod-discovery/tests -p "test_*.py"
node skills/vod-discovery/tests/test_app.js
node skills/vod-discovery/tests/test_playback.js
node skills/vod-discovery/tests/test_aids.js
node skills/vod-discovery/tests/test_panel.js
```

None of these need footage, model downloads or Premiere. For instruction-only changes, check project independence, adapter limits, links and example validity without claiming new runtime or host verification. Evaluate workflow changes on representative footage with [benchmark](benchmark.md); earlier project results cannot establish recall on new footage.
