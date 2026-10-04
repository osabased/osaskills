"""Synthetic software fixtures only; these do not measure real discovery quality."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import benchmark


def fixture():
    events = {'sources': [{'id': 'a', 'path': 'D:/VODs/a.mp4', 'duration_sec': 100},
                          {'id': 'b', 'path': 'D:/VODs/b.mp4', 'duration_sec': 110}],
              'events': [{'id': 'first', 'title': 'Quiet setup', 'perspectives': [
                  {'source_id': 'a', 'start_sec': 10, 'end_sec': 15, 'evidence': 'Reviewed frames'},
                  {'source_id': 'b', 'start_sec': 30, 'end_sec': 35, 'evidence': 'Reviewed dialogue'}]},
                  {'id': 'second', 'title': 'Repeated attempt', 'perspectives': [
                      {'source_id': 'a', 'start_sec': 20, 'end_sec': 25, 'evidence': 'Continuous reviewed interval'}]}]}
    reference = benchmark.scaffold_reference(events, 'Synthetic reference')
    reference.update(reviewed_by='Fixture', reviewed_at='2026-10-04')
    for coverage in reference['coverage']:
        coverage.update(reviewed=True, evidence='Synthetic reviewed range')
    for moment in reference['moments']:
        moment['reviewed'] = True
    reference['moments'][0]['tags'] = ['quiet-setup']
    reference['moments'][1]['tags'] = ['repeated-attempt']
    return reference, events


def judge(reference, events):
    result = benchmark.scaffold_adjudication(reference, events)
    for item in result['observations']:
        item.update(verdict='match', moment_id=item['candidate_event_id'], note='Synthetic identity inspected')
    for item in result['pov_links']:
        item.update(verdict='correct', note='Synthetic paired views inspected')
    return result


class BenchmarkTests(unittest.TestCase):
    def test_reference_scaffold_requires_actual_review(self):
        _, events = fixture()
        scaffold = benchmark.scaffold_reference(events, 'Pending review')
        self.assertFalse(scaffold['exhaustive'])
        self.assertFalse(scaffold['coverage'][0]['reviewed'])
        self.assertFalse(scaffold['moments'][0]['reviewed'])
        with self.assertRaisesRegex(ValueError, 'reviewed_by'):
            benchmark.scaffold_adjudication(scaffold, events)
        reference, events = fixture()
        reference['exhaustive'] = True
        with self.assertRaisesRegex(ValueError, 'exhaustive'):
            benchmark.reference_data(reference)

    def test_matching_fixture_and_absent_performance(self):
        reference, events = fixture()
        report = benchmark.score(reference, events, judge(reference, events))
        self.assertEqual(report['quality']['known_moments_missed'], 0)
        self.assertEqual(report['quality']['known_moment_recall'], 1)
        self.assertEqual(report['quality']['incorrect_pov_associations'], 0)
        self.assertEqual(report['quality']['duplicate_observations'], 0)
        self.assertIsNone(report['performance'])
        self.assertFalse(report['reference']['exhaustive'])

    def test_miss_and_duplicate_keep_repeated_attempts_distinct(self):
        reference, events = fixture()
        events['events'] = [events['events'][0], copy.deepcopy(events['events'][0])]
        events['events'][1]['id'] = 'duplicate'
        judgments = judge(reference, events)
        for item in judgments['observations']:
            item['moment_id'] = 'first'
        report = benchmark.score(reference, events, judgments)
        self.assertEqual(report['quality']['known_moments_missed'], 1)
        self.assertEqual(report['unmatched_reference_moments'], ['second'])
        self.assertEqual(report['quality']['duplicate_observations'], 2)
        self.assertEqual(len(report['duplicates']), 2)
        # One observation per different POV is useful coverage, not a duplicate.
        events['events'][1]['perspectives'] = [events['events'][1]['perspectives'][1]]
        events['events'][0]['perspectives'] = [events['events'][0]['perspectives'][0]]
        judgments = judge(reference, events)
        for item in judgments['observations']:
            item['moment_id'] = 'first'
        self.assertEqual(benchmark.score(reference, events, judgments)['quality']['duplicate_observations'], 0)

    def test_pending_judgments_are_not_correct_incorrect_or_known_misses(self):
        reference, events = fixture()
        judgments = benchmark.scaffold_adjudication(reference, events)
        report = benchmark.score(reference, events, judgments)
        quality = report['quality']
        self.assertEqual(quality['known_moments_matched'], 0)
        self.assertIsNone(quality['known_moments_missed'])
        self.assertIsNone(quality['known_moment_recall'])
        self.assertEqual(quality['pending_observations'], 3)
        self.assertEqual(quality['pending_pov_associations'], 1)
        self.assertEqual(quality['correct_pov_associations'], 0)
        self.assertEqual(quality['incorrect_pov_associations'], 0)
        self.assertIsNone(report['unmatched_reference_moments'])
        self.assertIsNone(report['unmatched_reference_perspectives'])
        # Partial positive judgments still cannot turn outstanding entries into misses.
        judgments['observations'][0].update(verdict='match', moment_id='first', note='Inspected fixture')
        partial = benchmark.score(reference, events, judgments)
        self.assertEqual(partial['quality']['known_moments_matched'], 1)
        self.assertIsNone(partial['quality']['known_moments_missed'])
        self.assertIsNone(partial['unmatched_reference_moments'])

    def test_correct_link_cannot_connect_different_matched_moments(self):
        reference, events = fixture()
        # The negative example is a second, independently reviewed B event
        # at the same broad review interval; semantic identity requires judgment.
        reference['moments'][1]['perspectives'].append(copy.deepcopy(reference['moments'][0]['perspectives'][1]))
        judgments = judge(reference, events)
        judgments['observations'][1]['moment_id'] = 'second'
        with self.assertRaisesRegex(ValueError, 'contradicts'):
            benchmark.score(reference, events, judgments)
        judgments['pov_links'][0].update(verdict='incorrect', note='The paired views are independent events')
        self.assertEqual(benchmark.score(reference, events, judgments)['quality']['incorrect_pov_associations'], 1)

    def test_incorrect_pov_is_explicit_and_related_event_not_scored(self):
        reference, events = fixture()
        events['events'][0]['related_events'] = [{'event_id': 'second', 'source_id': 'a', 'relationship': 'later'}]
        judgments = judge(reference, events)
        judgments['pov_links'][0].update(verdict='incorrect', note='View B has similar scenery but is another occurrence')
        report = benchmark.score(reference, events, judgments)
        self.assertEqual(report['quality']['incorrect_pov_associations'], 1)
        self.assertEqual(len(report['incorrect_pov_links']), 1)
        self.assertEqual(len(judgments['pov_links']), 1)

    def test_no_automatic_matches_and_missing_judgment_rejected(self):
        reference, events = fixture()
        judgments = benchmark.scaffold_adjudication(reference, events)
        # Even byte-identical events are pending until an actual authored decision.
        self.assertTrue(all(item['verdict'] == 'pending' for item in judgments['observations']))
        judgments['observations'].pop()
        with self.assertRaisesRegex(ValueError, 'Missing observation'):
            benchmark.score(reference, events, judgments)
        judgments = judge(reference, events)
        judgments['observations'][0]['moment_id'] = 'second'
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            benchmark.score(reference, events, judgments)

    def test_changed_artifacts_and_media_identity_rejected(self):
        reference, events = fixture()
        judgments = judge(reference, events)
        for artifact in ('reference', 'events'):
            ref, run = copy.deepcopy(reference), copy.deepcopy(events)
            (ref if artifact == 'reference' else run)['changed'] = True
            with self.subTest(artifact=artifact), self.assertRaisesRegex(ValueError, 'stale'):
                benchmark.score(ref, run, judgments)
        for field, value in [('path', 'D:/VODs/replaced.mp4'), ('duration_sec', 101), ('id', 'new-id')]:
            modified = copy.deepcopy(events)
            modified['sources'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                benchmark.scaffold_adjudication(reference, modified)
        events['sources'][0]['path'] = 'd:\\vods\\A.MP4'
        self.assertEqual(len(benchmark.scaffold_adjudication(reference, events)['observations']), 3)

    def test_reviewed_coverage_limits_scoring(self):
        reference, events = fixture()
        reference['coverage'][0].update(start_sec=10, end_sec=25)
        extra = copy.deepcopy(events['events'][1])
        extra['id'] = 'outside'
        extra['perspectives'][0].update(start_sec=30, end_sec=35)
        events['events'].append(extra)
        judgments = judge(reference, events)
        report = benchmark.score(reference, events, judgments)
        self.assertEqual(len(report['excluded_observations']), 1)
        self.assertEqual(report['quality']['known_moments_missed'], 0)
        reference['coverage'][0]['end_sec'] = 24
        with self.assertRaisesRegex(ValueError, 'outside reviewed coverage'):
            benchmark.reference_data(reference)
        reference, _ = fixture()
        reference['coverage'][0]['reviewed'] = False
        with self.assertRaisesRegex(ValueError, 'coverage must be reviewed'):
            benchmark.reference_data(reference)

    def test_storage_excludes_sources_counts_roots_once_and_preserves_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / 'source.mp4'
            original.write_bytes(b'original-media')
            artifacts = root / 'prepared'
            artifacts.mkdir()
            evidence = artifacts / 'frame.jpg'
            evidence.write_bytes(b'frame-fixture')
            reference, events = fixture()
            events['sources'][0]['path'] = str(original)
            reference['sources'][0]['path'] = str(original)
            snapshot = {p: p.read_bytes() for p in (original, evidence)}
            record = benchmark.record_run(events, 'cache retry', 3.5, [root, artifacts])
            self.assertEqual(record['output_storage_bytes'], len(b'frame-fixture'))
            self.assertEqual(record['output_files'], 1)
            self.assertEqual(record['excluded_source_files'], [str(original.resolve())])
            report = benchmark.score(reference, events, judge(reference, events), record)
            self.assertEqual(report['performance']['elapsed_wall_sec'], 3.5)
            for path, content in snapshot.items():
                self.assertEqual(path.read_bytes(), content)
            record['events_sha256'] = 'stale'
            with self.assertRaisesRegex(ValueError, 'Run measurements are stale'):
                benchmark.score(reference, events, judge(reference, events), record)
            for value in (-1, float('nan'), True):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    benchmark.record_run(events, 'bad', value, [artifacts])

    def test_partial_coverage_candidate_cannot_create_confirmed_miss(self):
        reference, events = fixture()
        reference['coverage'] = [{'source_id': 'a', 'start_sec': 0, 'end_sec': 10,
                                 'reviewed': True, 'evidence': 'Reviewed bounded range'}]
        reference['moments'] = [reference['moments'][0]]
        reference['moments'][0]['perspectives'] = [reference['moments'][0]['perspectives'][0]]
        reference['moments'][0]['perspectives'][0].update(start_sec=6, end_sec=8)
        events['events'] = [events['events'][0]]
        events['events'][0]['perspectives'] = [events['events'][0]['perspectives'][0]]
        events['events'][0]['perspectives'][0].update(start_sec=5, end_sec=25)
        scaffold = benchmark.scaffold_adjudication(reference, events)
        report = benchmark.score(reference, events, scaffold)
        self.assertTrue(report['quality']['observation_judgments_complete'])
        self.assertFalse(report['quality']['miss_scoring_complete'])
        self.assertEqual(report['quality']['partial_coverage_observations'], 1)
        self.assertIsNone(report['quality']['known_moments_missed'])
        self.assertIsNone(report['quality']['known_moment_recall'])
        self.assertIsNone(report['unmatched_reference_moments'])
        self.assertTrue(report['excluded_observations'][0]['partially_reviewed'])
        events['events'][0]['perspectives'][0].update(start_sec=20, end_sec=25)
        report = benchmark.score(reference, events, benchmark.scaffold_adjudication(reference, events))
        self.assertTrue(report['quality']['miss_scoring_complete'])
        self.assertEqual(report['quality']['known_moments_missed'], 1)

    def test_cli_records_and_scores_without_overwriting_authored_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            reference, events = fixture()
            judgments = judge(reference, events)
            for name, value in [('reference', reference), ('events', events), ('judgments', judgments)]:
                (root / (name + '.json')).write_text(json.dumps(value), encoding='utf-8')
            command = [sys.executable, '-B', str(Path(benchmark.__file__)), 'score',
                       '--reference', str(root / 'reference.json'), '--events', str(root / 'events.json'),
                       '--adjudication', str(root / 'judgments.json'), '--out', str(root / 'report.json')]
            completed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = (root / 'report.json').read_bytes()
            completed = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn('already exists', completed.stderr)
            self.assertEqual((root / 'report.json').read_bytes(), report)


if __name__ == '__main__':
    unittest.main()
