# Benchmark catalog foundation

## Motivation

AHI currently validates and compares evidence after observations exist. Discovery remains manual: contributors need to know which benchmark, harness and capability dimensions are already represented.

The catalog layer adds metadata discovery without changing evidence semantics.

## Catalog entities

A catalog entry may describe:

- benchmark identity and versions;
- task family;
- supported evaluation dimensions;
- expected observation fields;
- primary documentation links;
- evidence status.

## Evidence boundary

Catalog metadata is descriptive. It does not create benchmark results.

Every capability claim must still come from:

- normalized observations;
- reproducible configuration identity;
- environment provenance;
- explicit evidence snapshots.

## Future schema direction

```text
benchmark
  -> task families
  -> expected metrics
  -> compatible observation schema
  -> evidence snapshots
```

The catalog should remain independent from any model vendor, harness vendor or ranking policy.
