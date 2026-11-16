"""Deterministic execution of an explicitly declared teaching-workspace program.

Reuse direction 31's restricted AST interpreter. No Python exec, imports, file
access, arbitrary function dispatch, or private test results enter model input.
"""
from __future__ import annotations

import math
import re

from scripts.full_coverage.directions.d31 import Interpreter, Unsupported


def validate_contract(contract, files):
    if contract.get("engine") != "restricted_python_ast_v1":
        raise ValueError("Unsupported workspace execution engine")
    if contract.get("source_path") not in files:
        raise ValueError("Execution source must be an existing workspace file")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", contract.get("function_name", "")):
        raise ValueError("Invalid execution function name")
    tests = contract.get("public_tests")
    if not isinstance(tests, list) or not tests or len(tests) > 100:
        raise ValueError("Execution requires a bounded public test list")
    for test in tests:
        if not isinstance(test.get("input"), list) or len(test["input"]) > 20 or "expected" not in test:
            raise ValueError("Invalid public execution test")
        if not all(type(x) is int and -100 <= x <= 100 for x in test["input"]):
            raise ValueError("Only bounded integer-list inputs are supported")


def equal_result(actual, expected):
    if expected is None:
        return actual is None
    return (type(actual) in (int, float) and type(expected) in (int, float)
            and math.isfinite(actual) and abs(actual - expected) < 1e-9)


def run_program(files, contract, tests=None):
    from scripts.full_coverage.core import digest

    source = files[contract["source_path"]]
    base = {"engine": "restricted_python_ast_v1", "source_path": contract["source_path"],
            "source_sha256": digest(source.encode()), "function_name": contract["function_name"]}
    rows = []
    try:
        if len(source) > 20000:
            raise Unsupported("Program exceeds the documented 20000-character limit")
        evaluator = Interpreter(source, function_name=contract["function_name"])
    except (SyntaxError, Unsupported, ValueError, RecursionError) as exc:
        return {**base, "passed": False, "program_error": type(exc).__name__, "detail": str(exc), "results": []}
    for index, test in enumerate(tests if tests is not None else contract["public_tests"]):
        row = {"test_id": test.get("test_id", str(index)), "input": test["input"], "expected": test["expected"]}
        try:
            actual = evaluator.run(test["input"])
            row.update(observed=actual, passed=equal_result(actual, test["expected"]))
        except (Unsupported, IndexError, ZeroDivisionError, TypeError, ValueError, OverflowError, RecursionError) as exc:
            row.update(passed=False, program_error=type(exc).__name__, detail=str(exc))
        rows.append(row)
    return {**base, "passed": bool(rows) and all(row["passed"] for row in rows), "results": rows}


def submission_checks(files, runtime, events):
    """Run public cases and require a recorded run of the submitted source."""
    result = run_program(files, runtime["execution_contract"])
    recorded = [event["observation"] for event in events
                if event.get("command", {}).get("action") == "run"]
    verified = any(row.get("source_sha256") == result["source_sha256"] and row.get("passed") is True
                   for row in recorded)
    return {"passed": result["passed"] and verified, "execution_public": result,
            "checks": [{"check": "submitted_source_passes_public_tests", "passed": result["passed"]},
                       {"check": "recorded_passing_run_of_submitted_source", "passed": verified}]}
