# Setup and preparation

## Components

- [claude-real-video 0.10.7](https://github.com/HUANGCHIHHUNGLeo/claude-real-video) is a third-party MIT package, not an Anthropic product. It supplies FFmpeg frame extraction with timestamp mapping, contact sheets, joined frame/transcript spans and local transcript search. The adapters call only `core.extract_frames`, `write_frames_json`, `make_grids`, `timeline_lite.build_spans` and `memory.remember/search`, pinned to this version and checked at runtime. They avoid its high-level `process` function, which copies the input and applies deduplication and frame caps. Installing it also pulls in yt-dlp and deno, which these adapters do not use.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper): local speech recognition. Preparation uses `WhisperModel(..., device="cpu", compute_type="int8")` with the multilingual `small` model and automatic language detection by default. Models download once, free. Do not download a huge model just for a smoke check.
- [FFmpeg](https://ffmpeg.org/): probing, extraction and audio decoding. Discover an existing installation first.
- Optional, each with its own reference: [whisper.cpp](speech-search.md) with Vulkan, [FastEmbed](speech-search.md) semantic search (English only), [Audalign](optional-tools.md) audio matching, [Windows OCR](optional-tools.md). They are capabilities with prerequisites, not requirements for every project.

Processing is free and local: no API keys, paid services or cloud inference. Images and transcripts you view in the conversation count toward the normal usage of that conversation. Respect the project's processing and privacy constraints.

## Install

Requires Python 3.11 or newer (3.13 is tested), FFmpeg and ffprobe on `PATH`. Use a project-owned environment, or reuse a compatible existing one, and record its location in the project's notes. Prefer `uv`:

```sh
uv venv --python 3.13 work/vod-env
uv pip install --python work/vod-env -r <skill>/requirements.txt
PY=work/vod-env/bin/python          # Windows: PY=work/vod-env/Scripts/python.exe
"$PY" <skill>/scripts/vod.py doctor
```

All examples use `$PY` for this environment's Python and `<skill>` for the skill folder. Without `uv`, use `python3.13 -m venv work/vod-env` and `"$PY" -m pip install -r <skill>/requirements.txt`. Internet access is needed only for packages and models.

`doctor` prints tool and package versions plus `problems` (missing tools, packages or Python older than 3.11) and `notes` (for example an FFmpeg build without libx264, which review-queue previews need). It exits non-zero when there are problems.

## Project notes

Record project decisions in `AGENT_DIR/vod/project-context.md` under the video project's root, where `AGENT_DIR` is the project's `.claude/` if it exists, otherwise `.agents/` if it exists, otherwise a new `.claude/` (if both exist, use the one that already contains `vod/`, else `.claude/`). An older `project-context.md` beside the analysis still counts; offer to move it. Record: source paths and part order, POV identities, review scope, editing preferences, environment and runtime locations. It is an agent-readable note, not a configuration file; pass real settings through script arguments. Keep machine-specific paths out of this skill.

## Prepare

```sh
"$PY" <skill>/scripts/vod.py prepare --source /media/vods/alice.mp4 --out work/vods/alice --limit-packets 1
# After checking the pilot, resume the remaining packets with the same settings:
"$PY" <skill>/scripts/vod.py prepare --source /media/vods/alice.mp4 --out work/vods/alice
```

Defaults: 300-second packets with 15 seconds of overlap on each side; a regular sample at least every 5 seconds, plus scene changes; 960-pixel frames; `small` CPU transcription with automatic language detection. Frame deduplication and frame caps are deliberately off. This is an initial sampling policy, not exhaustive visual detection. With variable frame rate, real-time gaps can exceed the interval; `packet.json` reports the actual maximum gap. Use `detail` for fast moments and small text.

Every audio stream is transcribed separately and labelled by stream index; check duplicate or mixed tracks in the evidence instead of assuming stream 0 has everyone. VAD or no-speech results do not prove that no meaningful sound occurred.

`--limit-packets` limits how many new packets one run prepares; omit it to prepare all remaining packets. Each packet writes `complete.json` only after extraction and requested transcription succeed. A failure keeps its diagnostic files, and the next run retries in a new attempt folder. Interrupting a run (including killing it) loses only the packet in progress and may leave an unreferenced `attempt-*` folder, which is safe to delete. Never report a partial run as complete. Running long preparations within tool time limits is covered in SKILL.md under "Long jobs".

## Resume and caches

Resuming needs the same source size, mtime and settings. To change settings, use a fresh `--out` with a shared `--cache-dir` so matching stages are reused:

```sh
"$PY" <skill>/scripts/vod.py prepare --source /media/vods/alice.mp4 --out work/vods/alice-small --cache-dir work/vods/stage-cache --model small --limit-packets 1
"$PY" <skill>/scripts/vod.py prepare --source /media/vods/alice.mp4 --out work/vods/alice-other --cache-dir work/vods/stage-cache --model <local-model-folder> --limit-packets 1
```

- Frames and contact sheets, analysis audio, and each stream's transcript are cached separately. A failed speech stream can retry while reusing visual and audio work and the other streams. Checksums are verified before reuse; corrupt entries are rebuilt.
- Cache keys include source identity and window, stage settings and versions, audio stream, and the speech runtime and model. A model change reuses frames and audio; a frame-width change rebuilds the visual stage. A `--no-transcribe` pilot never supplies a speech result.
- Size and mtime are a practical identity check, not a hash of a many-hour VOD. Use a new cache if media was replaced while keeping those attributes.
- The default cache lives in the output folder. Caches hold images, audio and transcripts, add storage and are never evicted automatically. Each attempt gets independent copies, so editing an attempt never alters the cache.
- New speech preparations record the effective runtime and model hashes in `asr-runtime.json`, including the installed `faster-whisper`, `ctranslate2` and `tokenizers` versions. Extending a partial preparation rejects changed weights or versions, so do not upgrade the environment mid-preparation. Fully completed folders resume without loading a model. An older partial faster-whisper folder without that record needs a fresh output folder. Local faster-whisper models need their own `tokenizer.json`.

Completed packets and their `review.json` decisions are always kept. Compare processing time and storage with [benchmark](benchmark.md); cache hits show reuse, not discovery quality.

## Source clocks

Source seconds count from the media's playback start. They are not wall-clock time, sequence time or embedded SMPTE timecode. Never compute seconds from a frame index and an assumed constant frame rate.
