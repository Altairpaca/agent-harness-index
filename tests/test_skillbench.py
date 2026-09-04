from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import unittest

from agent_harness_index import Observation, SkillBenchDiagnostic, normalize_skillbench_observation

FIXTURE = Path(__file__).parent / "fixtures" / "skillbench-harness-observation.v1.json"


def fixture() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class SkillBenchInteropTests(unittest.TestCase):
    def test_scoreable_fixture_normalizes_without_losing_identity(self) -> None:
        result = normalize_skillbench_observation(fixture())
        self.assertIsInstance(result, Observation)
        assert isinstance(result, Observation)
        self.assertEqual(result.run_id, "fixture-run-001")
        self.assertEqual(result.benchmark, "skillbench-fixture")
        self.assertEqual(result.benchmark_version, "1")
        self.assertEqual(result.task_id, "portable-contract")
        self.assertEqual(result.model, "fixture-model")
        self.assertEqual(result.model_version, "2026-08-31")
        self.assertEqual(result.harness, "fixture-harness")
        self.assertEqual(result.harness_version, "1.2.3")
        self.assertEqual(result.success, True)
        self.assertEqual(result.latency_ms, 1250.0)
        self.assertEqual(result.configuration["_skillbench"]["skill_source_sha256"], "a" * 64)

    def test_fail_maps_to_false_but_error_and_skipped_do_not_enter_score_cells(self) -> None:
        failed = fixture()
        failed["outcome"] = "fail"
        failed_result = normalize_skillbench_observation(failed)
        self.assertIsInstance(failed_result, Observation)
        assert isinstance(failed_result, Observation)
        self.assertFalse(failed_result.success)

        for outcome in ("error", "skipped"):
            payload = fixture()
            payload["outcome"] = outcome
            result = normalize_skillbench_observation(payload)
            self.assertIsInstance(result, SkillBenchDiagnostic)
            assert isinstance(result, SkillBenchDiagnostic)
            self.assertFalse(result.scoreable)
            self.assertEqual(result.outcome, outcome)

    def test_skill_source_is_part_of_configuration_identity(self) -> None:
        first = normalize_skillbench_observation(fixture())
        other_payload = fixture()
        other_payload["skillSourceSha256"] = "b" * 64
        other_payload["runId"] = "fixture-run-002"
        second = normalize_skillbench_observation(other_payload)
        assert isinstance(first, Observation)
        assert isinstance(second, Observation)
        self.assertNotEqual(first.configuration_sha256, second.configuration_sha256)

    def test_reserved_skillbench_configuration_key_is_rejected(self) -> None:
        payload = fixture()
        payload["configuration"] = {"_skillbench": {"spoofed": True}}
        with self.assertRaisesRegex(ValueError, "reserves the _skillbench key"):
            normalize_skillbench_observation(payload)

    def test_latency_must_match_timestamps(self) -> None:
        payload = fixture()
        payload["latencyMs"] = 999
        with self.assertRaisesRegex(ValueError, "latencyMs must equal"):
            normalize_skillbench_observation(payload)

    def test_normalized_mapping_round_trips_through_ahi_schema(self) -> None:
        result = normalize_skillbench_observation(fixture())
        assert isinstance(result, Observation)
        round_trip = Observation.from_mapping(asdict(result))
        self.assertEqual(round_trip, result)


if __name__ == "__main__":
    unittest.main()
