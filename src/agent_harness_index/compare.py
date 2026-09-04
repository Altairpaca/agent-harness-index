from __future__ import annotations

from hashlib import sha256
from statistics import mean
from typing import Any, Iterable

from .model import Observation

COMPARISON_SCHEMA_VERSION = "ahi.comparison/v1"


def _cell_signature(item: Observation) -> tuple[object, ...]:
    return (
        item.benchmark,
        item.benchmark_version,
        item.model,
        item.model_version,
        item.harness,
        item.harness_version,
        item.configuration_sha256,
        item.environment_sha256,
    )


def _signature_dict(signature: tuple[object, ...]) -> dict[str, object]:
    (
        benchmark,
        benchmark_version,
        model,
        model_version,
        harness,
        harness_version,
        configuration_sha256,
        environment_sha256,
    ) = signature
    return {
        "benchmark": benchmark,
        "benchmark_version": benchmark_version,
        "model": model,
        "model_version": model_version,
        "harness": harness,
        "harness_version": harness_version,
        "configuration_sha256": configuration_sha256,
        "environment_sha256": environment_sha256,
    }


def _require_single_cell(items: list[Observation], side: str) -> tuple[object, ...]:
    if not items:
        raise ValueError(f"{side} cell contains no observations")
    signatures = {_cell_signature(item) for item in items}
    if len(signatures) != 1:
        raise ValueError(f"{side} input must contain exactly one model/harness/configuration/environment cell")
    return next(iter(signatures))


def _match_key(item: Observation) -> tuple[str, str | None, str, int]:
    return (item.benchmark, item.benchmark_version, item.task_id, item.trial)


def _paired_metric(
    matched: list[tuple[Observation, Observation]], attribute: str
) -> dict[str, float | int | None]:
    deltas: list[float] = []
    for left, right in matched:
        left_value = getattr(left, attribute)
        right_value = getattr(right, attribute)
        if left_value is not None and right_value is not None:
            deltas.append(float(left_value) - float(right_value))
    return {
        "paired": len(deltas),
        "mean_delta_left_minus_right": mean(deltas) if deltas else None,
    }


def compare_cells(left: Iterable[Observation], right: Iterable[Observation]) -> dict[str, Any]:
    left_items = list(left)
    right_items = list(right)
    left_signature = _require_single_cell(left_items, "left")
    right_signature = _require_single_cell(right_items, "right")

    if left_signature[0:2] != right_signature[0:2]:
        raise ValueError("left and right cells must use the same benchmark identity/version")

    left_by_key = {_match_key(item): item for item in left_items}
    right_by_key = {_match_key(item): item for item in right_items}
    if len(left_by_key) != len(left_items):
        raise ValueError("left cell contains duplicate task/trial identities")
    if len(right_by_key) != len(right_items):
        raise ValueError("right cell contains duplicate task/trial identities")

    shared_keys = sorted(left_by_key.keys() & right_by_key.keys())
    matched = [(left_by_key[key], right_by_key[key]) for key in shared_keys]
    if not matched:
        raise ValueError("cells have no matched benchmark/task/trial observations")

    left_wins = sum(1 for l, r in matched if l.success and not r.success)
    right_wins = sum(1 for l, r in matched if r.success and not l.success)
    ties = len(matched) - left_wins - right_wins
    left_success = sum(1 for l, _ in matched if l.success) / len(matched)
    right_success = sum(1 for _, r in matched if r.success) / len(matched)

    match_payload = "\n".join(f"{key[0]}\t{key[1] or ''}\t{key[2]}\t{key[3]}" for key in shared_keys)
    matched_set_sha256 = sha256(match_payload.encode("utf-8")).hexdigest()

    return {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "left": _signature_dict(left_signature),
        "right": _signature_dict(right_signature),
        "environment_match": left_signature[7] == right_signature[7],
        "matched_trials": len(matched),
        "matched_set_sha256": matched_set_sha256,
        "left_only": len(left_by_key.keys() - right_by_key.keys()),
        "right_only": len(right_by_key.keys() - left_by_key.keys()),
        "success": {
            "left_rate": left_success,
            "right_rate": right_success,
            "delta_left_minus_right": left_success - right_success,
            "left_wins": left_wins,
            "right_wins": right_wins,
            "ties": ties,
        },
        "cost_usd": _paired_metric(matched, "cost_usd"),
        "latency_ms": _paired_metric(matched, "latency_ms"),
        "input_tokens": _paired_metric(matched, "input_tokens"),
        "output_tokens": _paired_metric(matched, "output_tokens"),
    }
