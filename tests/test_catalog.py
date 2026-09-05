from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from agent_harness_index.catalog import BenchmarkCatalog, load_catalog


class BenchmarkCatalogTests(unittest.TestCase):
    def _catalog(self) -> BenchmarkCatalog:
        return BenchmarkCatalog.from_mapping(
            {
                "schema_version": "ahi.catalog/v1",
                "benchmarks": [
                    {
                        "id": "frontier-harness-eval",
                        "name": "FrontierHarness Eval",
                        "source_url": "https://github.com/frontier-harness-eval/eval",
                        "task_families": ["software-engineering"],
                        "metrics": ["success", "cost_usd", "latency_ms"],
                        "evidence_policy": "matched model/task/runtime; repeated trials preferred",
                        "versions": ["2026-09"],
                    },
                    {
                        "id": "skill-regression",
                        "name": "Skill Regression Fixtures",
                        "source_url": "https://github.com/Altairpaca/skillbench",
                        "task_families": ["agent-skill"],
                        "metrics": ["success", "latency_ms"],
                        "evidence_policy": "portable observations with source provenance",
                    },
                ],
            }
        )

    def test_query_preserves_evidence_boundary(self) -> None:
        catalog = self._catalog()
        self.assertEqual([entry.id for entry in catalog.query(metric="cost_usd")], ["frontier-harness-eval"])
        self.assertEqual([entry.id for entry in catalog.query(task_family="agent-skill")], ["skill-regression"])
        self.assertEqual([entry.id for entry in catalog.query(text="repeated trials")], ["frontier-harness-eval"])

    def test_rejects_unknown_metric_and_duplicate_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported metrics"):
            BenchmarkCatalog.from_mapping(
                {
                    "schema_version": "ahi.catalog/v1",
                    "benchmarks": [
                        {
                            "id": "bad",
                            "name": "Bad",
                            "source_url": "https://example.com",
                            "task_families": ["coding"],
                            "metrics": ["subjective_score"],
                            "evidence_policy": "none",
                        }
                    ],
                }
            )

        entry = {
            "id": "dup",
            "name": "Duplicate",
            "source_url": "https://example.com",
            "task_families": ["coding"],
            "metrics": ["success"],
            "evidence_policy": "matched trials",
        }
        with self.assertRaisesRegex(ValueError, "ids must be unique"):
            BenchmarkCatalog.from_mapping(
                {"schema_version": "ahi.catalog/v1", "benchmarks": [entry, dict(entry)]}
            )

    def test_load_catalog_round_trip(self) -> None:
        catalog = self._catalog()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(catalog.to_mapping()), encoding="utf-8")
            loaded = load_catalog(path)
        self.assertEqual(loaded, catalog)


if __name__ == "__main__":
    unittest.main()
