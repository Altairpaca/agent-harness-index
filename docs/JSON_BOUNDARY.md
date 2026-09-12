# Observation JSON boundary

`Observation.from_mapping()` rejects non-finite cost/latency, float-overflowing numeric telemetry, and metadata that cannot be represented as portable JSON. Missing telemetry remains `None`; it is not zero or a failed measurement.

Configuration/environment permit objects with string keys, arrays, strings, finite numbers, booleans and null. Python tuples, sets, bytes, opaque objects, non-string keys and cycles are rejected rather than coerced into another identity. Repeated references to an otherwise valid child are not cycles.

## Compatibility

The schema remains `ahi.observation/v1`. For valid existing JSON, sorted-key compact UTF-8 serialization and SHA-256 bytes are unchanged. This is input validation tightening: previously accepted non-JSON observations must be corrected at their producer, not silently rewritten during aggregation. No benchmark scores or statistical claims are added.

This is not an immutable snapshot redesign. Direct dataclass construction and subsequent mutation of caller-owned metadata remain separate API concerns. Use the validated ingestion path for external records.

## Regression

`python -m unittest discover -s tests -v` includes `test_observation_json_boundary.py`. The nine tests cover rejected telemetry, metadata coercions/cycles, repeated child references, missingness and unchanged valid fingerprints.

Refs #12.
