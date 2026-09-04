from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Any, Iterable

from .model import Observation

DATASET_SCHEMA_VERSION = "ahi.dataset/v1"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def observation_identity(observation: Observation) -> tuple[object, ...]:
    """Identity of one stochastic trial inside a comparable benchmark cell."""
    return (
        observation.benchmark,
        observation.benchmark_version,
        observation.task_id,
        observation.trial,
        observation.model,
        observation.model_version,
        observation.harness,
        observation.harness_version,
        observation.configuration_sha256,
        observation.environment_sha256,
    )


def dataset_fingerprint(observations: Iterable[Observation]) -> str:
    rows = [asdict(observation) for observation in observations]
    canonical_rows = sorted(_canonical_json(row) for row in rows)
    payload = "\n".join(canonical_rows).encode("utf-8")
    return sha256(payload).hexdigest()


def inspect_dataset(observations: Iterable[Observation]) -> dict[str, Any]:
    items = list(observations)
    if not items:
        raise ValueError("dataset contains no observations")

    seen: dict[tuple[object, ...], str] = {}
    errors: list[str] = []
    run_ids: set[str] = set()

    for item in items:
        identity = observation_identity(item)
        existing = seen.get(identity)
        if existing is not None:
            errors.append(
                "duplicate trial identity: "
                f"benchmark={item.benchmark!r} task={item.task_id!r} trial={item.trial} "
                f"model={item.model!r} harness={item.harness!r}; run_ids={existing!r},{item.run_id!r}"
            )
        else:
            seen[identity] = item.run_id

        if item.run_id in run_ids:
            errors.append(f"duplicate run_id: {item.run_id}")
        run_ids.add(item.run_id)

    return {
        "schema_version": DATASET_SCHEMA_VERSION,
        "valid": not errors,
        "observations": len(items),
        "distinct_runs": len(run_ids),
        "benchmarks": sorted({item.benchmark for item in items}),
        "dataset_sha256": dataset_fingerprint(items),
        "errors": sorted(set(errors)),
    }
