from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import math
import re
from typing import Any, Mapping

from .model import Observation, mapping_fingerprint

SKILLBENCH_OBSERVATION_SCHEMA_VERSION = "skillbench.harness-observation/v1"
SKILLBENCH_IMPORT_SCHEMA_VERSION = "ahi.skillbench-import/v1"


@dataclass(frozen=True, slots=True)
class SkillBenchDiagnostic:
    schema_version: str
    run_id: str
    outcome: str
    scoreable: bool
    reason: str

    def to_mapping(self) -> dict[str, object]:
        return asdict(self)


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _optional_str(data: Mapping[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string when present")
    return value


def _required_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _nonnegative_int(data: Mapping[str, Any], key: str, *, required: bool = False) -> int | None:
    value = data.get(key)
    if value is None and not required:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{key} must be a non-negative integer")
    return value


def _nonnegative_number(data: Mapping[str, Any], key: str, *, required: bool = False) -> float | None:
    value = data.get(key)
    if value is None and not required:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{key} must be a non-negative finite number")
    return float(value)


def _parse_timestamp(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone offset")
    return parsed


def normalize_skillbench_observation(payload: Mapping[str, Any]) -> Observation | SkillBenchDiagnostic:
    if payload.get("schemaVersion") != SKILLBENCH_OBSERVATION_SCHEMA_VERSION:
        raise ValueError(f"schemaVersion must equal {SKILLBENCH_OBSERVATION_SCHEMA_VERSION!r}")

    run_id = _required_str(payload, "runId")
    benchmark = _required_mapping(payload, "benchmark")
    harness = _required_mapping(payload, "harness")
    model = _required_mapping(payload, "model")
    configuration = dict(_required_mapping(payload, "configuration"))
    environment = dict(_required_mapping(payload, "environment"))

    benchmark_id = _required_str(benchmark, "id")
    benchmark_version = _optional_str(benchmark, "version")
    harness_id = _required_str(harness, "id")
    harness_version = _required_str(harness, "version")
    model_id = _required_str(model, "id")
    model_version = _optional_str(model, "version")
    case_id = _required_str(payload, "caseId")
    trial = _nonnegative_int(payload, "trial", required=True)
    assert trial is not None

    source_sha256 = _required_str(payload, "skillSourceSha256").lower()
    if re.fullmatch(r"[0-9a-f]{64}", source_sha256) is None:
        raise ValueError("skillSourceSha256 must be a 64-character SHA-256 hex digest")

    outcome = _required_str(payload, "outcome")
    if outcome not in {"pass", "fail", "error", "skipped"}:
        raise ValueError("outcome must be pass, fail, error, or skipped")

    started_at = _required_str(payload, "startedAt")
    finished_at = _required_str(payload, "finishedAt")
    started = _parse_timestamp(started_at, "startedAt")
    finished = _parse_timestamp(finished_at, "finishedAt")
    if finished < started:
        raise ValueError("finishedAt must not precede startedAt")

    latency_ms = _nonnegative_number(payload, "latencyMs", required=True)
    assert latency_ms is not None
    derived_latency_ms = (finished - started).total_seconds() * 1000
    if abs(latency_ms - derived_latency_ms) > 1e-6:
        raise ValueError("latencyMs must equal the elapsed time between startedAt and finishedAt")

    input_tokens = _nonnegative_int(payload, "inputTokens")
    output_tokens = _nonnegative_int(payload, "outputTokens")
    cost_usd = _nonnegative_number(payload, "costUsd")
    evidence_uri = _optional_str(payload, "evidenceUri")

    # Fail early if either object contains values that AHI cannot fingerprint deterministically.
    mapping_fingerprint(configuration)
    mapping_fingerprint(environment)

    if "_skillbench" in configuration:
        raise ValueError("configuration reserves the _skillbench key for importer provenance")
    configuration["_skillbench"] = {
        "observation_schema": SKILLBENCH_OBSERVATION_SCHEMA_VERSION,
        "skill_source_sha256": source_sha256,
    }

    if outcome in {"error", "skipped"}:
        return SkillBenchDiagnostic(
            schema_version=SKILLBENCH_IMPORT_SCHEMA_VERSION,
            run_id=run_id,
            outcome=outcome,
            scoreable=False,
            reason="execution outcome is not a benchmark pass/fail and is excluded from AHI score cells",
        )

    return Observation(
        run_id=run_id,
        benchmark=benchmark_id,
        benchmark_version=benchmark_version,
        task_id=case_id,
        trial=trial,
        model=model_id,
        model_version=model_version,
        harness=harness_id,
        harness_version=harness_version,
        success=outcome == "pass",
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        recorded_at=finished_at,
        evidence_uri=evidence_uri,
        environment=environment,
        configuration=configuration,
    )
