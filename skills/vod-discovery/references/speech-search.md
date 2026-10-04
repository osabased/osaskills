# Vulkan transcription and semantic retrieval

These are optional local additions. Reuse the tested installations listed in validation.md when present. Run a bounded pilot when changing models, drivers, language or inference settings. Source timing and evidence review still govern markers and POV placement.

## whisper.cpp with Vulkan

The adapter was tested with [whisper.cpp v1.9.4](https://github.com/ggml-org/whisper.cpp/tree/v1.9.4), commit `927cfce34f31707e17f2bff35c349632fb9e2c3a`, and the RX 5700 XT. This is a selectable backend for `vod.py prepare`. The existing faster-whisper CPU backend remains available and is the CLI default; for this machine's English VODs, the verified Vulkan runtime can be selected explicitly.

On a new installation, discover existing tools first. A source build needs CMake, a compatible C++ compiler, and Vulkan development files including glslc and SPIRV-Headers. Use official upstream source and the [LunarG SDK](https://vulkan.lunarg.com/sdk/home/). An installed Vulkan driver alone does not supply the build tools. The official Windows release archives inspected during the pilot lacked a Vulkan variant; do not assume a CPU archive can accelerate on AMD.

```powershell
git clone --depth 1 --branch v1.9.4 https://github.com/ggml-org/whisper.cpp.git work/whisper-cpp
cmake -S work/whisper-cpp -B <short-build-dir> -DGGML_VULKAN=ON -DWHISPER_BUILD_TESTS=OFF -DWHISPER_BUILD_SERVER=OFF
cmake --build <short-build-dir> --config Release --target whisper-cli -j 4
```

Use a short absolute build path on Windows: nested shader projects exceeded MSBuild's path limit in the original long workspace path. A duplicate `PATH`/`Path` environment entry also broke MSBuild; a child process launched with `env=dict(os.environ)` resolved that locally. No upstream source edits were needed. Keep the executable with its generated DLLs. The SDK files used for this installation were unpacked locally; no system SDK installer or driver change was required.

The English pilot uses `ggml-small.en-q5_1.bin`, downloaded from the [official converted-model repository](https://huggingface.co/ggerganov/whisper.cpp/tree/5359861c739e955e79d9a303bcbc70fb988958b1). Its SHA256 is `bfdff4894dcb76bbf647d56263ea2a96645423f1669176f4844a1bf8e478ad30` (190,098,681 bytes). This is an English-only, quantized model; use and pilot an appropriate multilingual model for other languages. The adapter supports a local GGML model path, not an API endpoint.

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py prepare --source 'D:/VODs/alice.mp4' --out work/vods/alice-vulkan --asr-backend whisper-cpp --whisper-cli work/whisper-runtime/whisper-cli.exe --whisper-model work/downloads/ggml-small.en-q5_1.bin --language en --limit-packets 1
```

Use fresh preparation folders when changing backend/model/settings. Completed older packets and their review decisions are retained; they are not silently retranscribed. Subsequent identical calls resume normally. Add the same `--cache-dir work/vods/stage-cache` to different preparation folders to reuse matching frames/contact sheets and decoded audio. Transcripts are cached per stream with their language and runtime/model identity; a failed stream does not invalidate successful other streams. Binary/DLL/model hashes are part of the recorded settings, so replacing them requires a fresh folder. `--whisper-threads` defaults to 4 and `--whisper-gpu` to 0. `--whisper-device cpu` explicitly runs the same model without GPU acceleration for comparison or fallback.

The adapter checks the runtime log for **selection** of a Vulkan backend. Listing a GPU or compiling with Vulkan is insufficient. A requested Vulkan run fails explicitly if selection is not confirmed. It preserves raw CLI JSON, logs, run timing, selected runtime/model hashes and each analysis WAV's hash inside the packet. Millisecond offsets are converted to source seconds exactly once, separately for every actual audio stream. The CLI default no-context behavior is paired with zero retained text-context tokens. This adapter currently runs without VAD; this differs from the faster-whisper preparation settings.

Cached whisper.cpp run records identify raw JSON/log paths relative to the run file. Their command paths are explicitly historical: a copied transcript is reused evidence, not a new inference run. Failed and corrupt cache snapshots retain diagnostic files. New partial preparations also compare `asr-runtime.json` before adding packets; see setup.md for older faster-whisper folders without that provenance.

Invalid ASR bounds remain raw and are flagged/excluded by the existing evidence adapter. Non-speech placeholders, invented words, names and repeated text still need inspection. Do not interpret an empty transcript or `[BLANK_AUDIO]` as proof that no event happened. More recognized text does not by itself establish greater accuracy.

## Search by meaning

The optional semantic helper uses [FastEmbed](https://github.com/qdrant/fastembed) with a small English BGE retrieval model on CPU through ONNX Runtime. This implements the semantic-search addition without a PyTorch installation or a vector-database service. It reuses the project's existing literal-index aggregates and exact occurrence references. Literal phrase search remains useful for names, exact wording and checking a semantic lead.

Create or reuse a **separate Python 3.12 environment**, then download the pinned model once:

```powershell
py -3.12 -m venv work/semantic-env
work/semantic-env/Scripts/python.exe -m pip install -r <skill>/requirements-semantic.txt
work/semantic-env/Scripts/python.exe <skill>/scripts/semantic.py download-model --out work/semantic-model
```

The model is `BAAI/bge-small-en-v1.5`, using Qdrant's quantized ONNX conversion at revision `aa8f8b060edb00e03bfdd08813a2949946c8ba55`. Its main file is approximately 67 MB. The download command uses immutable URLs and checks the model checksum; subsequent runs validate every saved model file. After installation, indexing and querying use local files only. The selected model and code have permissive free licenses (MIT and Apache-2.0). There are no media uploads, cloud accounts or usage fees for these helpers.

First build/reuse the literal index in the preparation environment, then the semantic index in its own environment:

```powershell
work/vod-env/Scripts/python.exe <skill>/scripts/vod.py index --prepared work/vods/alice-vulkan work/vods/bob-vulkan --out work/vods/search
work/semantic-env/Scripts/python.exe <skill>/scripts/semantic.py index --literal-index work/vods/search --model-dir work/semantic-model --out work/vods/semantic
work/semantic-env/Scripts/python.exe <skill>/scripts/semantic.py search --index work/vods/semantic --model-dir work/semantic-model --query 'someone watching instead of helping me fight' --limit 10 --out work/vods/query.json
```

Pass one preparation folder per media source to the literal index: choose the desired transcript version, not both old and new preparations of the same VOD. Search can include partly prepared sources; returned coverage makes those limits visible. Preparation coverage is not completed footage review.

The semantic index contains individual statements and nearby context windows, separated by source and audio stream. Combined windows span at most 30 seconds and do not cross gaps above 10 seconds. An individual ASR segment can be longer. A tokenizer checks a 384-token budget; long text is split without dropping characters. Those pieces keep the original segment's full time interval and character offsets because their individual word times are unknown. Source clocks are never derived from token position.

Every hit includes source seconds, original text, stream, transcript file, segment index and evidence references. Similar overlapping windows from the same source/stream are grouped for readability; independent POVs, other streams and later occurrences remain separate. All indexed passages stay on disk. `more_available` and `limit` describe retrieval presentation, not a top-N cap on discovery. Model/input/artifact hashes detect stale or changed evidence; rebuild literal then semantic indexes after preparation changes. Builds publish a new snapshot only after embedding succeeds; unchanged indexes are reused.

Semantic rebuilds cache each exact passage text independently of its evidence references, scoped to model identity, passage policy and embedding recipe. Growing or rebuilding the literal index reuses matching vectors while publishing current source clocks and occurrence references. Entries are checksummed and validated; failed batches leave previously completed batches reusable. `index --cache-dir work/vods/embedding-cache` can share these vectors between semantic output folders; the default cache stays in the semantic output. Build results report `embeddings_reused` and `embeddings_computed` for unique passage texts. This saves embedding work; models still initialize for indexing/token checks and each standalone search invocation.

Similarity is a ranking score, **not a percentage, confidence, editorial priority or match confirmation**. Even an unrelated query returns nearest passages. Inspect the quoted evidence and surrounding footage before adding a candidate or a POV link; never use a score as a discard threshold. This is English speech-text search, not OCR search, visual retrieval, speaker identification or synchronization. Keep the regular overinclusive visual pass.

## Keep inference models loaded for repeated work

For multiple related searches, use `search-many` with a JSON array of query strings and a fresh output file. It loads the semantic model once and returns the usual complete result for each query:

```powershell
work/semantic-env/Scripts/python.exe <skill>/scripts/semantic.py search-many --index work/vods/semantic --model-dir work/semantic-model --queries work/vods/queries.json --limit 10 --out work/vods/query-results.json
```

For an adaptive sequence of searches, `semantic.py worker --index ... --model-dir ...` keeps the model in one process and accepts one JSON object per stdin line: `{"id":"q1","query":"someone watching instead of helping","limit":10}`. Wait for `{"ready":true,"protocol":"vod-semantic-worker/v1"}`. Each reply contains the request ID and either `result` or `error`. EOF stops the worker; close stdin and wait for exit after the investigation. Requests are serial, limited to 16,384 characters. An oversized line stops the worker. Invalid queries return errors without replaying old results. This transport opens no network port.

Every query still verifies raw preparation signatures, model hashes and index artifacts and reads current evidence references. Only the model is retained; a changed model requires restarting the worker. A valid rebuilt index with the same model can be read by the existing worker. Single-query `search` remains available. None of these modes change the retrieval/overlap-grouping rules or write to the indexed evidence.

For multi-packet whisper.cpp preparation, the optional `--whisper-server <path>` flag owns one local server for the duration of `prepare`. It starts lazily on the first uncached transcript and closes on normal completion, exceptions or handled interruption. Fully cached runs do not load a model. The server binds only to 127.0.0.1 on a temporary port, uses a random route and an empty public directory, and accepts the already decoded WAV files. The adapter never requests model changes or runtime format conversion. A request failure closes the worker and leaves the failed stage available for diagnosis/resume; it never silently falls back to another ASR mode.

Use a `whisper-server` built from the same verified whisper.cpp source/build as `whisper-cli`, with identical adjacent runtime DLLs. The tested runtime is v1.9.4 with Vulkan on the RX 5700 XT. An existing CMake build can add the server by configuring `WHISPER_BUILD_SERVER=ON` and building target `whisper-server`; no model download or upstream source modification is needed. Keep the helper hidden on Windows. Server/model/runtime hashes and explicit decoding settings are included in transcript cache identity. Preserve the CLI route for single requests and unverified server builds.

```powershell
python <skill>/scripts/vod.py prepare --source "D:/VODs/alice.mp4" --out work/vods/alice-worker --cache-dir work/vods/stage-cache --asr-backend whisper-cpp --whisper-cli work/whisper-runtime/whisper-cli.exe --whisper-server work/whisper-runtime/whisper-server.exe --whisper-model work/downloads/ggml-small.en-q5_1.bin --whisper-device vulkan --language en
```

Switching transport changes preparation/runtime identity: use a fresh output folder with the same cache directory. Frames and audio can be reused; CLI transcripts are not silently relabelled as server results. The worker explicitly matches the tested CLI's beam/best-of, context, temperature and segment-timestamp settings; upstream server defaults differ. Requests retain independent source clocks and streams, with raw server JSON, canonical transcript JSON and worker logs. Timing metadata separates startup from request inference. Verification currently covers bounded English pilot windows, not all languages, hours-long throughput, or recovery after forcibly killing the parent process.
