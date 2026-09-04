# Methodology

Agent Harness Index is an observation and aggregation layer, not a task benchmark. It is designed to ingest evidence produced by existing benchmarks and controlled internal runs without erasing the configuration that made a result possible.

## Unit of evidence

One JSONL row is one trial of one task under one model/harness/configuration cell.

Required identity fields are:

- `run_id`
- `task_id`
- `trial`
- `model`
- `harness`
- `success`
- `schema_version`

Versions, cost, latency, token counts, environment, configuration and evidence URI should be recorded whenever the runner can observe them.

## Comparability rules

A public comparison should not rank two rows merely because both report a success rate.

At minimum, comparable cells should share:

1. the same task-set fingerprint;
2. compatible success criteria;
3. pinned or explicitly recorded harness versions;
4. pinned or explicitly recorded model identity/version where available;
5. equivalent reasoning/effort and tool policy, represented in `configuration`;
6. enough repeated trials to expose stochastic variance.

`task_set_sha256` and `configuration_sha256` exist to make accidental apples-to-oranges aggregation visible.

## Missing metrics

Missing cost, latency or token data is **missing**, not zero. Summaries therefore report the number of observations contributing to each metric.

## Statistical reporting

The v0.1 summary reports raw counts, success rate and a 95% Wilson interval. It does not imply statistical significance between cells. Later comparison layers may add paired tests where the underlying design supports them.

## Provenance

Raw run artifacts should remain addressable through `evidence_uri`. Aggregated data should be reproducible from immutable or content-addressed raw observations. The index should prefer append-only snapshots over silently rewriting historical results when harnesses or models change.

## Relationship to DSHelm

The index may later export evidence suitable for DSHelm routing policies. Routing should consume observed, task-conditioned performance rather than treating a leaderboard rank as universal model quality.
