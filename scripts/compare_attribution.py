#!/usr/bin/env python3
"""Strict baseline-vs-HEAD regression attribution for NUnit/JUnit XML.

The default gate blocks when the current run introduces any of the following:
- a test that newly fails (HEAD-only failure)
- an existing failure whose signature changes
- a baseline test that disappears from the HEAD inventory
- a test that becomes newly skipped/ignored/inconclusive
- duplicate test identifiers that make attribution ambiguous

This is deliberately stricter than comparing aggregate pass/fail counts. The
report can also be emitted as JSON for an agent evidence pack.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


FAILED_RESULTS = {"failed", "failure", "error"}
PASSED_RESULTS = {"passed", "pass", "success", "successful"}
SKIPPED_RESULTS = {"skipped", "ignored", "inconclusive", "notrun", "not-run"}
NORMALIZED_STATES = {"Passed", "Failed", "Skipped"}


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _direct_child(element, wanted_names):
    wanted_names = set(wanted_names)
    for child in element:
        if _local_name(child.tag) in wanted_names:
            return child
    return None


def _first_descendant_text(element, wanted_names):
    wanted_names = set(wanted_names)
    for child in element.iter():
        if _local_name(child.tag) in wanted_names and child.text:
            text = child.text.strip()
            if text:
                return text
    return ""


def _normalize_result(test_case) -> str:
    raw_result = test_case.attrib.get("result")
    if raw_result:
        lowered = raw_result.strip().lower()
        if lowered in FAILED_RESULTS:
            return "Failed"
        if lowered in PASSED_RESULTS:
            return "Passed"
        if lowered in SKIPPED_RESULTS:
            return "Skipped"
        return raw_result.strip() or "Unknown"

    # JUnit normally expresses state through child elements.
    if _direct_child(test_case, {"failure", "error"}) is not None:
        return "Failed"
    if _direct_child(test_case, {"skipped"}) is not None:
        return "Skipped"
    return "Passed"


def _case_name(test_case) -> str:
    fullname = test_case.attrib.get("fullname")
    if fullname:
        return fullname.strip()

    name = (test_case.attrib.get("name") or "Unknown").strip()
    classname = (test_case.attrib.get("classname") or "").strip()
    return f"{classname}.{name}" if classname else name


def _failure_details(test_case):
    failure_element = _direct_child(test_case, {"failure", "error"})
    message = ""
    stack_trace = ""

    if failure_element is not None:
        message = (failure_element.attrib.get("message") or "").strip()
        body = (failure_element.text or "").strip()
        if body:
            stack_trace = body
            if not message:
                message = body.splitlines()[0][:1000]

    # NUnit often nests message/stack-trace below <failure>.
    nested_message = _first_descendant_text(test_case, {"message"})
    nested_stack = _first_descendant_text(test_case, {"stack-trace", "stacktrace"})
    if nested_message:
        message = nested_message
    if nested_stack:
        stack_trace = nested_stack

    return message, stack_trace


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_test_results(xml_path: str):
    """Parse NUnit/JUnit-family XML into a normalized test inventory."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Test result file not found: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    tests = {}
    duplicates = []
    unknown_states = []

    for element in root.iter():
        if _local_name(element.tag) not in {"test-case", "testcase"}:
            continue

        name = _case_name(element)
        result = _normalize_result(element)
        fail_msg, stack_trace = _failure_details(element)

        if name in tests:
            duplicates.append(name)
            continue

        if result not in NORMALIZED_STATES:
            unknown_states.append({"name": name, "state": result})

        tests[name] = {
            "result": result,
            "message": fail_msg,
            "stack": stack_trace,
        }

    total = len(tests)
    passed = sum(1 for info in tests.values() if info["result"] == "Passed")
    failed = sum(1 for info in tests.values() if info["result"] == "Failed")
    skipped = sum(1 for info in tests.values() if info["result"] == "Skipped")

    return {
        "path": os.path.abspath(xml_path),
        "sha256": _sha256(xml_path),
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "tests": tests,
        "duplicates": sorted(set(duplicates)),
        "unknown_states": unknown_states,
    }


def _failure_signature(info):
    """Signature used to tell a pre-existing failure from a changed failure."""
    return (info.get("message", "").strip(), info.get("stack", "").strip())


