# Benchmark catalog and evidence discovery

## Motivation

AHI validates and compares evidence after observations exist. Discovery previously remained manual: contributors had to know which benchmark, task family and metrics were already represented, and catalog metadata could easily be mistaken for measured support.

The catalog layer adds metadata discovery while the coverage layer answers a separate question: **what evidence do we actually have?**

## Catalog entities

An `ahi.catalog/v1` entry may describe:

- benchmark identity and versions;
- task families;
- explicit task horizon (`short`, `medium`, `long`, `mixed`, `unknown`);
- evaluation dimensions the benchmark can expose;
- source/documentation URL;
- evidence policy and notes.

Horizon is descriptive context for interpreting harness evidence. Unknown stays `unknown`; AHI does not infer horizon from benchmark names or marketing copy.

Catalog metadata is descriptive. Listing `cost_usd` means the benchmark can represent that metric; it does not mean AHI has observed cost evidence.

## Evidence coverage

`ahi catalog-coverage <catalog.json> <observations.jsonl>` joins catalog entries against normalized observations and reports:

- observation count;
- model and harness identities seen;
- metrics actually observed;
- declared metrics that still have no evidence;
- evidence-URI coverage;
- declared benchmark versions with and without observations;
- unversioned observations;
- observations whose benchmark is not cataloged.

This is intentionally not a ranking surface. Zero coverage means unknown, not poor performance.

## CLI

```bash
ahi catalog-validate catalog.json
ahi catalog-query catalog.json --metric cost_usd
ahi catalog-query catalog.json --task-family software-engineering
ahi catalog-query catalog.json --horizon long
ahi catalog-coverage catalog.json results.jsonl
```

## Evidence boundary

Every capability/performance claim must still come from:

- normalized observations;
- reproducible configuration identity;
- environment provenance;
- explicit evidence snapshots;
- matched comparisons where comparative language is used.

Catalog and coverage outputs must not convert vendor/model descriptions into scores. This keeps AHI distinct from a universal leaderboard or literature-only benchmark index.
