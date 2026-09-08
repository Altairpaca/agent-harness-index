from __future__ import annotations

import unittest

from agent_harness_index.catalog import BenchmarkCatalog
from agent_harness_index.coverage import catalog_coverage
from agent_harness_index.model import Observation


class CatalogCoverageTests(unittest.TestCase):
    def _catalog(self) -> BenchmarkCatalog:
        return BenchmarkCatalog.from_mapping(
            {
                "schema_version": "ahi.catalog/v1",
                "benchmarks": [
                    {
                        "id": "bench-a",
                        "name": "Benchmark A",
                        "source_url": "https://example.invalid/a",
                        "task_families": ["software-engineering"],
                        "metrics": ["success", "cost_usd", "latency_ms"],
                        "evidence_policy": "matched trials",
                        "versions": ["v1", "v2"],
                    }
                ],
            }
        )

    def _observation(self, **overrides: object) -> Observation:
        value: dict[str, object] = {
            "schema_version": "ahi.observation/v1",
            "run_id": "run-1",
            "benchmark": "bench-a",
            "benchmark_version": "v1",
            "task_id": "task-1",
            "trial": 0,
            "model": "model-a",
            "harness": "harness-a",
            "success": True,
            "latency_ms": 100.0,
            "evidence_uri": "https://example.invalid/evidence/run-1",
        }
        value.update(overrides)
        return Observation.from_mapping(value)

    def test_reports_evidence_without_promoting_declared_metrics(self) -> None:
        report = catalog_coverage(self._catalog(), [self._observation()])
        row = report["benchmarks"][0]
        self.assertEqual(row["observed_metrics"], ["latency_ms", "success"])
        self.assertEqual(row["declared_metrics_without_evidence"], ["cost_usd"])
        self.assertEqual(row["observed_versions"], ["v1"])
        self.assertEqual(row["declared_versions_without_evidence"], ["v2"])
        self.assertEqual(row["evidence_uri_observations"], 1)

    def test_surfaces_uncataloged_and_unversioned_evidence(self) -> None:
        unknown = self._observation(run_id="run-2", benchmark="unknown", benchmark_version=None, evidence_uri=None)
        unversioned = self._observation(run_id="run-3", benchmark_version=None, evidence_uri=None)
        report = catalog_coverage(self._catalog(), [unknown, unversioned])
        self.assertEqual(report["uncataloged_benchmarks"], ["unknown"])
        row = report["benchmarks"][0]
        self.assertEqual(row["unversioned_observations"], 1)
        self.assertEqual(row["evidence_uri_observations"], 0)

    def test_coverage_is_descriptive_for_empty_catalog_entry(self) -> None:
        report = catalog_coverage(self._catalog(), [])
        row = report["benchmarks"][0]
        self.assertEqual(row["observations"], 0)
        self.assertEqual(row["observed_metrics"], [])
        self.assertEqual(row["declared_metrics_without_evidence"], ["cost_usd", "latency_ms", "success"])


if __name__ == "__main__":
    unittest.main()
