#!/usr/bin/env python3
"""
Regression Attribution Comparator for automated test XML results.

Supported inputs:
- NUnit-style XML (including Unity / Tuanjie-style test-case elements)
- Common JUnit-style XML (testcase + failure/error/skipped elements)

Computes the exact delta between a Baseline test run and a Head (current) test run:
- HEAD-ONLY Failures (critical: must be 0 to pass the default gate)
- Baseline-Only Failures (fixed tests)
- Identical Failures (pre-existing, inherited from baseline)
- Changed Failure Signatures (same failing test, different failure text)
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET


FAILED_RESULTS = {"failed", "failure", "error"}
PASSED_RESULTS = {"passed", "pass", "success", "successful"}
SKIPPED_RESULTS = {"skipped", "ignored", "inconclusive", "notrun", "not-run"}


def _local_name(tag: str) -> str:
    """Return an XML tag name without an optional namespace prefix."""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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
    """Normalize NUnit/JUnit case state into Passed / Failed / Skipped / other."""
    raw_result = test_case.attrib.get("result")
    if raw_result:
        lowered = raw_result.strip().lower()
        if lowered in FAILED_RESULTS:
            return "Failed"
        if lowered in PASSED_RESULTS:
            return "Passed"
        if lowered in SKIPPED_RESULTS:
            return "Skipped"
        return raw_result

    # JUnit normally expresses state through child elements rather than result=.
    if _direct_child(test_case, {"failure", "error"}) is not None:
        return "Failed"
    if _direct_child(test_case, {"skipped"}) is not None:
        return "Skipped"
    return "Passed"


def _case_name(test_case) -> str:
    fullname = test_case.attrib.get("fullname")
    if fullname:
        return fullname

    name = test_case.attrib.get("name", "Unknown")
    classname = test_case.attrib.get("classname")
    if classname and name:
        return f"{classname}.{name}"
    return name


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
                # Keep the signature concise while preserving the full body as stack text.
                message = body.splitlines()[0][:1000]

    # NUnit often nests <message> and <stack-trace> below <failure>.
    nested_message = _first_descendant_text(test_case, {"message"})
    nested_stack = _first_descendant_text(test_case, {"stack-trace", "stacktrace"})

    if nested_message:
        message = nested_message
    if nested_stack:
        stack_trace = nested_stack

    return message, stack_trace


def parse_test_results(xml_path: str):
    """Parse common NUnit/JUnit-family XML into a normalized test dictionary."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Test result file not found: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    tests = {}
    for element in root.iter():
        if _local_name(element.tag) not in {"test-case", "testcase"}:
            continue

        name = _case_name(element)
        result = _normalize_result(element)
        fail_msg, stack_trace = _failure_details(element)

        tests[name] = {
            "result": result,
            "message": fail_msg,
            "stack": stack_trace,
        }

    # Prefer summary attributes where available, but fall back to normalized cases.
    total = _safe_int(root.attrib.get("total", root.attrib.get("tests")), len(tests))
    if total == 0 and tests:
        total = len(tests)

    failed_attr = root.attrib.get("failed", root.attrib.get("failures"))
    failed = _safe_int(failed_attr, -1)
    errors = _safe_int(root.attrib.get("errors"), 0)
    if failed < 0:
        failed = sum(1 for info in tests.values() if info["result"] == "Failed")
    else:
        failed += errors

    skipped_attr = root.attrib.get("skipped", root.attrib.get("disabled"))
    skipped = _safe_int(skipped_attr, -1)
    if skipped < 0:
        skipped = sum(1 for info in tests.values() if info["result"] == "Skipped")

    passed = _safe_int(root.attrib.get("passed"), -1)
    if passed < 0:
        passed = max(total - failed - skipped, 0)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "tests": tests,
    }


def _failure_signature(info):
    """Build a stable-enough signature for detecting changed failure reasons."""
    return (info.get("message", "").strip(), info.get("stack", "").strip())


def compare_suites(baseline_path: str, head_path: str, suite_name: str = "Test Suite"):
    """Compare baseline and HEAD test results and return an attribution dictionary."""
    base = parse_test_results(baseline_path)
    head = parse_test_results(head_path)

    print(f"=== {suite_name} COMPARISON ===")
    print(
        f"Baseline: Total={base['total']}, Passed={base['passed']}, "
        f"Failed={base['failed']}, Skipped={base['skipped']}"
    )
    print(
        f"HEAD:     Total={head['total']}, Passed={head['passed']}, "
        f"Failed={head['failed']}, Skipped={head['skipped']}"
    )
    print("-" * 50)

    base_fails = {k: v for k, v in base["tests"].items() if v["result"] == "Failed"}
    head_fails = {k: v for k, v in head["tests"].items() if v["result"] == "Failed"}

    identical = []
    base_only = []
    head_only = []
    changed_sig = []

    for name, b_info in base_fails.items():
        if name not in head_fails:
            base_only.append(name)
            continue

        h_info = head_fails[name]
        if _failure_signature(b_info) == _failure_signature(h_info):
            identical.append(name)
        else:
            changed_sig.append(
                {
                    "name": name,
                    "baseline_msg": b_info["message"],
                    "head_msg": h_info["message"],
                }
            )

    for name in head_fails:
        if name not in base_fails:
            head_only.append(name)

    print(f"  Identical Failures (Pre-existing): {len(identical)}")
    print(f"  Fixed in HEAD (Baseline-Only):     {len(base_only)}")
    print(f"  HEAD-ONLY Failures (NEW BREAKS):   {len(head_only)}")
    print(f"  Changed Signatures:                {len(changed_sig)}")
    print("-" * 50)

    if head_only:
        print("[FAIL GATE] Tests that fail in HEAD but not in the baseline:")
        for test_name in head_only:
            print(f"  * {test_name}")
            msg = head_fails[test_name]["message"]
            if msg:
                suffix = "..." if len(msg) > 200 else ""
                print(f"    Message: {msg[:200]}{suffix}")

    return {
        "suite": suite_name,
        "baseline_summary": {k: base[k] for k in ["total", "passed", "failed", "skipped"]},
        "head_summary": {k: head[k] for k in ["total", "passed", "failed", "skipped"]},
        "head_only_count": len(head_only),
        "head_only_tests": head_only,
        "fixed_count": len(base_only),
        "fixed_tests": base_only,
        "identical_count": len(identical),
        "changed_signature_count": len(changed_sig),
        "changed_signatures": changed_sig,
        "gate_pass": len(head_only) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="A/B test regression attribution comparator")
    parser.add_argument("--baseline", required=True, help="Path to baseline test result XML")
    parser.add_argument("--head", required=True, help="Path to HEAD test result XML")
    parser.add_argument("--suite", default="Unit Tests", help="Suite name (for example: Unit Tests)")
    parser.add_argument("--json", help="Optional path to write comparison JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Backward-compatible alias for the default behavior: fail when HEAD-ONLY > 0",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Report new failures without exiting with status 1",
    )

    args = parser.parse_args()
    result = compare_suites(args.baseline, args.head, args.suite)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)
        print(f"Report saved to {args.json}")

    strict = not args.no_strict
    if strict and not result["gate_pass"]:
        print(
            f"\n[STRICT GATE FAILED] {result['head_only_count']} HEAD-ONLY "
            "failures detected."
        )
        sys.exit(1)

    if result["gate_pass"]:
        print("\n[GATE PASSED] Zero HEAD-ONLY regressions.")
    else:
        print("\n[REPORT ONLY] HEAD-ONLY regressions detected; strict exit disabled.")


if __name__ == "__main__":
    main()
