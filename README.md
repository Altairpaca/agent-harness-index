# Agent Harness Index

**Reproducible, longitudinal evidence for models × agent harnesses × orchestration configurations.**

Coding-agent results are usually published as isolated leaderboard cells. Agent Harness Index keeps the information needed to decide whether two cells are actually comparable: task identity, trial, model, harness, versions, configuration, success, cost, latency, tokens and evidence provenance.

> Status: early foundation. v0.1 defines a normalized observation contract and deterministic aggregation kernel; real benchmark ingestion follows next.

## Core model

```text
existing benchmark / controlled run
  -> ahi.observation/v1 JSONL
  -> validate
  -> group by model + harness + version + config
  -> task-set fingerprint
  -> success rate + Wilson interval + cost/latency coverage
  -> reproducible snapshot
```

## Quickstart

```bash
python -m pip install -e .
ahi validate results.jsonl
ahi summarize results.jsonl
```

The core has no runtime dependencies and does not call model APIs.

## Why this exists

GitTaskBench, BoundaryBench and other projects already provide valuable task suites and controlled studies. This project targets the missing **normalization and longitudinal evidence layer**, so benchmark results can be compared without erasing harness/configuration provenance.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for comparability rules and [`docs/LANDSCAPE.md`](docs/LANDSCAPE.md) for the product boundary.

## Intended downstream uses

- track harness regressions across versions;
- compare cost/success trade-offs on matched task sets;
- publish auditable benchmark snapshots;
- ingest SkillBench real-harness evidence;
- provide empirical task-conditioned evidence to DSHelm routing policies.

## Non-goals

This is not a universal model leaderboard, a benchmark scraper, or a new task suite. Missing metrics stay missing, and unmatched task sets should not be ranked as though they were controlled comparisons.

Apache-2.0 licensed.