def compare_suites(
    baseline_path: str,
    head_path: str,
    suite_name: str = "Test Suite",
    *,
    base_sha: str | None = None,
    head_sha: str | None = None,
    runner: str | None = None,
):
    base = parse_test_results(baseline_path)
    head = parse_test_results(head_path)

    base_names = set(base["tests"])
    head_names = set(head["tests"])
    common_names = base_names & head_names

    missing_tests = sorted(base_names - head_names)
    new_tests = sorted(head_names - base_names)

    head_only_failures = []
    fixed_failures = []
    identical_failures = []
    changed_failures = []
    new_skips = []
    state_transitions = []

    for name in sorted(common_names):
        base_info = base["tests"][name]
        head_info = head["tests"][name]
        base_state = base_info["result"]
        head_state = head_info["result"]

        if base_state != head_state:
            state_transitions.append({"name": name, "baseline": base_state, "head": head_state})

        if head_state == "Failed" and base_state != "Failed":
            head_only_failures.append(name)
        elif base_state == "Failed" and head_state == "Failed":
            if _failure_signature(base_info) == _failure_signature(head_info):
                identical_failures.append(name)
            else:
                changed_failures.append(
                    {
                        "name": name,
                        "baseline_msg": base_info.get("message", ""),
                        "head_msg": head_info.get("message", ""),
                    }
                )
        elif base_state == "Failed" and head_state != "Failed":
            fixed_failures.append(name)

        if head_state == "Skipped" and base_state != "Skipped":
            new_skips.append(name)

    # A brand-new test that fails is also a HEAD-only failure. A brand-new test
    # that is skipped is also considered a new skip because it contributes no
    # verification evidence.
    for name in new_tests:
        state = head["tests"][name]["result"]
        if state == "Failed":
            head_only_failures.append(name)
        elif state == "Skipped":
            new_skips.append(name)

    head_only_failures = sorted(set(head_only_failures))
    new_skips = sorted(set(new_skips))

    duplicate_tests = sorted(set(base["duplicates"] + head["duplicates"]))
    unknown_states = {
        "baseline": base["unknown_states"],
        "head": head["unknown_states"],
    }

    blockers = {
        "head_only_failures": head_only_failures,
        "changed_failures": changed_failures,
        "missing_tests": missing_tests,
        "new_skips": new_skips,
        "duplicate_tests": duplicate_tests,
        "unknown_states": unknown_states,
    }
    blocker_count = (
        len(head_only_failures)
        + len(changed_failures)
        + len(missing_tests)
        + len(new_skips)
        + len(duplicate_tests)
        + len(base["unknown_states"])
        + len(head["unknown_states"])
    )

    result = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suite": suite_name,
        "runner": runner,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "baseline": {
            "path": base["path"],
            "sha256": base["sha256"],
            "summary": {k: base[k] for k in ["total", "passed", "failed", "skipped"]},
        },
        "head": {
            "path": head["path"],
            "sha256": head["sha256"],
            "summary": {k: head[k] for k in ["total", "passed", "failed", "skipped"]},
        },
        "inventory": {
            "baseline_count": len(base_names),
            "head_count": len(head_names),
            "new_tests": new_tests,
            "missing_tests": missing_tests,
        },
        "attribution": {
            "head_only_failures": head_only_failures,
            "changed_failures": changed_failures,
            "identical_failures": identical_failures,
            "fixed_failures": fixed_failures,
            "new_skips": new_skips,
            "state_transitions": state_transitions,
        },
        "blockers": blockers,
        "blocker_count": blocker_count,
        "gate_pass": blocker_count == 0,
    }

    print(f"=== {suite_name} STRICT ATTRIBUTION ===")
    print(
        f"Baseline: total={base['total']} passed={base['passed']} "
        f"failed={base['failed']} skipped={base['skipped']}"
    )
    print(
        f"HEAD:     total={head['total']} passed={head['passed']} "
        f"failed={head['failed']} skipped={head['skipped']}"
    )
    print("-" * 64)
    print(f"New failures:              {len(head_only_failures)}")
    print(f"Changed failure signatures:{len(changed_failures):>3}")
    print(f"Missing baseline tests:    {len(missing_tests):>3}")
    print(f"New skips:                 {len(new_skips):>3}")
    print(f"Duplicate test IDs:        {len(duplicate_tests):>3}")
    print(
        f"Unknown states:            "
        f"{len(base['unknown_states']) + len(head['unknown_states']):>3}"
    )
    print(f"Fixed baseline failures:   {len(fixed_failures):>3}")
    print(f"New tests discovered:      {len(new_tests):>3}")
    print("-" * 64)
    print("GATE:", "PASS" if result["gate_pass"] else f"FAIL ({blocker_count} blocker(s))")

    return result


def main():
    parser = argparse.ArgumentParser(description="Strict baseline-vs-HEAD test attribution gate")
    parser.add_argument("--baseline", required=True, help="Baseline NUnit/JUnit XML")
    parser.add_argument("--head", required=True, help="HEAD NUnit/JUnit XML")
    parser.add_argument("--suite", default="Unit Tests", help="Human-readable suite name")
    parser.add_argument("--json", help="Optional JSON evidence output path")
    parser.add_argument("--base-sha", help="Optional baseline Git commit SHA")
    parser.add_argument("--head-sha", help="Optional HEAD Git commit SHA")
    parser.add_argument("--runner", help="Optional test-runner identifier/version")
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Report blockers without returning exit status 1",
    )
    args = parser.parse_args()

    result = compare_suites(
        args.baseline,
        args.head,
        args.suite,
        base_sha=args.base_sha,
        head_sha=args.head_sha,
        runner=args.runner,
    )

    if args.json:
        output_dir = os.path.dirname(os.path.abspath(args.json))
        os.makedirs(output_dir, exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)
        print(f"Evidence JSON: {args.json}")

    if not result["gate_pass"] and not args.no_strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
