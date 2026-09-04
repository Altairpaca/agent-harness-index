# Agent Harness Index

**Reproducible, longitudinal evidence for models × agent harnesses × orchestration configurations.**

Coding-agent results are usually published as isolated leaderboard cells. Agent Harness Index keeps the information needed to decide whether two cells are actually comparable: benchmark identity, task identity, trial, model, harness, versions, configuration, success, cost, latency, tokens and evidence provenance.

> Status: early v0.2 foundation. Observation normalization, dataset integrity checks, deterministic aggregation and matched cell comparison are implemented; real benchmark collection remains a separate evidence-ingestion step.

## Core model

```text
existing benchmark / controlled run
  -> ahi.observation/v1 JSONL
  -> row validation
  -> dataset integrity + content fingerprint
  -> aggregate comparable cells
  -> matched task/trial comparison
  -> reproducible evidence snapshot
```

## Quickstart

```bash
python -m pip install -e .
ahi validate results.jsonl
ahi integrity results.jsonl
ahi summarize results.jsonl
ahi compare left-cell.jsonl right-cell.jsonl
```

The core has no runtime dependencies and does not call model APIs.

## Dataset integrity

`ahi integrity` rejects duplicate `run_id` values and duplicate stochastic trial identities within the same benchmark/model/harness/configuration cell. It also emits an order-independent SHA-256 fingerprint for the normalized dataset contents.

## Matched comparison

`ahi compare` deliberately accepts one cell per side. The two sides must share benchmark identity/version; observations are paired on benchmark + task + trial. The report exposes matched and unmatched coverage, win/loss/tie counts, success-rate delta, and paired cost/latency/token deltas only where both sides actually observed the metric.

The comparison report is descriptive evidence, not a statistical-significance claim.

## Why this exists

GitTaskBench, BoundaryBench and other projects already provide valuable task suites and controlled studies. This project targets the missing **normalization and longitudinal evidence layer**, so benchmark results can be compared without erasing harness/configuration provenance.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md), [`docs/LANDSCAPE.md`](docs/LANDSCAPE.md), and [`docs/V0.2.md`](docs/V0.2.md).

## Intended downstream uses

- track harness regressions across versions;
- compare cost/success trade-offs on matched task sets;
- publish auditable benchmark snapshots;
- ingest SkillBench real-harness evidence;
- provide empirical task-conditioned evidence to DSHelm routing policies.

## Non-goals

This is not a universal model leaderboard, a benchmark scraper, or a new task suite. Missing metrics stay missing, and unmatched task sets should not be ranked as though they were controlled comparisons.

Apache-2.0 licensed.
