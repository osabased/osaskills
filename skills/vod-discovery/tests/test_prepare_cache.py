"""Preparation retry/invalidation checks without downloading a model or using user media."""
from collections import Counter
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import vod
from stage_cache import StageCache, file_lock, file_hash


class PrepareCaches(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.mp4'; self.source.write_bytes(b'source fixture')
        self.frames = 0; self.audio = Counter(); self.speech = Counter()
        self.streams = [1]; self.fail_stream = None; self.empty = False; self.mutate_source = False
        self.audio_duration = 2
        self.duration = 2; self.effective_revision = 'fixture'
        self.model = SimpleNamespace(transcribe=self.transcribe)
        self.addCleanup(patch.stopall)
        patch.object(vod, 'probe', side_effect=lambda source: ({'streams': [
            {'codec_type': 'video', 'index': 0}, *[{'codec_type': 'audio', 'index': i} for i in self.streams]]}, self.duration)).start()
        patch.object(vod, 'extract', side_effect=self.extract).start()
        patch.object(vod, 'tool_identity', return_value={'version': 'fixture ffmpeg'}).start()
        patch.object(vod, 'faster_whisper_identity', side_effect=lambda name: (
            {'model': name, 'backend': 'fixture', 'revision': self.effective_revision}, name)).start()
        self.load = patch.object(vod, 'load_faster_whisper', return_value=self.model).start()
        patch.object(vod.subprocess, 'run', side_effect=self.encode_audio).start()

    def args(self, out='out', **changes):
        args = SimpleNamespace(source=str(self.source), out=str(self.root / out), cache_dir=str(self.root / 'cache'),
            window=300, overlap=15, interval=5, width=960, model='small', language='auto', no_transcribe=False,
            limit_packets=0, asr_backend='faster-whisper')
        for name, value in changes.items(): setattr(args, name, value)
        return args

    def run_prepare(self, args):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            vod.prepare(args)
        return json.loads(output.getvalue().splitlines()[-1])

    def extract(self, source, folder, start, end, interval, width):
        self.frames += 1
        (folder / 'frames').mkdir(); (folder / 'grids').mkdir()
        (folder / 'frames/raw_000001.jpg').write_bytes(b'frame fixture')
        (folder / 'grids/grid_01.jpg').write_bytes(b'contact sheet fixture')
        vod.write(folder / 'frames.json', {'frames': [{'file': 'raw_000001.jpg', 'timestamp_sec': start + .5}]})
        if self.mutate_source:
            self.source.write_bytes(b'changed media fixture with new size')
        return {'frame_count': 1, 'interval_sec': interval, 'max_sample_gap_sec': 1.5}

    def encode_audio(self, command, **kwargs):
        stream = int(command[command.index('-map') + 1].split(':')[1]); self.audio[stream] += 1
        with wave.open(command[-1], 'wb') as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(16000)
            wav.writeframes(b'\0' * round(32000 * self.audio_duration))
        return subprocess.CompletedProcess(command, 0)

    def transcribe(self, audio, **kwargs):
        stream = int(Path(audio).stem.rsplit('-', 1)[1]); self.speech[stream] += 1
        if self.fail_stream == stream:
            self.fail_stream = None
            raise RuntimeError('transcription fixture failure')
        segments = [] if self.empty else [SimpleNamespace(start=.25, end=.75, text='Quiet setup.')]
        return iter(segments), None

    def attempt(self, out='out'):
        packet = self.root / out / 'packet-0000'
        return packet / vod.read(packet / 'complete.json')['attempt']

    def test_failed_transcription_reuses_frames_and_audio(self):
        self.fail_stream = 1
        with self.assertRaisesRegex(RuntimeError, 'fixture failure'): self.run_prepare(self.args())
        result = self.run_prepare(self.args())
        self.assertEqual((self.frames, self.audio[1], self.speech[1]), (1, 1, 2))
        self.assertEqual(result['cache']['stages']['frames']['reused'], 1)
        self.assertEqual(result['cache']['stages']['audio']['reused'], 1)
        self.assertEqual(result['cache']['stages']['transcript']['generated'], 1)
        self.assertGreaterEqual(result['elapsed_sec'], 0)
        self.assertEqual(vod.read(self.attempt() / 'transcript.json')['segments'][0]['start'], .25)
        self.assertTrue(list((self.root / 'cache/transcript').glob('incomplete-*/error.json')))

    def test_second_stream_failure_keeps_first_stream(self):
        self.streams = [1, 2]; self.fail_stream = 2
        with self.assertRaises(RuntimeError): self.run_prepare(self.args())
        result = self.run_prepare(self.args())
        self.assertEqual(self.frames, 1)
        self.assertEqual(dict(self.audio), {1: 1, 2: 1})
        self.assertEqual(dict(self.speech), {1: 1, 2: 2})
        self.assertEqual(result['cache']['stages']['transcript']['reused'], 1)
        self.assertEqual(vod.read(self.attempt() / 'transcript.json')['streams'], {'1': 'transcribed', '2': 'transcribed'})

    def test_model_change_in_fresh_output_reuses_media_stages(self):
        self.run_prepare(self.args())
        result = self.run_prepare(self.args('different-model', model='large'))
        self.assertEqual((self.frames, self.audio[1], self.speech[1]), (1, 1, 2))
        self.assertEqual(result['cache']['stages']['transcript']['generated'], 1)
        with self.assertRaisesRegex(ValueError, 'Source or settings changed'):
            self.run_prepare(self.args(model='large'))

    def test_language_change_reuses_media_but_not_transcript(self):
        self.run_prepare(self.args())
        self.run_prepare(self.args('english', language='en'))
        self.assertEqual((self.frames, self.audio[1], self.speech[1]), (1, 1, 2))

    def test_frame_settings_change_only_invalidates_visuals(self):
        self.run_prepare(self.args())
        result = self.run_prepare(self.args('dense', interval=1, width=1280))
        self.assertEqual((self.frames, self.audio[1], self.speech[1]), (2, 1, 1))
        self.assertEqual(result['cache']['stages']['transcript']['reused'], 1)

    def test_quiet_transcript_is_reused_and_does_not_discard_frames(self):
        self.empty = True
        self.run_prepare(self.args())
        self.run_prepare(self.args('quiet'))
        self.assertEqual((self.frames, self.audio[1], self.speech[1]), (1, 1, 1))
        transcript = vod.read(self.attempt('quiet') / 'transcript.json')
        self.assertEqual(transcript['status'], 'no_speech_detected')
        self.assertTrue((self.attempt('quiet') / 'frames/raw_000001.jpg').is_file())

    def test_no_transcribe_visual_pilot_can_seed_fresh_full_preparation(self):
        self.run_prepare(self.args(no_transcribe=True))
        self.assertEqual(dict(self.audio), {}); self.load.assert_not_called()
        self.assertEqual(vod.read(self.attempt() / 'transcript.json')['status'], 'not_requested')
        self.run_prepare(self.args('full'))
        self.assertEqual((self.frames, self.audio[1], self.speech[1]), (1, 1, 1))

    def test_no_audio_does_not_load_model(self):
        self.streams = []
        self.run_prepare(self.args())
        self.load.assert_not_called()
        self.assertEqual(vod.read(self.attempt() / 'transcript.json')['status'], 'no_audio_stream')

    def test_source_mutation_does_not_publish_stage_or_packet(self):
        self.mutate_source = True
        with self.assertRaisesRegex(RuntimeError, 'Source changed'): self.run_prepare(self.args())
        self.assertFalse((self.root / 'out/packet-0000/complete.json').exists())
        self.assertFalse([p for p in (self.root / 'cache/frames').glob('*/manifest.json')
                          if not p.parent.name.startswith(('incomplete-', 'corrupt-'))])
        self.assertTrue(list((self.root / 'cache/frames').glob('incomplete-*/error.json')))
        self.assertEqual(dict(self.audio), {})

    def test_corrupt_visual_artifact_rebuilds_only_visual_stage(self):
        self.run_prepare(self.args())
        cache_frame = next((self.root / 'cache/frames').glob('*/data/frames/raw_000001.jpg'))
        cache_frame.write_bytes(b'corrupt')
        self.run_prepare(self.args('repaired'))
        self.assertEqual((self.frames, self.audio[1], self.speech[1]), (2, 1, 1))
        self.assertTrue(list((self.root / 'cache/frames').glob('corrupt-*')))

    def test_audio_stream_ending_before_video_is_preserved(self):
        self.audio_duration = 1
        self.run_prepare(self.args())
        self.assertEqual(vod.read(self.attempt() / 'transcript.json')['status'], 'transcribed')
        with wave.open(str(self.attempt() / 'audio-stream-1.wav'), 'rb') as wav:
            self.assertEqual(wav.getnframes() / wav.getframerate(), 1)

    def test_completed_reviews_and_attempts_are_unchanged(self):
        self.run_prepare(self.args())
        review = self.root / 'out/packet-0000/review.json'
        vod.write(review, {'status': 'reviewed', 'event_ids': ['keep'], 'notes': 'Human choice'})
        before = review.read_bytes(); attempt = self.attempt()
        before_transcript = (attempt / 'transcript.json').read_bytes()
        with patch.object(vod, 'faster_whisper_identity', side_effect=AssertionError('model resolution on completed resume')):
            result = self.run_prepare(self.args())
        self.assertEqual(result['new_packets'], 0)
        self.assertEqual(review.read_bytes(), before)
        self.assertEqual(self.attempt(), attempt)
        self.assertEqual((attempt / 'transcript.json').read_bytes(), before_transcript)

    def test_copying_does_not_alias_cache_and_attempt(self):
        self.run_prepare(self.args())
        frame = self.attempt() / 'frames/raw_000001.jpg'
        frame.write_bytes(b'edited attempt')
        self.run_prepare(self.args('clean'))
        self.assertEqual(self.frames, 1)
        self.assertEqual((self.attempt('clean') / 'frames/raw_000001.jpg').read_bytes(), b'frame fixture')

    def test_output_lock_blocks_concurrent_preparers(self):
        out = self.root / 'out'; out.mkdir()
        with file_lock(out / '.prepare.lock'):
            with self.assertRaisesRegex(RuntimeError, 'already active'): self.run_prepare(self.args())

    def test_effective_model_change_cannot_mix_partial_preparation(self):
        self.duration = 4
        self.run_prepare(self.args(window=2, overlap=0, limit_packets=1))
        first = self.attempt(); before = (first / 'transcript.json').read_bytes()
        self.effective_revision = 'changed-model-weights'
        with self.assertRaisesRegex(ValueError, 'Effective speech model or runtime changed'):
            self.run_prepare(self.args(window=2, overlap=0))
        self.assertEqual(self.frames, 1)
        self.assertFalse((self.root / 'out/packet-0001/complete.json').exists())
        self.assertEqual((first / 'transcript.json').read_bytes(), before)

    def test_partial_legacy_fast_preparation_requires_fresh_output(self):
        self.duration = 4
        self.run_prepare(self.args(window=2, overlap=0, limit_packets=1))
        (self.root / 'out/asr-runtime.json').unlink()
        with self.assertRaisesRegex(ValueError, 'partial legacy preparation'):
            self.run_prepare(self.args(window=2, overlap=0))
        self.assertEqual(self.frames, 1)

    def test_cpp_cached_diagnostics_resolve_from_materialized_run_file(self):
        cli = self.root / 'whisper-cli.exe'; cli.write_bytes(b'cli fixture')
        model = self.root / 'ggml-model.bin'; model.write_bytes(b'model fixture')
        config = {'backend': 'whisper.cpp', 'cli': str(cli), 'model': str(model), 'device': 'vulkan'}
        calls = []
        def cpp_transcribe(audio, prefix, source_start, stream, runtime, language):
            calls.append(1)
            raw, log = Path(str(prefix) + '.json'), Path(str(prefix) + '.log')
            vod.write(raw, {'transcription': []}); log.write_text('fixture Vulkan backend')
            vod.write(Path(str(prefix) + '-run.json'), {'raw_json': str(raw), 'log': str(log),
                'command': ['whisper-cli', '-f', str(audio), '-of', str(prefix)]})
            return [{'start': source_start + .25, 'end': source_start + .75, 'text': 'Quiet setup.', 'audio_stream': stream}]
        def cpp_args(out):
            return self.args(out, asr_backend='whisper-cpp', whisper_cli=str(cli), whisper_model=str(model),
                             whisper_device='vulkan', whisper_threads=4, whisper_gpu=0)
        with patch('whisper_cpp.runtime_identity', return_value=config), patch('whisper_cpp.transcribe', side_effect=cpp_transcribe):
            self.run_prepare(cpp_args('cpp')); self.run_prepare(cpp_args('cpp-reused'))
        self.assertEqual(len(calls), 1)
        first_run = vod.read(self.attempt('cpp') / 'whisper-stream-1-run.json')
        run = vod.read(self.attempt('cpp-reused') / 'whisper-stream-1-run.json')
        self.assertEqual(run['command'], first_run['command'])
        self.assertTrue(run['command_paths_are_historical'])
        self.assertTrue(run['artifact_paths_relative_to_run_file'])
        self.assertTrue((self.attempt('cpp-reused') / run['raw_json']).is_file())
        self.assertTrue((self.attempt('cpp-reused') / run['log']).is_file())


class CacheValidation(unittest.TestCase):
    def test_unsafe_manifest_entry_never_reads_external_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); cache = StageCache(root / 'cache'); outside = root / 'secret.txt'
            outside.write_bytes(b'not a cache artifact')
            calls = []
            def produce(data):
                calls.append(1); (data / 'value.txt').write_bytes(b'cached'); return {'ok': True}
            data, _, _ = cache.get('test', {'version': 1}, produce)
            manifest = json.loads((data.parent / 'manifest.json').read_text())
            manifest['artifacts']['../../secret.txt'] = {'size': outside.stat().st_size, 'sha256': file_hash(outside)}
            (data.parent / 'manifest.json').write_text(json.dumps(manifest))
            import stage_cache
            original = stage_cache.file_hash
            def checked_hash(path):
                self.assertNotEqual(Path(path).resolve(), outside.resolve())
                return original(path)
            with patch.object(stage_cache, 'file_hash', side_effect=checked_hash):
                _, _, reused = cache.get('test', {'version': 1}, produce)
            self.assertFalse(reused); self.assertEqual(len(calls), 2)
            self.assertEqual(outside.read_bytes(), b'not a cache artifact')

    def test_failed_stage_preserved_and_never_reused(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = StageCache(temp)
            def fail(data):
                (data / 'partial.txt').write_bytes(b'incomplete')
                raise RuntimeError('stage failed')
            with self.assertRaises(RuntimeError): cache.get('test', {'v': 1}, fail)
            def complete(data):
                (data / 'done.txt').write_bytes(b'complete'); return {'ok': True}
            _, result, reused = cache.get('test', {'v': 1}, complete)
            self.assertFalse(reused); self.assertEqual(result, {'ok': True})
            self.assertTrue(list(Path(temp).glob('test/incomplete-*/error.json')))

    def test_effective_local_model_identity_hashes_the_weights(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for name in ('config.json', 'model.bin', 'tokenizer.json', 'vocabulary.json'):
                (folder / name).write_bytes(b'model fixture')
            first, effective = vod.faster_whisper_identity(str(folder))
            (folder / 'model.bin').write_bytes(b'changed weights')
            second, _ = vod.faster_whisper_identity(str(folder))
            self.assertNotEqual(first['model_sha256']['model.bin'], second['model_sha256']['model.bin'])
            self.assertEqual(effective, str(folder.resolve()))
            self.assertIn('ctranslate2', first['versions'])


if __name__ == '__main__': unittest.main()
