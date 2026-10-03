"""Adapt whisper.cpp CLI JSON to source-local, per-stream transcript evidence."""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import time

from vod import number, read, text, write


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def runtime_identity(cli, model, device='vulkan', threads=4, gpu=0):
    cli, model = Path(cli).resolve(strict=True), Path(model).resolve(strict=True)
    if not cli.is_file() or not model.is_file():
        raise ValueError('whisper.cpp needs a CLI executable and a GGML model file')
    if device not in ('vulkan', 'cpu'):
        raise ValueError('whisper.cpp device must be vulkan or cpu')
    if not isinstance(threads, int) or isinstance(threads, bool) or threads < 1:
        raise ValueError('Whisper thread count must be a positive integer')
    if not isinstance(gpu, int) or isinstance(gpu, bool) or gpu < 0:
        raise ValueError('Whisper GPU index must be a nonnegative integer')
    return {'backend': 'whisper.cpp', 'cli': str(cli), 'cli_sha256': file_hash(cli),
            'model': str(model), 'model_sha256': file_hash(model), 'device': device,
            'gpu': gpu, 'threads': threads, 'vad': False, 'max_context': 0,
            'dll_sha256': {p.name: file_hash(p) for p in sorted(cli.parent.glob('*.dll'))}}


def convert_segments(raw, source_start, stream):
    number(source_start, 'source start')
    if isinstance(stream, bool) or not isinstance(stream, int) or stream < 0:
        raise ValueError('Invalid audio stream index')
    if not isinstance(raw.get('transcription'), list):
        raise ValueError('Missing whisper.cpp transcription array; inspect the raw JSON')
    result = []
    for row in raw['transcription']:
        # CLI offsets are integer milliseconds, not its human-readable timestamps.
        a = number(row['offsets']['from'], 'Whisper start milliseconds') / 1000
        b = number(row['offsets']['to'], 'Whisper end milliseconds') / 1000
        value = text(row['text'], 'Whisper transcript')
        # Preserve questionable bounds for packet_evidence to flag; never clamp them.
        result.append({'start': round(source_start + a, 3), 'end': round(source_start + b, 3),
                       'text': value, 'audio_stream': stream})
    return result


def verify_backend(log, device):
    # Listing a GPU or compiling Vulkan support does not prove it was selected.
    if device == 'vulkan' and not re.search(r'whisper_backend_init_gpu: using Vulkan\d+ backend', log):
        raise RuntimeError('Vulkan inference was requested but not confirmed in the runtime log; inspect it, do not silently fall back')


def transcribe(audio, output_prefix, source_start, stream, config, language):
    prefix = Path(output_prefix).resolve()
    json_path = Path(str(prefix) + '.json')
    log_path = Path(str(prefix) + '.log')
    if json_path.exists() or log_path.exists():
        raise ValueError('Use a fresh whisper.cpp output prefix')
    prefix.parent.mkdir(parents=True, exist_ok=True)
    command = [config['cli'], '-m', config['model'], '-f', str(Path(audio).resolve()),
               '-oj', '-of', str(prefix), '-l', language, '-t', str(config['threads']), '-mc', '0']
    if config['device'] == 'cpu':
        command.append('-ng')
    else:
        command.extend(['-dev', str(config['gpu'])])
    start = time.perf_counter()
    with log_path.open('w', encoding='utf-8') as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=dict(os.environ))
    elapsed = time.perf_counter() - start
    if completed.returncode or not json_path.is_file():
        raise RuntimeError(f'whisper.cpp failed or produced no JSON; inspect {log_path}')
    log = log_path.read_text(encoding='utf-8', errors='replace')
    verify_backend(log, config['device'])
    raw = read(json_path)
    segments = convert_segments(raw, source_start, stream)
    write(Path(str(prefix) + '-run.json'), {'runtime': config, 'language': language,
          'detected_language': raw.get('result', {}).get('language'), 'elapsed_sec': elapsed,
          'source_start_sec': source_start, 'audio_stream': stream, 'audio_sha256': file_hash(audio),
          'raw_json': str(json_path), 'log': str(log_path), 'command': command})
    return segments
