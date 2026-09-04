# Contributing to Agent Harness Index

Agent Harness Index is an evidence-normalization layer. Contributions should make benchmark observations more comparable without erasing the conditions under which they were produced.

## Core contribution rules

For schema, validation, aggregation or comparison changes:

- add deterministic tests that run in GitHub Actions;
- state the comparability invariant being changed;
- preserve missing telemetry as missing rather than coercing it to zero;
- do not merge benchmark, model, harness, configuration or environment identities merely to simplify a leaderboard;
- document schema compatibility when changing an emitted contract.

## Observation/data contributions

Real datasets must identify, when observable:

- benchmark and benchmark version;
- task and trial identity;
- model and model version;
- harness and harness version;
- configuration and environment;
- success criterion;
- evidence provenance;
- cost/latency/token telemetry source semantics.

Do not infer unavailable telemetry. Do not silently substitute fallback models or harnesses.

## Pull request contract

A PR should state:

1. **Problem** — which ambiguity or comparability failure is being addressed?
2. **Scope / non-goals** — what is deliberately excluded?
3. **Acceptance** — which deterministic tests prove the new invariant?
4. **Evidence** — which fixture, source SHA or real run supports the change?
5. **Interpretation** — what conclusions the resulting data does and does not justify?

## Statistical claims

Current comparison output is descriptive. Do not present a success delta, win count or paired metric delta as statistically significant unless an explicit statistical method and suitable experimental design are added and reviewed.

## Product boundaries

This project is not a new universal task benchmark or a scraper that flattens unrelated leaderboard cells. Benchmark-specific runners should normally remain upstream or in integrations; AHI should normalize their evidence.

## Sensitive data

Never commit credentials, account identifiers, private billing payloads or proprietary benchmark inputs without the right to redistribute them. Sanitized telemetry fixtures should retain only semantics needed by the normalizer.

Apache-2.0 applies to contributions unless explicitly stated otherwise.
