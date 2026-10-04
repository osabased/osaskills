"""Owned, loopback-only whisper.cpp worker; one model per preparation run."""
from copy import deepcopy
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import uuid
import wave

from vod import number, read, text, write
from whisper_cpp import convert_segments, file_hash, runtime_identity, verify_backend


DECODING = {'best_of': '5', 'beam_size': '5', 'temperature': '0', 'temperature_inc': '0.2',
            'token_timestamps': 'false', 'no_language_probabilities': 'true', 'max_len': '0',
            'offset_t': '0', 'prompt': '', 'carry_initial_prompt': 'false', 'vad': 'false',
            'translate': 'false', 'diarize': 'false', 'detect_language': 'false',
            'response_format': 'verbose_json'}


def worker_identity(config, executable):
    executable = Path(executable).resolve(strict=True)
    if not executable.is_file(): raise ValueError('Whisper server executable is required')
    dlls = {p.name: file_hash(p) for p in sorted(executable.parent.glob('*.dll'))}
    if dlls != config['dll_sha256']:
        raise ValueError('Whisper server must use the same runtime DLLs as the verified CLI')
    return {**config, 'transport': 'owned-server/v1', 'server': str(executable),
            'server_sha256': file_hash(executable), 'decoding': DECODING.copy()}


def convert_response(raw, source_start, stream):
    if not isinstance(raw, dict) or not isinstance(raw.get('segments'), list):
        raise ValueError('Missing whisper-server segments; inspect raw response')
    rows = []
    for segment in raw['segments']:
        start = number(segment['start'], 'server speech start')
        end = number(segment['end'], 'server speech end')
        rows.append({'offsets': {'from': round(start * 1000), 'to': round(end * 1000)},
                     'text': text(segment['text'], 'server speech text')})
    # Keep questionable source bounds for the existing evidence validator.
    return convert_segments({'transcription': rows}, source_start, stream)


def multipart(audio, language):
    with wave.open(str(audio)) as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getcomptype()) != (1, 2, 16000, 'NONE'):
            raise ValueError('Worker input must be mono 16 kHz PCM16 WAV')
    boundary = 'vod-' + uuid.uuid4().hex
    chunks = []
    for key, value in {**DECODING, 'language': language}.items():
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
    chunks.extend([f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="audio.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode(),
                   Path(audio).read_bytes(), f'\r\n--{boundary}--\r\n'.encode()])
    return b''.join(chunks), 'multipart/form-data; boundary=' + boundary


class WhisperWorker:
    def __init__(self, config, folder, startup_timeout=90, request_timeout=600):
        self.config = deepcopy(config)
        self.folder = Path(folder) / uuid.uuid4().hex
        self.proc = self.log = None
        self.startup_timeout, self.request_timeout = startup_timeout, request_timeout
        self.failed = False

    def __enter__(self): return self

    def __exit__(self, *args): self.close()

    def close(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try: self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill(); self.proc.wait(timeout=10)
        if self.log is not None:
            self.log.close(); self.log = None

    def start(self):
        if self.failed: raise RuntimeError('Whisper worker failed; resume preparation to retry')
        if self.proc is not None:
            if self.proc.poll() is not None: raise RuntimeError('Whisper worker exited; resume preparation to retry')
            return
        base = runtime_identity(self.config['cli'], self.config['model'], self.config['device'],
                                self.config['threads'], self.config['gpu'])
        if worker_identity(base, self.config['server']) != self.config:
            raise ValueError('Whisper runtime changed before worker startup')
        self.folder.mkdir(parents=True, exist_ok=False)
        public = self.folder / 'public'; public.mkdir()
        self.log_path = self.folder / 'server.log'
        self.log = self.log_path.open('w', encoding='utf-8')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); self.port = sock.getsockname()[1]
        self.route = '/' + uuid.uuid4().hex
        command = [self.config['server'], '-m', self.config['model'], '-t', str(self.config['threads']),
                   '-mc', '0', '-bo', '5', '-bs', '5', '-nlp', '--host', '127.0.0.1', '--port', str(self.port),
                   '--public', str(public), '--request-path', self.route]
        command += ['-ng'] if self.config['device'] == 'cpu' else ['-dev', str(self.config['gpu'])]
        started = time.perf_counter()
        try:
            self.proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=self.log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            deadline = time.monotonic() + self.startup_timeout
            while True:
                if self.proc.poll() is not None:
                    raise RuntimeError(f'Whisper server exited; inspect {self.log_path}')
                try:
                    connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=.25)
                    try:
                        connection.request('GET', self.route + '/health')
                        response = connection.getresponse(); response.read()
                        if response.status == 200: break
                    finally: connection.close()
                except (OSError, http.client.HTTPException): pass
                if time.monotonic() > deadline: raise TimeoutError('Whisper server startup timed out')
                time.sleep(.05)
            verify_backend(self.log_path.read_text(encoding='utf-8', errors='replace'), self.config['device'])
            write(self.folder / 'worker.json', {'runtime': self.config, 'startup_sec': time.perf_counter()-started,
                                              'pid': self.proc.pid, 'command': command})
        except BaseException:
            self.failed = True; self.close(); raise

    def transcribe(self, audio, output_prefix, source_start, stream, language):
        prefix = Path(output_prefix).resolve()
        raw_path, json_path = Path(str(prefix)+'-server.json'), Path(str(prefix)+'.json')
        log_path, run_path = Path(str(prefix)+'.log'), Path(str(prefix)+'-run.json')
        if any(p.exists() for p in (raw_path, json_path, log_path, run_path)):
            raise ValueError('Use a fresh whisper.cpp output prefix')
        audio = Path(audio).resolve(strict=True)
        number(source_start, 'source start')
        if not isinstance(language, str) or not language.isalpha():
            raise ValueError('Whisper language must be a language code or auto')
        body, content_type = multipart(audio, language)
        self.start()
        started = time.perf_counter()
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=self.request_timeout)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        try:
            connection.request('POST', self.route+'/inference', body, {'Content-Type': content_type})
            response = connection.getresponse(); raw = response.read()
            raw_path.write_bytes(raw)
            if response.status != 200: raise RuntimeError(f'Whisper request failed ({response.status}); inspect {raw_path}')
            data = json.loads(raw)
            segments = convert_response(data, source_start, stream)
            # Preserve the CLI evidence shape and the unmodified server JSON.
            canonical = {'result': {'language': data.get('language')}, 'transcription': [
                {'offsets': {'from': round(s['start']*1000), 'to': round(s['end']*1000)}, 'text': s['text']}
                for s in data['segments']]}
            write(json_path, canonical)
            log_path.write_text(f'Owned worker log: {self.log_path}\nRuntime: {self.config["device"]}\n', encoding='utf-8')
            write(run_path, {'runtime': self.config, 'language': language, 'detected_language': data.get('language'),
                'elapsed_sec': time.perf_counter()-started, 'source_start_sec': source_start, 'audio_stream': stream,
                'audio_sha256': file_hash(audio), 'raw_json': str(json_path), 'server_raw_json': raw_path.name,
                'log': str(log_path), 'worker_log': str(self.log_path), 'worker_startup_in_request_time': False})
            return segments
        except BaseException:
            self.failed = True; self.close(); raise
        finally: connection.close()
