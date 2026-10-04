import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import whisper_worker as worker


class WhisperWorkerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.audio = self.root / 'audio.wav'
        with wave.open(str(self.audio), 'wb') as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(16000); wav.writeframes(b'\0'*32000)

    def test_conversion_preserves_source_clocks_streams_and_questionable_bounds(self):
        raw = {'segments':[{'start':.25,'end':1.8,'text':' A quiet setup.'}]}
        self.assertEqual(worker.convert_response(raw, 100, 2),[
            {'start':100.25,'end':101.8,'text':' A quiet setup.','audio_stream':2}])
        self.assertEqual(worker.convert_response({'segments':[]}, 100, 2),[])
        for bad in [{'text':'no timestamps'},{'segments':[{'start':float('nan'),'end':1,'text':'bad'}]}]:
            with self.assertRaises(ValueError): worker.convert_response(bad,0,1)

    def test_request_parameters_do_not_enable_context_or_change_cli_decoding(self):
        body, content_type = worker.multipart(self.audio, 'en')
        self.assertIn(b'name="beam_size"\r\n\r\n5', body)
        self.assertIn(b'name="best_of"\r\n\r\n5', body)
        self.assertIn(b'name="token_timestamps"\r\n\r\nfalse', body)
        self.assertIn(b'name="prompt"\r\n\r\n\r\n', body)
        self.assertIn(b'name="vad"\r\n\r\nfalse', body)
        self.assertTrue(content_type.startswith('multipart/form-data; boundary='))

    def test_incompatible_audio_and_runtime_are_rejected(self):
        with wave.open(str(self.audio), 'wb') as wav:
            wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(16000); wav.writeframes(b'\0'*64000)
        with self.assertRaisesRegex(ValueError,'mono 16 kHz'): worker.multipart(self.audio,'en')
        exe=self.root/'whisper-server.exe';exe.write_bytes(b'fake')
        with self.assertRaisesRegex(ValueError,'same runtime DLLs'):
            worker.worker_identity({'dll_sha256':{'missing.dll':'x'}}, exe)

    def test_worker_stays_lazy_when_nothing_needs_transcribing(self):
        with patch.object(worker.subprocess,'Popen') as launch:
            with worker.WhisperWorker({},self.root/'workers'): pass
            launch.assert_not_called()
            self.assertFalse((self.root/'workers').exists())

    def test_worker_process_is_closed_on_completion_and_exception(self):
        for fail in (False,True):
            instance=worker.WhisperWorker({},self.root)
            proc=Mock();proc.poll.return_value=None;instance.proc=proc
            try:
                with instance:
                    if fail: raise RuntimeError('fixture interruption')
            except RuntimeError: pass
            proc.terminate.assert_called_once();proc.wait.assert_called_once()

    def test_worker_kills_unresponsive_owned_process(self):
        instance=worker.WhisperWorker({},self.root)
        proc=Mock();proc.poll.return_value=None;proc.wait.side_effect=[subprocess.TimeoutExpired('fake',10),0]
        instance.proc=proc;instance.close();proc.kill.assert_called_once()

    def ready_worker(self):
        instance=worker.WhisperWorker({'device':'vulkan'},self.root)
        instance.start=lambda:None;instance.port=1;instance.route='/private';instance.log_path=self.root/'server.log'
        return instance

    def test_failed_request_closes_worker_and_never_publishes_success(self):
        instance=self.ready_worker();proc=Mock();proc.poll.return_value=None;instance.proc=proc
        conn=Mock();conn.getresponse.return_value=SimpleNamespace(status=500,read=lambda:b'{"error":"fixture"}')
        with patch.object(worker.http.client,'HTTPConnection',return_value=conn):
            with self.assertRaisesRegex(RuntimeError,'500'):
                instance.transcribe(self.audio,self.root/'failed',0,1,'en')
        self.assertTrue(instance.failed);proc.terminate.assert_called_once();conn.close.assert_called_once()
        self.assertFalse((self.root/'failed-run.json').exists())
        self.assertTrue((self.root/'failed-server.json').exists())

    def test_success_preserves_raw_and_canonical_evidence_without_overwriting(self):
        instance=self.ready_worker()
        payload={'language':'english','segments':[{'start':.2,'end':.8,'text':' Hello'}]}
        conn=Mock();conn.getresponse.return_value=SimpleNamespace(status=200,read=lambda:json.dumps(payload).encode())
        with patch.object(worker.http.client,'HTTPConnection',return_value=conn):
            result=instance.transcribe(self.audio,self.root/'ok',90,2,'en')
            self.assertEqual(result[0]['start'],90.2)
            self.assertEqual(json.loads((self.root/'ok-server.json').read_text()),payload)
            before=(self.root/'ok.json').read_bytes()
            with self.assertRaises(ValueError):instance.transcribe(self.audio,self.root/'ok',90,2,'en')
            self.assertEqual((self.root/'ok.json').read_bytes(),before)


if __name__=='__main__': unittest.main()
