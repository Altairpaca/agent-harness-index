# Golden interoperability handoff

AHI keeps a pinned copy of the SkillBench portable-observation fixture and a golden `ahi.summary/v1` output generated through the real normalization and aggregation path.

```text
skillbench.harness-observation/v1
  -> normalize_skillbench_observation
  -> ahi.observation/v1
  -> summarize
  -> ahi.summary/v1 (golden)
```

The golden contract locks the semantics that matter to downstream routing evidence:

- benchmark, model and harness identity/version;
- exact skill-source provenance through the configuration fingerprint;
- execution environment fingerprint;
- task-set fingerprint;
- pass/fail aggregation;
- Wilson interval;
- cost, latency and token telemetry.

The fixture is intentionally copied and pinned rather than fetched from SkillBench during CI. Cross-repository drift therefore requires an explicit reviewed fixture update instead of making historical AHI semantics depend on the current state of another repository.

This contract remains synthetic. It proves schema handoff and deterministic aggregation only; it is not evidence that a real model/harness run occurred.
