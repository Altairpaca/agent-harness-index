from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Iterable

from .aggregate import summarize
from .catalog import load_catalog, render_catalog
from .compare import compare_cells
from .coverage import catalog_coverage
from .dataset import inspect_dataset
from .model import Observation
from .skillbench import SkillBenchDiagnostic, normalize_skillbench_observation


def _iter_records(path: Path) -> Iterable[tuple[int, dict[str, object]]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number}: observation must be a JSON object")
            yield line_number, value


def _load(path: Path) -> list[Observation]:
    observations: list[Observation] = []
    for line_number, value in _iter_records(path):
        try:
            observations.append(Observation.from_mapping(value))
        except ValueError as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
    if not observations:
        raise ValueError("input contains no observations")
    return observations


def _validate(path: Path) -> int:
    errors: list[str] = []
    count = 0
    try:
        records = list(_iter_records(path))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "observations": 0, "errors": [str(exc)]}, indent=2))
        return 1

    for line_number, value in records:
        try:
            Observation.from_mapping(value)
            count += 1
        except ValueError as exc:
            errors.append(f"line {line_number}: {exc}")

    print(json.dumps({"valid": not errors and count > 0, "observations": count, "errors": errors}, indent=2))
    return 0 if not errors and count > 0 else 1


def _normalize_skillbench(path: Path) -> int:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("SkillBench observation must be a JSON object")
    result = normalize_skillbench_observation(value)
    print(json.dumps(asdict(result), sort_keys=True, separators=(",", ":")))
    return 1 if isinstance(result, SkillBenchDiagnostic) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ahi", description="Normalize and compare agent-harness benchmark observations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate observation JSONL syntax and row contracts")
    validate_parser.add_argument("path", type=Path)

    integrity_parser = subparsers.add_parser("integrity", help="inspect dataset-level uniqueness and content fingerprint")
    integrity_parser.add_argument("path", type=Path)

    summarize_parser = subparsers.add_parser("summarize", help="aggregate comparable observations")
    summarize_parser.add_argument("path", type=Path)

    compare_parser = subparsers.add_parser("compare", help="compare two single cells on matched benchmark/task/trial observations")
    compare_parser.add_argument("left", type=Path)
    compare_parser.add_argument("right", type=Path)

    skillbench_parser = subparsers.add_parser(
        "normalize-skillbench",
        help="normalize one verified skillbench.harness-observation/v1 payload into AHI",
    )
    skillbench_parser.add_argument("path", type=Path)

    catalog_validate = subparsers.add_parser("catalog-validate", help="validate an ahi.catalog/v1 benchmark catalog")
    catalog_validate.add_argument("path", type=Path)

    catalog_query = subparsers.add_parser("catalog-query", help="discover benchmarks by evidence-relevant metadata")
    catalog_query.add_argument("path", type=Path)
    catalog_query.add_argument("--metric")
    catalog_query.add_argument("--task-family")
    catalog_query.add_argument("--text")

    catalog_coverage_parser = subparsers.add_parser(
        "catalog-coverage",
        help="report which catalog metadata is backed by normalized observations",
    )
    catalog_coverage_parser.add_argument("catalog", type=Path)
    catalog_coverage_parser.add_argument("observations", type=Path)

    args = parser.parse_args(argv)
    if args.command == "validate":
        return _validate(args.path)

    try:
        if args.command == "integrity":
            report = inspect_dataset(_load(args.path))
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["valid"] else 1

        if args.command == "summarize":
            rows = summarize(_load(args.path))
            print(json.dumps(rows, indent=2, sort_keys=True))
            return 0

        if args.command == "compare":
            report = compare_cells(_load(args.left), _load(args.right))
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0

        if args.command == "normalize-skillbench":
            return _normalize_skillbench(args.path)

        if args.command == "catalog-validate":
            catalog = load_catalog(args.path)
            print(json.dumps({"valid": True, "benchmarks": len(catalog.entries)}, sort_keys=True))
            return 0

        if args.command == "catalog-query":
            catalog = load_catalog(args.path)
            entries = catalog.query(metric=args.metric, task_family=args.task_family, text=args.text)
            print(render_catalog(entries))
            return 0

        if args.command == "catalog-coverage":
            report = catalog_coverage(load_catalog(args.catalog), _load(args.observations))
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"ahi: {exc}", file=sys.stderr)
        return 2

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
