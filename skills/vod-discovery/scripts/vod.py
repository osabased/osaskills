"""Small adapters around existing video tools; no paid inference service."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def number(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise ValueError(f"Invalid {name}: {value!r}")
    return value


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing {name}")
    return value


def probe(source):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(source)],
                       check=True, capture_output=True, encoding="utf-8")
    data = json.loads(r.stdout)
    if not any(s["codec_type"] == "video" for s in data["streams"]):
        raise ValueError("Source has no video stream")
    duration = float(data["format"]["duration"])
    number(duration, "duration", 0.001)
    return data, duration


def extract(source, folder, start, end, interval, width):
    from claude_real_video import core
    if importlib.metadata.version("claude-real-video") != "0.10.7":
        raise RuntimeError("This adapter is verified against claude-real-video 0.10.7; revalidate before upgrading")
    count, times = core.extract_frames(str(source), str(folder / "frames"), scene=0.30,
                                      fps_floor=interval, start=start, end=end, frame_width=width)
    files = sorted((folder / "frames").glob("raw_*.jpg"))
    if not count or len(times) != len(files):
        raise RuntimeError("Missing or inconsistent frame timestamps; do not infer them")
    if any(b <= a for a, b in zip(times, times[1:])) or any(t < start - .1 or t > end + .1 for t in times):
        raise RuntimeError("Non-monotone or out-of-window frame timestamps")
    records = [{"name": f.name, "t": t, "kept": True, "via": "sample-or-scene"} for f, t in zip(files, times)]
    core.write_frames_json(str(folder), records)
    core.make_grids(str(folder / "frames"), str(folder))
    gaps = [times[0] - start, end - times[-1]] + [b - a for a, b in zip(times, times[1:])]
    return {"frame_count": count, "max_sample_gap_sec": max(gaps), "interval_sec": interval}


def prepare(args):
    source = Path(args.source).resolve(strict=True)
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    metadata, duration = probe(source)
    settings = {k: getattr(args, k) for k in ("window", "overlap", "interval", "width", "model", "language", "no_transcribe")}
    stat = source.stat()
    identity = {"path": str(source), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    source_id = hashlib.sha256(str(source).casefold().encode()).hexdigest()[:12]
    info = {"id": source_id, **identity, "duration_sec": duration, "settings": settings}
    if (out / "source.json").exists() and read(out / "source.json") != info:
        raise ValueError("Source or settings changed. Use a new output folder.")
    write(out / "source.json", info)
    write(out / "probe.json", metadata)
    audio_streams = [s["index"] for s in metadata["streams"] if s["codec_type"] == "audio"]
    model = None
    processed = 0
    total = math.ceil(duration / args.window)
    for index in range(total):
        folder = out / f"packet-{index:04d}"
        if (folder / "complete.json").exists():
            record = read(folder / "complete.json")
            attempt = folder / record["attempt"]
            if not all((attempt / f).is_file() for f in ["packet.json", "frames.json", "transcript.json"]):
                raise RuntimeError(f"Incomplete cached packet {folder}; inspect it before resuming")
            continue
        if args.limit_packets and processed >= args.limit_packets:
            break
        start = max(0, index * args.window - args.overlap)
        end = min(duration, (index + 1) * args.window + args.overlap)
        attempt = folder / ("attempt-" + uuid.uuid4().hex[:8])
        attempt.mkdir(parents=True)
        print(f"Preparing {index + 1}/{total}: {start:.3f}–{end:.3f}s", flush=True)
        try:
            visual = extract(source, attempt, start, end, args.interval, args.width)
            segments = []
            transcript_status = "not_requested" if args.no_transcribe else "no_audio_stream"
            stream_status = {}
            if audio_streams and not args.no_transcribe:
                if model is None:
                    from faster_whisper import WhisperModel
                    model = WhisperModel(args.model, device="cpu", compute_type="int8")
                for audio_index in audio_streams:
                    audio = attempt / f"audio-stream-{audio_index}.wav"
                    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(source), "-t", str(end-start),
                                    "-map", f"0:{audio_index}", "-vn", "-ac", "1", "-ar", "16000", str(audio)], check=True)
                    iterator, _ = model.transcribe(str(audio), language=None if args.language == "auto" else args.language,
                                                   vad_filter=True, condition_on_previous_text=False)
                    stream_segments = [{"start": round(s.start + start, 3), "end": round(s.end + start, 3),
                                        "text": s.text, "audio_stream": audio_index} for s in iterator]
                    stream_status[str(audio_index)] = "transcribed" if stream_segments else "no_speech_detected"
                    segments.extend(stream_segments)
                segments.sort(key=lambda s: s["start"])
                transcript_status = "transcribed" if segments else "no_speech_detected"
            write(attempt / "transcript.json", {"status": transcript_status, "streams": stream_status, "segments": segments})
            write(attempt / "packet.json", {"source_id": source_id, "start_sec": start, "end_sec": end,
                                            "core_start_sec": index * args.window, "core_end_sec": min(duration, (index+1)*args.window),
                                            "transcript_status": transcript_status, **visual})
            write(folder / "review.json", {"status": "unreviewed", "inspected_sheets": [], "event_ids": []})
            write(folder / "complete.json", {"attempt": attempt.name})
        except Exception as exc:
            write(attempt / "error.json", {"error": str(exc)})
            raise
        processed += 1
    complete = sum((out / f"packet-{i:04d}" / "complete.json").exists() for i in range(total))
    print(json.dumps({"prepared_packets": complete, "total_packets": total, "new_packets": processed,
                      "review_status": "See each review.json; preparation is not review"}))


def detail(args):
    source = Path(args.source).resolve(strict=True)
    _, duration = probe(source)
    if not 0 <= args.start < args.end <= duration:
        raise ValueError("Detail interval must lie within the source duration")
    folder = Path(args.out).resolve()
    if folder.exists() and any(folder.iterdir()):
        raise ValueError("Use an empty detail output folder")
    folder.mkdir(parents=True, exist_ok=True)
    result = extract(source, folder, args.start, args.end, args.interval, args.width)
    write(folder / "packet.json", {"source": str(source), "start_sec": args.start, "end_sec": args.end, **result})
    print(json.dumps(result))


def clock(seconds):
    millis = round(seconds * 1000)
    return f"{millis//3600000:02d}:{millis//60000%60:02d}:{millis//1000%60:02d}.{millis%1000:03d}"


def marker_clock(seconds):
    value = clock(seconds)
    if value.startswith("00:"):
        value = value[3:]
    return value.removesuffix(".000")


def marker_label(value):
    """Validate authored visual copy; never truncate a description into a label."""
    value = text(value, "marker_title: author a 1–4-word visual label")
    if (not 1 <= len(value.split()) <= 4 or value != " ".join(value.split())
            or re.search(r"[\[\]|\r\n]|\.\.\.|…", value)):
        raise ValueError("Marker name must be a clean 1–4-word label, without metadata or truncation")
    return value


def validate_marker_presentation(marker):
    marker_label(marker["name"])
    key = text(marker["key"], "marker key")
    if any(c in key for c in "[]\r\n"):
        raise ValueError("Invalid marker key")
    comments = text(marker["comments"], "marker comments")
    if re.findall(r"\[VOD:([^\[\]\r\n]+)\]", comments) != [key]:
        raise ValueError("Marker comments must contain exactly one matching [VOD:key] reference")


def export_events(data):
    if data.get("schema_version") != 1:
        raise ValueError("Expected events schema_version 1")
    sources = {}
    paths = set()
    for src in data["sources"]:
        sid = text(src["id"], "source id")
        path = text(src["path"], "source path")
        # Accept Windows absolute paths even when exported on another OS.
        from pathlib import PureWindowsPath
        if not (Path(path).is_absolute() or PureWindowsPath(path).is_absolute()):
            raise ValueError("Source paths must be absolute")
        key = path.replace("\\", "/").casefold()
        if sid in sources or key in paths:
            raise ValueError("Duplicate source id or path")
        paths.add(key)
        label = src.get("label", Path(path.replace(chr(92), '/')).stem)
        sources[sid] = {"id": sid, "path": path, "label": text(label, "source label"),
                        "duration_sec": number(src["duration_sec"], "duration", .001), "markers": []}
        if 'pov' in src:
            sources[sid]['pov'] = text(src['pov'], 'source POV bin').strip()
    ids = set()
    event_map = {e["id"]: e for e in data["events"]}

    def link_line(view, heading=None, include_alignment=True):
        source = sources[view["source_id"]]
        role = text(view.get("marker_role", view["role"]), "marker role")
        kind = heading or text(view.get("marker_type", "POV"), "marker type")
        timing = ""
        if include_alignment and view["alignment"] == "estimated":
            timing = f" [CHECK sync ±{view['uncertainty_sec']}s]"
        elif include_alignment and view["uncertainty_sec"]:
            timing = f" (±{view['uncertainty_sec']}s)"
        return (f"{kind} {source['label']} {marker_clock(view['start_sec'])}–"
                f"{marker_clock(view['end_sec'])} — {role}{timing}")

    for event in data["events"]:
        eid = text(event["id"], "event id")
        if eid in ids or any(c in eid for c in "[]\r\n"):
            raise ValueError("Duplicate or invalid event id")
        ids.add(eid)
        title, why = text(event["title"], "title"), text(event["why"], "why")
        status = event["status"]
        if status not in ("candidate", "context", "uncertain"):
            raise ValueError("Invalid editorial status")
        views = event["perspectives"]
        if not views:
            raise ValueError("Each event needs an evidenced perspective")
        seen = set()
        for view in views:
            sid = view["source_id"]
            if sid not in sources or sid in seen:
                raise ValueError("Unknown or duplicate perspective source")
            seen.add(sid)
            start, end = number(view["start_sec"], "start"), number(view["end_sec"], "end")
            if not start < end <= sources[sid]["duration_sec"]:
                raise ValueError("Marker interval outside source or empty")
            text(view["role"], "role"); text(view["evidence"], "evidence")
            uncertainty = number(view["uncertainty_sec"], "uncertainty")
            if view["alignment"] not in ("observed", "estimated") or (view["alignment"] == "estimated" and uncertainty <= 0):
                raise ValueError("Estimated alignment requires positive uncertainty")
        # Display copy is authored separately: long analysis titles and editorial
        # rationale must never silently become Premiere names/descriptions.
        short_title = marker_label(event.get("marker_title"))
        summary = text(event.get("marker_summary"), "marker_summary: describe what happened")
        review_note = event.get("review_note")
        if review_note is not None:
            text(review_note, "review note")
        related = []
        for relation in event.get("related_events", []):
            target = event_map.get(relation["event_id"])
            relationship = relation["relationship"]
            if target is None or target["id"] == eid or relationship not in ("earlier", "later", "setup", "payoff", "related"):
                raise ValueError("Invalid related event")
            matched = [v for v in target["perspectives"] if v["source_id"] == relation["source_id"]]
            if len(matched) != 1:
                raise ValueError("Related event must identify an existing perspective")
            related.append(link_line(matched[0], relationship.upper(), include_alignment=False))
        for view in views:
            name = marker_label(view.get("marker_title", short_title))
            lines = [text(view.get("marker_summary", summary), "perspective marker summary")]
            lines.extend(link_line(v) for v in views if v["source_id"] != view["source_id"])
            lines.extend(related)
            if view["alignment"] == "estimated":
                lines.append(f"CHECK sync: this POV is estimated ±{view['uncertainty_sec']}s.")
            if review_note:
                lines.append(f"CHECK: {review_note}")
            elif status == "uncertain":
                lines.append("CHECK: Confirm the event and wording.")
            # Stable identity survives XML/UXP import without cluttering Name.
            # Source paths, raw evidence and provenance remain in the sidecar.
            lines.append(f"Ref [VOD:{eid}]")
            comments = "\n".join(lines)
            marker = {"key": eid, "name": name, "comments": comments,
                      "start_sec": view["start_sec"], "end_sec": view["end_sec"]}
            validate_marker_presentation(marker)
            sources[view["source_id"]]["markers"].append(marker)
    return {"schema": "vod-source-markers/v1", "sources": [s for s in sources.values() if s["markers"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    for name in ("prepare", "detail"):
        p = sub.add_parser(name)
        p.add_argument("--source", required=True); p.add_argument("--out", required=True)
        p.add_argument("--interval", type=float, default=5); p.add_argument("--width", type=int, default=960)
        if name == "prepare":
            p.add_argument("--window", type=float, default=300); p.add_argument("--overlap", type=float, default=15)
            p.add_argument("--model", default="small"); p.add_argument("--language", default="auto")
            p.add_argument("--no-transcribe", action="store_true"); p.add_argument("--limit-packets", type=int, default=0)
        else:
            p.add_argument("--start", type=float, required=True); p.add_argument("--end", type=float, required=True)
    p = sub.add_parser("export"); p.add_argument("--events", required=True); p.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.command == "doctor":
        result = {k: shutil.which(k) for k in ("ffmpeg", "ffprobe")}
        for k in ("claude-real-video", "faster-whisper"):
            try: result[k] = importlib.metadata.version(k)
            except importlib.metadata.PackageNotFoundError: result[k] = None
        print(json.dumps(result, indent=2)); return 0 if all(result.values()) else 1
    if args.command == "export":
        write(args.out, export_events(read(args.events))); print(f"Wrote {args.out}"); return 0
    number(args.interval, "interval", .01); number(args.width, "width", 64)
    if args.command == "prepare":
        number(args.window, "window", 1); number(args.overlap, "overlap"); number(args.limit_packets, "limit-packets")
        prepare(args)
    else:
        detail(args)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, KeyError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
