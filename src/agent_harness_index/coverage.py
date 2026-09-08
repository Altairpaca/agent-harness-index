from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .catalog import BenchmarkCatalog
from .model import Observation

COVERAGE_SCHEMA_VERSION = "ahi.catalog-coverage/v1"


def _observed_metrics(rows: list[Observation]) -> list[str]:
    metrics = {"success"} if rows else set()
    if any(row.cost_usd is not None for row in rows):
        metrics.add("cost_usd")
    if any(row.latency_ms is not None for row in rows):
        metrics.add("latency_ms")
    if any(row.input_tokens is not None for row in rows):
        metrics.add("input_tokens")
    if any(row.output_tokens is not None for row in rows):
        metrics.add("output_tokens")
    return sorted(metrics)


def catalog_coverage(catalog: BenchmarkCatalog, observations: Iterable[Observation]) -> dict[str, object]:
    """Describe evidence coverage without turning catalog metadata into benchmark claims."""

    rows = list(observations)
    by_benchmark: dict[str, list[Observation]] = defaultdict(list)
    for row in rows:
        by_benchmark[row.benchmark].append(row)

    catalog_ids = {entry.id for entry in catalog.entries}
    entries: list[dict[str, object]] = []
    for entry in catalog.entries:
        matched = by_benchmark.get(entry.id, [])
        observed_versions = sorted({row.benchmark_version for row in matched if row.benchmark_version is not None})
        expected_versions = list(entry.versions)
        entries.append(
            {
                "id": entry.id,
                "observations": len(matched),
                "models": sorted({row.model for row in matched}),
                "harnesses": sorted({row.harness for row in matched}),
                "observed_metrics": _observed_metrics(matched),
                "declared_metrics_without_evidence": sorted(set(entry.metrics) - set(_observed_metrics(matched))),
                "evidence_uri_observations": sum(row.evidence_uri is not None for row in matched),
                "observed_versions": observed_versions,
                "declared_versions_without_evidence": sorted(set(expected_versions) - set(observed_versions)),
                "unversioned_observations": sum(row.benchmark_version is None for row in matched),
            }
        )

    unknown = sorted(
        {
            row.benchmark
            for row in rows
            if row.benchmark not in catalog_ids
        }
    )
    return {
        "schema_version": COVERAGE_SCHEMA_VERSION,
        "catalog_schema_version": catalog.schema_version,
        "observations": len(rows),
        "benchmarks": entries,
        "uncataloged_benchmarks": unknown,
    }
