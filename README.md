# Agent Harness Index

**Reproducible, longitudinal evidence for models × agent harnesses × orchestration configurations.**

AHI preserves the context that isolated leaderboard cells erase: benchmark/version, task/trial, model/version, harness/version, configuration, environment, cost, latency, tokens and provenance. Its catalog is a discovery layer, while normalized observations remain the only source of empirical claims.

> Status: early foundation. Observation normalization, dataset integrity, matched comparison, SkillBench interoperability, benchmark catalog discovery and evidence-coverage reporting are implemented.

## Evidence pipeline

```text
benchmark catalog metadata
        ↘
controlled run -> ahi.observation/v1 -> integrity -> comparable cells -> matched comparison
        ↗                                      ↓
SkillBench evidence                       evidence coverage
```

Task horizon is explicit catalog context (`short|medium|long|mixed|unknown`) because harness value can vary materially with horizon. Unknown horizon stays unknown; AHI does not infer it from benchmark names.

## CLI

```bash
ahi validate results.jsonl
ahi integrity results.jsonl
ahi summarize results.jsonl
ahi compare left.jsonl right.jsonl
ahi catalog-validate catalog.json
ahi catalog-query catalog.json --horizon long
ahi catalog-coverage catalog.json results.jsonl
```

Catalog metadata never becomes a benchmark score. Coverage distinguishes declared metrics/versions from evidence actually observed.

See `docs/METHODOLOGY.md`, `docs/BENCHMARK_CATALOG.md`, and `docs/LANDSCAPE.md`.
