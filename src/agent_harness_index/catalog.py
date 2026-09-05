from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

CATALOG_SCHEMA_VERSION = "ahi.catalog/v1"
_ALLOWED_METRICS = frozenset({"success", "cost_usd", "latency_ms", "input_tokens", "output_tokens"})
_ALLOWED_HORIZONS = frozenset({"short", "medium", "long", "mixed", "unknown"})


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _string_list(data: Mapping[str, Any], key: str, *, required: bool = False) -> tuple[str, ...]:
    value = data.get(key)
    if value is None:
        if required:
            raise ValueError(f"{key} must be a non-empty array of strings")
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{key} must be an array of strings")
    if not value:
        if required:
            raise ValueError(f"{key} must be a non-empty array of strings")
        return ()
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return tuple(dict.fromkeys(item.strip() for item in value))


def _optional_horizon(data: Mapping[str, Any]) -> str:
    value = data.get("horizon", "unknown")
    if not isinstance(value, str) or value not in _ALLOWED_HORIZONS:
        raise ValueError(f"horizon must be one of: {', '.join(sorted(_ALLOWED_HORIZONS))}")
    return value


@dataclass(frozen=True, slots=True)
class BenchmarkCatalogEntry:
    id: str
    name: str
    source_url: str
    task_families: tuple[str, ...]
    metrics: tuple[str, ...]
    evidence_policy: str
    versions: tuple[str, ...] = ()
    horizon: str = "unknown"
    notes: str | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "BenchmarkCatalogEntry":
        metrics = _string_list(data, "metrics", required=True)
        unknown_metrics = sorted(set(metrics) - _ALLOWED_METRICS)
        if unknown_metrics:
            raise ValueError(f"unsupported metrics: {', '.join(unknown_metrics)}")
        notes = data.get("notes")
        if notes is not None and (not isinstance(notes, str) or not notes.strip()):
            raise ValueError("notes must be a non-empty string when present")
        return cls(
            id=_required_str(data, "id"),
            name=_required_str(data, "name"),
            source_url=_required_str(data, "source_url"),
            task_families=_string_list(data, "task_families", required=True),
            metrics=metrics,
            evidence_policy=_required_str(data, "evidence_policy"),
            versions=_string_list(data, "versions"),
            horizon=_optional_horizon(data),
            notes=notes.strip() if isinstance(notes, str) else None,
        )

    def to_mapping(self) -> dict[str, object]:
        value: dict[str, object] = {
            "id": self.id,
            "name": self.name,
            "source_url": self.source_url,
            "task_families": list(self.task_families),
            "metrics": list(self.metrics),
            "evidence_policy": self.evidence_policy,
            "horizon": self.horizon,
        }
        if self.versions:
            value["versions"] = list(self.versions)
        if self.notes is not None:
            value["notes"] = self.notes
        return value


@dataclass(frozen=True, slots=True)
class BenchmarkCatalog:
    entries: tuple[BenchmarkCatalogEntry, ...]
    schema_version: str = CATALOG_SCHEMA_VERSION

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "BenchmarkCatalog":
        if data.get("schema_version") != CATALOG_SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {CATALOG_SCHEMA_VERSION!r}")
        raw_entries = data.get("benchmarks")
        if not isinstance(raw_entries, list) or not raw_entries:
            raise ValueError("benchmarks must be a non-empty array")
        entries: list[BenchmarkCatalogEntry] = []
        for item in raw_entries:
            if not isinstance(item, dict):
                raise ValueError("benchmark entries must be objects")
            entries.append(BenchmarkCatalogEntry.from_mapping(item))
        ids = [entry.id for entry in entries]
        if len(ids) != len(set(ids)):
            raise ValueError("benchmark ids must be unique")
        return cls(entries=tuple(entries))

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "benchmarks": [entry.to_mapping() for entry in self.entries],
        }

    def query(
        self,
        *,
        metric: str | None = None,
        task_family: str | None = None,
        horizon: str | None = None,
        text: str | None = None,
    ) -> tuple[BenchmarkCatalogEntry, ...]:
        if metric is not None and metric not in _ALLOWED_METRICS:
            raise ValueError(f"unsupported metric: {metric}")
        if horizon is not None and horizon not in _ALLOWED_HORIZONS:
            raise ValueError(f"unsupported horizon: {horizon}")
        needle = text.casefold().strip() if text else None
        result: list[BenchmarkCatalogEntry] = []
        for entry in self.entries:
            if metric is not None and metric not in entry.metrics:
                continue
            if task_family is not None and task_family not in entry.task_families:
                continue
            if horizon is not None and horizon != entry.horizon:
                continue
            if needle is not None:
                haystack = " ".join((entry.id, entry.name, entry.evidence_policy, entry.horizon, entry.notes or "")).casefold()
                if needle not in haystack:
                    continue
            result.append(entry)
        return tuple(result)


def load_catalog(path: Path) -> BenchmarkCatalog:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("catalog root must be an object")
    return BenchmarkCatalog.from_mapping(value)


def render_catalog(entries: Sequence[BenchmarkCatalogEntry]) -> str:
    return json.dumps([entry.to_mapping() for entry in entries], indent=2, sort_keys=True)
