from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from math import sqrt
from statistics import mean, median
from typing import Any, Iterable

from .model import Observation


def _wilson95(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + (z * z) / total
    centre = p + (z * z) / (2 * total)
    margin = z * sqrt((p * (1 - p) + (z * z) / (4 * total)) / total)
    return ((centre - margin) / denominator, (centre + margin) / denominator)


def _task_set_sha256(task_ids: Iterable[str]) -> str:
    payload = "\n".join(sorted(set(task_ids))).encode("utf-8")
    return sha256(payload).hexdigest()


def summarize(observations: Iterable[Observation]) -> list[dict[str, Any]]:
    groups: dict[
        tuple[str, str | None, str, str | None, str, str | None, str],
        list[Observation],
    ] = defaultdict(list)
    for observation in observations:
        key = (
            observation.benchmark,
            observation.benchmark_version,
            observation.harness,
            observation.harness_version,
            observation.model,
            observation.model_version,
            observation.configuration_sha256,
        )
        groups[key].append(observation)

    rows: list[dict[str, Any]] = []
    for key in sorted(groups, key=lambda item: tuple(value or "" for value in item)):
        (
            benchmark,
            benchmark_version,
            harness,
            harness_version,
            model,
            model_version,
            configuration_sha256,
        ) = key
        items = groups[key]
        successes = sum(1 for item in items if item.success)
        low, high = _wilson95(successes, len(items))
        costs = [item.cost_usd for item in items if item.cost_usd is not None]
        latencies = [item.latency_ms for item in items if item.latency_ms is not None]
        input_tokens = [item.input_tokens for item in items if item.input_tokens is not None]
        output_tokens = [item.output_tokens for item in items if item.output_tokens is not None]

        rows.append(
            {
                "schema_version": "ahi.summary/v1",
                "benchmark": benchmark,
                "benchmark_version": benchmark_version,
                "harness": harness,
                "harness_version": harness_version,
                "model": model,
                "model_version": model_version,
                "configuration_sha256": configuration_sha256,
                "task_set_sha256": _task_set_sha256(item.task_id for item in items),
                "distinct_tasks": len({item.task_id for item in items}),
                "observations": len(items),
                "successes": successes,
                "success_rate": successes / len(items),
                "success_rate_wilson95": {"low": low, "high": high},
                "cost_usd": {
                    "observed": len(costs),
                    "mean": mean(costs) if costs else None,
                },
                "latency_ms": {
                    "observed": len(latencies),
                    "median": median(latencies) if latencies else None,
                },
                "input_tokens": {
                    "observed": len(input_tokens),
                    "mean": mean(input_tokens) if input_tokens else None,
                },
                "output_tokens": {
                    "observed": len(output_tokens),
                    "mean": mean(output_tokens) if output_tokens else None,
                },
            }
        )

    return rows
