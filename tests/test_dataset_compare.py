from __future__ import annotations

import unittest

from agent_harness_index import Observation, compare_cells, dataset_fingerprint, inspect_dataset


def observation(**overrides: object) -> Observation:
    data: dict[str, object] = {
        "schema_version": "ahi.observation/v1",
        "run_id": "run-1",
        "benchmark": "fixture-bench",
        "benchmark_version": "1",
        "task_id": "task-a",
        "trial": 0,
        "model": "model-a",
        "model_version": "1",
        "harness": "harness-a",
        "harness_version": "1",
        "success": True,
        "cost_usd": 1.0,
        "latency_ms": 1000,
        "input_tokens": 100,
        "output_tokens": 50,
        "configuration": {"reasoning": "high"},
    }
    data.update(overrides)
    return Observation.from_mapping(data)


class DatasetTests(unittest.TestCase):
    def test_dataset_fingerprint_is_order_independent(self) -> None:
        first = observation()
        second = observation(run_id="run-2", task_id="task-b")
        self.assertEqual(dataset_fingerprint([first, second]), dataset_fingerprint([second, first]))

    def test_duplicate_trial_identity_is_rejected(self) -> None:
        report = inspect_dataset([observation(), observation(run_id="run-2")])
        self.assertFalse(report["valid"])
        self.assertTrue(any("duplicate trial identity" in error for error in report["errors"]))

    def test_duplicate_run_id_is_rejected(self) -> None:
        report = inspect_dataset([observation(), observation(task_id="task-b")])
        self.assertFalse(report["valid"])
        self.assertTrue(any("duplicate run_id" in error for error in report["errors"]))


class ComparisonTests(unittest.TestCase):
    def test_matched_comparison_reports_success_and_paired_metric_deltas(self) -> None:
        left = [
            observation(),
            observation(run_id="l2", task_id="task-b", success=False, cost_usd=3.0, latency_ms=2000),
        ]
        right = [
            observation(run_id="r1", model="model-b", harness="harness-b", cost_usd=2.0, latency_ms=900),
            observation(
                run_id="r2",
                task_id="task-b",
                model="model-b",
                harness="harness-b",
                success=True,
                cost_usd=1.0,
                latency_ms=1500,
            ),
        ]

        report = compare_cells(left, right)
        self.assertEqual(report["matched_trials"], 2)
        self.assertEqual(report["success"]["left_rate"], 0.5)
        self.assertEqual(report["success"]["right_rate"], 1.0)
        self.assertEqual(report["success"]["right_wins"], 1)
        self.assertEqual(report["cost_usd"]["paired"], 2)
        self.assertEqual(report["cost_usd"]["mean_delta_left_minus_right"], 0.5)

    def test_comparison_rejects_cross_benchmark_cells(self) -> None:
        with self.assertRaisesRegex(ValueError, "same benchmark"):
            compare_cells([observation()], [observation(run_id="r", benchmark="other", model="b", harness="b")])

    def test_comparison_reports_unmatched_coverage(self) -> None:
        left = [observation(), observation(run_id="l2", task_id="left-only")]
        right = [observation(run_id="r1", model="b", harness="b")]
        report = compare_cells(left, right)
        self.assertEqual(report["matched_trials"], 1)
        self.assertEqual(report["left_only"], 1)
        self.assertEqual(report["right_only"], 0)


if __name__ == "__main__":
    unittest.main()
