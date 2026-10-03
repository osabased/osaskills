from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from whisper_cpp import convert_segments, verify_backend


class WhisperCppClocks(unittest.TestCase):
    def test_milliseconds_source_offset_and_stream_identity(self):
        raw = {'transcription': [{'offsets': {'from': 1250, 'to': 3500}, 'text': 'Take the left path.'}]}
        self.assertEqual(convert_segments(raw, 285, 2), [
            {'start': 286.25, 'end': 288.5, 'text': 'Take the left path.', 'audio_stream': 2}])

    def test_invalid_bounds_preserved_for_evidence_validation(self):
        raw = {'transcription': [{'offsets': {'from': 30000, 'to': 29000}, 'text': 'Uncertain.'}]}
        self.assertEqual(convert_segments(raw, 10, 1)[0]['end'], 39)
        with self.assertRaises(ValueError):
            convert_segments({'transcription': [{'offsets': {'from': float('nan'), 'to': 1}, 'text': 'x'}]}, 0, 1)

    def test_device_enumeration_is_not_backend_selection(self):
        for log in ['ggml_vulkan: Found 1 Vulkan devices', 'VULKAN = 1 | CPU = 1', 'using CPU backend']:
            with self.assertRaises(RuntimeError):
                verify_backend(log, 'vulkan')
        verify_backend('whisper_backend_init_gpu: using Vulkan0 backend', 'vulkan')
        verify_backend('CPU inference', 'cpu')


if __name__ == '__main__':
    unittest.main()
