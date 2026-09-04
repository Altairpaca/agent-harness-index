from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Mapping

SCHEMA_VERSION = "ahi.observation/v1"


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


def _optional_nonnegative_number(data: Mapping[str, Any], key: str) -> float | None:
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{key} must be a non-negative number when present")
    return float(value)


def _optional_nonnegative_int(data: Mapping[str, Any], key: str) -> int | None:
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{key} must be a non-negative integer when present")
    return value


def mapping_fingerprint(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def configuration_fingerprint(configuration: Mapping[str, Any]) -> str:
    return mapping_fingerprint(configuration)


def environment_fingerprint(environment: Mapping[str, Any]) -> str:
    return mapping_fingerprint(environment)


@dataclass(frozen=True, slots=True)
class Observation:
    run_id: str
    benchmark: str
    task_id: str
    trial: int
    model: str
    harness: str
    success: bool
    benchmark_version: str | None = None
    model_version: str | None = None
    harness_version: str | None = None
    latency_ms: float | None = None
    cost_usd: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    recorded_at: str | None = None
    evidence_uri: str | None = None
    environment: Mapping[str, Any] = field(default_factory=dict)
    configuration: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    @property
    def configuration_sha256(self) -> str:
        return configuration_fingerprint(self.configuration)

    @property
    def environment_sha256(self) -> str:
        return environment_fingerprint(self.environment)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "Observation":
        if data.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION!r}")

        trial = data.get("trial")
        if isinstance(trial, bool) or not isinstance(trial, int) or trial < 0:
            raise ValueError("trial must be a non-negative integer")

        success = data.get("success")
        if not isinstance(success, bool):
            raise ValueError("success must be boolean")

        environment = data.get("environment", {})
        configuration = data.get("configuration", {})
        if not isinstance(environment, dict):
            raise ValueError("environment must be an object")
        if not isinstance(configuration, dict):
            raise ValueError("configuration must be an object")

        return cls(
            run_id=_required_str(data, "run_id"),
            benchmark=_required_str(data, "benchmark"),
            task_id=_required_str(data, "task_id"),
            trial=trial,
            model=_required_str(data, "model"),
            harness=_required_str(data, "harness"),
            success=success,
            benchmark_version=_optional_str(data, "benchmark_version"),
            model_version=_optional_str(data, "model_version"),
            harness_version=_optional_str(data, "harness_version"),
            latency_ms=_optional_nonnegative_number(data, "latency_ms"),
            cost_usd=_optional_nonnegative_number(data, "cost_usd"),
            input_tokens=_optional_nonnegative_int(data, "input_tokens"),
            output_tokens=_optional_nonnegative_int(data, "output_tokens"),
            recorded_at=_optional_str(data, "recorded_at"),
            evidence_uri=_optional_str(data, "evidence_uri"),
            environment=environment,
            configuration=configuration,
        )
