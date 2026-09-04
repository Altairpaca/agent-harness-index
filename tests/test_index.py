from __future__ import annotations

import unittest

from agent_harness_index import Observation, configuration_fingerprint, summarize


def observation(**overrides: object) -> Observation:
    data: dict[str, object] = {
        "schema_version": "ahi.observation/v1",
        "run_id": "run-1",
        "benchmark": "fixture-bench",
        "benchmark_version": "1",
        "task_id": "task-a",
        "trial": 0,
        "model": "model-a",
        "harness": "harness-a",
        "success": True,
        "cost_usd": 1.0,
        "latency_ms": 1000,
        "configuration": {"reasoning": "high"},
    }
    data.update(overrides)
    return Observation.from_mapping(data)


class ObservationTests(unittest.TestCase):
    def test_configuration_fingerprint_is_order_independent(self) -> None:
        left = configuration_fingerprint({"a": 1, "b": 2})
        right = configuration_fingerprint({"b": 2, "a": 1})
        self.assertEqual(left, right)

    def test_rejects_wrong_schema(self) -> None:
        with self.assertRaisesRegex(ValueError, "schema_version"):
            Observation.from_mapping(
                {
                    "schema_version": "wrong",
                    "run_id": "r",
                    "benchmark": "bench",
                    "task_id": "t",
                    "trial": 0,
                    "model": "m",
                    "harness": "h",
                    "success": True,
                }
            )

    def test_requires_benchmark_identity(self) -> None:
        with self.assertRaisesRegex(ValueError, "benchmark"):
            Observation.from_mapping(
                {
                    "schema_version": "ahi.observation/v1",
                    "run_id": "r",
                    "task_id": "t",
                    "trial": 0,
                    "model": "m",
                    "harness": "h",
                    "success": True,
                }
            )

    def test_missing_cost_is_not_treated_as_zero(self) -> None:
        rows = summarize([observation(), observation(run_id="run-2", trial=1, cost_usd=None)])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["cost_usd"], {"observed": 1, "mean": 1.0})

    def test_success_rate_and_task_set_are_reported(self) -> None:
        rows = summarize(
            [
                observation(),
                observation(run_id="run-2", task_id="task-b", trial=0, success=False, cost_usd=2.0),
            ]
        )
        row = rows[0]
        self.assertEqual(row["benchmark"], "fixture-bench")
        self.assertEqual(row["observations"], 2)
        self.assertEqual(row["successes"], 1)
        self.assertEqual(row["success_rate"], 0.5)
        self.assertEqual(row["distinct_tasks"], 2)
        self.assertEqual(len(row["task_set_sha256"]), 64)

    def test_same_task_id_from_different_benchmarks_never_coalesces(self) -> None:
        rows = summarize(
            [
                observation(),
                observation(run_id="run-2", benchmark="other-bench", benchmark_version="1"),
            ]
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["benchmark"] for row in rows}, {"fixture-bench", "other-bench"})


if __name__ == "__main__":
    unittest.main()
