# Bounded discovery benchmark

Use `scripts/benchmark.py` when comparing discovery changes. It scores authored judgments against a reviewed reference and records measured wall time and output storage. It does not recognize events, judge footage, or infer same-event links from overlapping ranges or similar text. No additional dependencies or models are required.

## Author a reference

Choose bounded source ranges and review them for known moments. Include important actions, quiet setup, separate repeated attempts, and similar-looking POVs that depict different events where those cases actually exist. Give each repeat its own moment ID. Optional `tags` such as `important`, `quiet-setup`, `repeated-attempt` and `misleading-POV` produce separate counts in the report.

An existing authored events file can seed a **pending scaffold**:

```powershell
python <skill>/scripts/benchmark.py reference --events work/bench/reviewed-events.json --name "Bounded discovery trial" --out work/bench/reference.json
```

Edit the resulting reference after review:

- Fill `reviewed_by` and `reviewed_at` with the reviewer identity and review date.
- Replace the default full-source `coverage` rows with the actual inspected source-local intervals. Each needs `reviewed: true` and an `evidence` description recording how it was reviewed. Adjacent or overlapping reviewed intervals can jointly cover a moment.
- Inspect the copied `moments`, their source-local perspectives and evidence. Remove unsupported entries, add known moments absent from the seed, set `reviewed: true`, and add useful tags. A moment must fit within reviewed coverage on each listed source.
- Set `review_basis` to `supplied-evidence` for sampled images/transcripts, or `continuous-video` for continuous footage review. `exhaustive: true` is rejected for sampled evidence; it should remain false unless the bounded continuous review supports that assertion. An empty moments list is valid for an explicitly reviewed negative-control range.

The reference schema is `vod-discovery-benchmark/v1`. Its `sources` use the same `id`, media `path`, and `duration_sec` as events.json. Each moment has an `id`, `reviewed`, optional `title`/`tags`, and `perspectives` with `source_id`, `start_sec`, `end_sec` and `evidence`. Source IDs, paths and durations must agree between reference and run. Keep the same original media and source clocks; this metadata check does not hash entire media files.

Previously reviewed project footage can support an explicitly labelled regression reference for preserving its already observed moments. A sampled review is not independent or exhaustive ground truth. Comparing an event file to itself does not measure a new run's discovery quality. No real project reference or discovery recall claim is bundled with this harness; tests use synthetic software fixtures. Choose and review reference footage for the current project.

## Judge a discovery run

Save the run's suggestions using the existing events.json format, then create a fresh judgment file:

```powershell
python <skill>/scripts/benchmark.py adjudication --reference work/bench/reference.json --events work/bench/run-events.json --out work/bench/run-judgments.json
```

The `vod-discovery-adjudication/v1` scaffold contains one observation for each candidate event/source perspective fully inside reference coverage, plus one POV-link judgment for each pair of those perspectives within an event. Perspectives outside coverage remain explicitly excluded from scoring. If a candidate only partly overlaps reviewed coverage, missed-moment scoring remains incomplete: narrow its candidate range or review the additional range and update the reference before judging it. Completely outside candidates do not block the bounded score. `related_events` are earlier/later/context links, not simultaneous POV claims, and are not scored as POV links.

Review each observation against the footage/reference. Set its `verdict` to `match`, `unmatched` or `pending`. A `match` needs the reference `moment_id` and an evidence `note`; an `unmatched` observation needs a note and a null `moment_id`. Leave anything unjudged `pending`. A proposed match must use that moment's source and overlap its source-local interval, but overlap itself never creates a match. Broad handles, repeated dialogue and similar scenery require an actual identity judgment.

Judge each `pov_links` row separately as `correct`, `incorrect` or `pending`, with a local-evidence note for a judged link. This tests the claimed correspondence, including misleading timing or coverage, separately from merely recognizing moments. A `correct` same-event link is rejected when its observations are explicitly mapped to different reference moments.

The judgment file is bound to the canonical reference and candidate JSON hashes. Editing either invalidates old judgments; generate and review a new scaffold. Do not carry mappings over silently. Scripts refuse to overwrite an existing output file, preserving authored references, judgments and prior reports.

## Record processing and storage

Time the actual work being compared with a stopwatch. Use consistent sources, models, packet settings and timing boundaries, and label cold preparation, cached reruns and failed-stage retries separately. Keep previous outputs so the cache trial measures reuse rather than a fresh folder. Record whether a model was already loaded and what failed in the run notes/label. Compare multiple trials when speed is the question; a single synthetic test establishes behavior, not machine-wide throughput.

For example, stop the timer immediately after the preparation command; the following storage scan is outside that timed boundary:

```powershell
$discoveryTimer = [Diagnostics.Stopwatch]::StartNew()
python <skill>/scripts/vod.py prepare --source "D:/VODs/alice.mp4" --out work/bench/prepared
$discoveryTimer.Stop()
python <skill>/scripts/benchmark.py record --events work/bench/run-events.json --label "Preparation only, cold trial 1" --wall-seconds $discoveryTimer.Elapsed.TotalSeconds --artifacts work/bench/prepared --out work/bench/run-cost.json
```

The `vod-discovery-benchmark-run/v1` record contains externally measured `elapsed_wall_sec`, enumerated `output_storage_bytes`, output-file count, roots, excluded source media and skipped links. Supply the relevant prepared/cache/output directories with `--artifacts`; overlapping roots count each physical path once. Source paths listed in events.json are excluded, and symlinks/junctions are skipped. Artifact roots themselves cannot be symlinks/junctions. Keep benchmark reference/judgment/report files outside these roots so they do not inflate pipeline storage. Source media and original evidence are read only.

The timer can cover preparation or the whole discovery workflow, provided the label states that scope. An externally measured preparation time excludes subsequent chat review, annotation and search unless those were inside the measured interval. An absent run-cost file produces `performance: null`, not a fabricated zero. A cost record must be bound to the same candidate event file as the score.

## Score and interpret

```powershell
python <skill>/scripts/benchmark.py score --reference work/bench/reference.json --events work/bench/run-events.json --adjudication work/bench/run-judgments.json --run work/bench/run-cost.json --out work/bench/run-report.json
```

The report includes:

- Known moments matched and missed, reference-relative recall, and known source perspectives missed. A moment is found when at least one of its perspectives has a judged match. Separate POV coverage remains visible. Counts by optional tags show, for example, whether quiet setup regressed.
- Explicitly judged incorrect and correct POV associations, plus pending links. Pending links are counted as neither correct nor incorrect.
- Duplicate observations: extra candidate event IDs matched to the same reference moment **and source**. Useful distinct POV coverage and separately annotated repeated attempts are not duplicates.
- Unmatched candidate observations, pending observations, excluded ranges, exact judgment details, and the supplied wall-time/storage record.

If any in-scope observation is pending, or a candidate partly overlaps reviewed coverage, missed-moment counts, missed-perspective counts, recall and unmatched-reference lists are null. Positive judged matches and duplicate counts are available as partial results; `miss_scoring_complete` records whether misses can be reported. Finish judgment and resolve partial coverage before reporting discovery misses. A nonempty list of unmatched candidates does not automatically mean those suggestions are wrong or worthless: the reference may be incomplete, especially after sampled review.

This measures performance against the specified reviewed set. It cannot establish that unprepared/unreviewed footage has no important moments, validate hours of drifting POVs from a five-minute trial, or turn retrieval similarity into alignment confidence. Preparation-cache experiments can confirm preserved artifacts and reduced repeated work without claiming new discovery quality until a reviewed run has been scored.
