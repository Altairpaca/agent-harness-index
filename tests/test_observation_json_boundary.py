"""Regression coverage for portable telemetry and metadata identity."""
from __future__ import annotations

from hashlib import sha256
import json
import math
import unittest

from agent_harness_index.model import Observation, mapping_fingerprint


def row(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "schema_version": "ahi.observation/v1", "run_id": "r", "benchmark": "b",
        "task_id": "t", "trial": 0, "model": "m", "harness": "h", "success": True,
    }
    data.update(overrides)
    return data


class ObservationJsonBoundaryTests(unittest.TestCase):
    def test_nonfinite_telemetry_is_rejected(self) -> None:
        for field in ("latency_ms", "cost_usd"):
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, field):
                        Observation.from_mapping(row(**{field: value}))

    def test_unrepresentable_integer_telemetry_is_a_validation_error(self) -> None:
        for field in ("latency_ms", "cost_usd"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    Observation.from_mapping(row(**{field: 10 ** 400}))

    def test_valid_telemetry_and_missingness_are_preserved(self) -> None:
        for value in (None, 0, 2, 1.25):
            item = Observation.from_mapping(row(latency_ms=value, cost_usd=value))
            expected = None if value is None else float(value)
            self.assertEqual(item.latency_ms, expected)
            self.assertEqual(item.cost_usd, expected)
        for value in (True, -1, "1"):
            with self.assertRaises(ValueError):
                Observation.from_mapping(row(latency_ms=value))

    def test_nonfinite_metadata_is_rejected_at_ingestion(self) -> None:
        for field in ("configuration", "environment"):
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, field):
                        Observation.from_mapping(row(**{field: {"nested": [value]}}))

    def test_nonstring_keys_cannot_alias_string_keys(self) -> None:
        self.assertEqual(len(mapping_fingerprint({"1": "value"})), 64)
        for key in (1, None, True):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    mapping_fingerprint({key: "value"})
        with self.assertRaisesRegex(ValueError, "configuration"):
            Observation.from_mapping(row(configuration={"nested": {1: "value"}}))

    def test_non_json_containers_and_objects_are_rejected(self) -> None:
        for value in ((1, 2), {1, 2}, object(), b"bytes"):
            with self.subTest(type=type(value).__name__):
                with self.assertRaisesRegex(ValueError, "environment"):
                    Observation.from_mapping(row(environment={"value": value}))

    def test_cycles_are_rejected_without_recursion_failure(self) -> None:
        cyclic: dict[str, object] = {}
        cyclic["self"] = cyclic
        with self.assertRaisesRegex(ValueError, "configuration"):
            Observation.from_mapping(row(configuration=cyclic))
        items: list[object] = []
        items.append(items)
        with self.assertRaises(ValueError):
            mapping_fingerprint({"items": items})

    def test_reused_children_are_not_mistaken_for_cycles(self) -> None:
        child = {"x": [None, True, 1, 2.5, "市场"]}
        actual = {"left": child, "right": child}
        expected = {"left": child, "right": {"x": [None, True, 1, 2.5, "市场"]}}
        self.assertEqual(mapping_fingerprint(actual), mapping_fingerprint(expected))

    def test_valid_fingerprint_bytes_do_not_change(self) -> None:
        payload = {"z": [None, True, False, 0, -4, 2.5, "市场"], "a": {"effort": "high"}}
        expected = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()
        self.assertEqual(mapping_fingerprint(payload), expected)
        self.assertEqual(mapping_fingerprint(payload), mapping_fingerprint(dict(reversed(list(payload.items())))))
        item = Observation.from_mapping(row(configuration=payload, environment=payload))
        self.assertEqual(item.configuration_sha256, expected)
        self.assertEqual(item.environment_sha256, expected)


if __name__ == "__main__":
    unittest.main()
