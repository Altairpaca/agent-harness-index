from __future__ import annotations

import json
from pathlib import Path
import unittest

from agent_harness_index import Observation, normalize_skillbench_observation, summarize

FIXTURES = Path(__file__).parent / "fixtures"
PORTABLE = FIXTURES / "skillbench-harness-observation.v1.json"
GOLDEN = FIXTURES / "skillbench-golden-summary.v1.json"


class GoldenHandoffTests(unittest.TestCase):
    def test_skillbench_portable_observation_produces_exact_golden_summary(self) -> None:
        portable = json.loads(PORTABLE.read_text(encoding="utf-8"))
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))

        normalized = normalize_skillbench_observation(portable)
        self.assertIsInstance(normalized, Observation)
        assert isinstance(normalized, Observation)

        rows = summarize([normalized])
        self.assertEqual(rows, [expected])

    def test_golden_summary_pins_skill_revision_and_execution_environment(self) -> None:
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(
            expected["configuration_sha256"],
            "32bc35c2c9567835be1c0f50129678d5eebcda5f84509149425b6d87a27434fc",
        )
        self.assertEqual(
            expected["environment_sha256"],
            "0d435a1e8407264720c153cf519ba81edca28a44033b0e36933a6f4c7825e730",
        )
        self.assertEqual(
            expected["task_set_sha256"],
            "4f6eeaba335444e611bb2629e2078976937e32863dde934ff7f1ff03244e1ce1",
        )


if __name__ == "__main__":
    unittest.main()
