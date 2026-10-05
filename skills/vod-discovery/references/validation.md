# Compatibility and verification

This reference describes the bundled adapters' validation boundaries. It is not a project configuration, a list of installed runtimes, or evidence that the current footage has been reviewed. Keep project findings, machine paths, local benchmarks and saved-project checks with that project's outputs. Recheck prerequisites when moving to another host.

## Processing and search

- Core preparation uses the pinned dependencies in `requirements.txt`, FFmpeg and ffprobe. The default speech route is faster-whisper on CPU with a multilingual model and automatic language detection. Verify source duration, audio streams, sample timing and transcript bounds on a representative interval before processing long sources.
- The optional whisper.cpp adapter's verified baseline is v1.9.4. It accepts explicit local runtime/model paths and checks actual Vulkan selection when requested. Building with Vulkan or listing a GPU is not evidence of accelerated inference. Verify model language, source-clock conversion and actual backend logs; see [speech-search.md](speech-search.md). Historical English trials do not establish multilingual quality or throughput on other hardware.
- Semantic retrieval uses the pinned English BGE model; it is not a universal multilingual adapter. Literal search and clickable transcripts retain source/stream/segment references without a semantic model. Similarity is not editorial importance or synchronization confidence.
- Audalign thresholds are development heuristics requiring evidence review. The OCR helper uses Windows PowerShell 5.1 and an installed Windows OCR language. It is optional; missing OS/language support does not block the core visual/speech workflow. See [optional-tools.md](optional-tools.md).
- Caches validate their inputs and artifacts; a cache hit proves reuse, not review completeness or discovery quality. Changing relevant runtime/model settings requires the documented fresh-output/resume workflow.

## Premiere delivery

The XML route has bounded historical Premiere 2026 host checks with nominal 60 and 30 fps media. Other supported rates are adapter-level support, not an equivalent live-host claim. Probe each project's actual media. The current XML exporter supports one progressive square-pixel video stream and at most one mono/stereo audio stream per source, with no nonzero embedded timecode; unsupported layouts fail rather than dropping streams. The optional UXP marker panel has host mocks but still needs live validation in the user's installed build.

After import, inspect the Project panel before treating an empty monitor as failure. Verify resolved media paths, short marker names/comments and source times. For timelines, check main-source order/duration, moment boundary cuts and label contrast, matching linked video/audio cuts, grouped stereo, disabled alternate clips and locally supported POV positions. Review current sources near both the beginning and end and at an overlapping moment. Existing projects are not updated by XML reimport. See [setup.md](setup.md) and [timeline.md](timeline.md).

Serialized labels and passing XML tests do not establish displayed colors in the host. A user's label preferences can change swatches. Mixed-rate timeline In/Out uses sequence-rate frames while masters retain native rates. Do not compensate for display rounding without checking stored source times. Do not patch Premiere project internals.

## Review queue

The last implementation verification passed 190 Python tests, four Node suites and ten browser interaction checks. Those checks covered authored related groups, saved choices, waveform/thumbnail clocks, literal transcript jumps, bounded excerpts, preview context, revised-queue migration and exports. They used bounded fixtures and a development pilot; no full-session discovery-recall or fatigue benefit was established. Test counts are historical evidence, not a claim that every new installation has passed.

On a new host or changed implementation, exercise a representative queue through playback/seeking, an alternate POV switch, a decision plus Undo/reload, and an export. When relevant, also check transcript navigation outside moment previews, context expansion, aid-cache recovery and migration. Preserve original review state and shared keyboard settings during trials. Browser behavior, local FFmpeg availability and Premiere import remain separate checks.

## Checks for changes

Run relevant existing suites for executable changes. A full regression pass, when justified, uses the project's compatible Python environment and Node:

```text
python -m unittest discover -s <skill>/tests -p "test_*.py"
node <skill>/tests/test_app.js
node <skill>/tests/test_playback.js
node <skill>/tests/test_aids.js
node <skill>/tests/test_panel.js
```

For instruction-only changes, check project independence, accurate adapter limits, linked resources, example validity and the skill validator without claiming new runtime or host verification. Evaluate meaningful workflow changes with representative footage and the benchmark harness in [benchmark.md](benchmark.md); previous project results cannot establish recall on new footage.
