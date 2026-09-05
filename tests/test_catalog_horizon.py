from __future__ import annotations

import unittest

from agent_harness_index.catalog import BenchmarkCatalog


class CatalogHorizonTests(unittest.TestCase):
    def test_horizon_is_explicit_and_queryable(self) -> None:
        catalog = BenchmarkCatalog.from_mapping(
            {
                "schema_version": "ahi.catalog/v1",
                "benchmarks": [
                    {
                        "id": "short-suite",
                        "name": "Short Suite",
                        "source_url": "https://example.invalid/short",
                        "task_families": ["software-engineering"],
                        "metrics": ["success"],
                        "evidence_policy": "matched trials",
                        "horizon": "short",
                    },
                    {
                        "id": "unknown-suite",
                        "name": "Unknown Suite",
                        "source_url": "https://example.invalid/unknown",
                        "task_families": ["software-engineering"],
                        "metrics": ["success"],
                        "evidence_policy": "matched trials",
                    },
                ],
            }
        )
        self.assertEqual([entry.id for entry in catalog.query(horizon="short")], ["short-suite"])
        self.assertEqual([entry.id for entry in catalog.query(horizon="unknown")], ["unknown-suite"])

    def test_invalid_horizon_is_rejected_instead_of_inferred(self) -> None:
        with self.assertRaisesRegex(ValueError, "horizon must be one of"):
            BenchmarkCatalog.from_mapping(
                {
                    "schema_version": "ahi.catalog/v1",
                    "benchmarks": [
                        {
                            "id": "suite",
                            "name": "Suite",
                            "source_url": "https://example.invalid/suite",
                            "task_families": ["software-engineering"],
                            "metrics": ["success"],
                            "evidence_policy": "matched trials",
                            "horizon": "very-long",
                        }
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
