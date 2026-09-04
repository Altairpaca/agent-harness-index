# Landscape and product boundary

Snapshot: 2026-09-04.

Agent Harness Index does not compete by inventing another benchmark task suite.

## Relevant projects

- [`QuantaAlpha/GitTaskBench`](https://github.com/QuantaAlpha/GitTaskBench) evaluates repo-level agents on 54 practical tasks and exposes completion/pass metrics plus cost-aware evaluation.
- [`boundary-bench/boundary-bench`](https://github.com/boundary-bench/boundary-bench) evaluates coding-agent harnesses under hardened sandbox policies and reports model/harness success and cost under controlled restrictions.
- [`tdrml/harness-bench`](https://github.com/tdrml/harness-bench) studies the marginal value of harness engineering and demonstrates why benchmark horizon and task design matter when interpreting harness ROI.

These projects provide evidence sources and methodological lessons rather than problems to reimplement.

## Gap targeted here

Results from different harness studies are difficult to reuse because the observation schemas, version metadata, cost semantics, configuration details and task-set identities differ.

Agent Harness Index targets the longitudinal evidence layer:

```text
benchmark/task runner
    -> normalized trial observation
    -> immutable raw evidence
    -> configuration + task-set fingerprints
    -> statistically honest summaries
    -> public snapshots / downstream routing evidence
```

The repository should make it easy to answer questions such as:

- Did a harness upgrade improve success on the *same* task set?
- Did the gain survive repeated trials?
- What happened to cost and latency coverage?
- Is a model comparison actually using the same harness configuration?
- Which observations are strong enough to inform a DSHelm routing policy?

## Non-goals

- universal model ranking;
- benchmark score scraping without provenance;
- hiding model/harness coupling behind one headline number;
- treating missing cost as zero;
- claiming causal harness improvements from unmatched task sets.
