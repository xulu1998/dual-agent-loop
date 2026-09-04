#!/usr/bin/env python3
"""
Regression Attribution Comparator for Automated Test XML Results (NUnit / JUnit / Unity / Tuanjie).

Computes the exact delta between a Baseline test run and a Head (current) test run:
- HEAD-ONLY Failures (CRITICAL: Must be 0 to pass gate)
- Baseline-Only Failures (Fixed tests)
- Identical Failures (Pre-existing, inherited from baseline)
- Changed Failure Signatures (Pre-existing tests failing for a different reason)
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET


def parse_test_results(xml_path: str):
    """Parses NUnit / JUnit / Tuanjie test result XML."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Test result file not found: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # NUnit / Tuanjie style root or test-run child
    run_el = root if root.tag == "test-run" else (root.find("test-run") or root)
    stats = run_el.attrib

    total = int(stats.get("total", stats.get("testcasecount", 0)))
    passed = int(stats.get("passed", 0))
    failed = int(stats.get("failed", 0))
    skipped = int(stats.get("skipped", stats.get("inconclusive", 0)))

    tests = {}
    for tc in root.iter("test-case"):
        fullname = tc.attrib.get("fullname", tc.attrib.get("name", "Unknown"))
        result = tc.attrib.get("result", "Unknown")
        fail_msg = ""
        stack_trace = ""

        failure_elem = tc.find("failure")
        if failure_elem is not None:
            msg_elem = failure_elem.find("message")
            if msg_elem is not None and msg_elem.text:
                fail_msg = msg_elem.text.strip()
            stack_elem = failure_elem.find("stack-trace")
            if stack_elem is not None and stack_elem.text:
                stack_trace = stack_elem.text.strip()
        else:
            # Check for generic message child
            msg_el = tc.find(".//message")
            if msg_el is not None and msg_el.text:
                fail_msg = msg_el.text.strip()

        tests[fullname] = {
            "result": result,
            "message": fail_msg,
            "stack": stack_trace
        }

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "tests": tests
    }


def compare_suites(baseline_path: str, head_path: str, suite_name: str = "Test Suite"):
    """Compares baseline and head test results and returns attribution dict."""
    base = parse_test_results(baseline_path)
    head = parse_test_results(head_path)

    print(f"=== {suite_name} COMPARISON ===")
    print(f"Baseline: Total={base['total']}, Passed={base['passed']}, Failed={base['failed']}, Skipped={base['skipped']}")
    print(f"HEAD:     Total={head['total']}, Passed={head['passed']}, Failed={head['failed']}, Skipped={head['skipped']}")
    print("-" * 50)

    base_fails = {k: v for k, v in base["tests"].items() if v["result"] in ("Failed", "Error")}
    head_fails = {k: v for k, v in head["tests"].items() if v["result"] in ("Failed", "Error")}

    identical = []
    base_only = []
    head_only = []
    changed_sig = []

    for name, b_info in base_fails.items():
        if name not in head_fails:
            base_only.append(name)
        else:
            h_info = head_fails[name]
            if b_info["message"] == h_info["message"]:
                identical.append(name)
            else:
                changed_sig.append({
                    "name": name,
                    "baseline_msg": b_info["message"],
                    "head_msg": h_info["message"]
                })

    for name in head_fails:
        if name not in base_fails:
            head_only.append(name)

    print(f"  Identical Failures (Pre-existing): {len(identical)}")
    print(f"  Fixed in HEAD (Baseline-Only):     {len(base_only)}")
    print(f"  HEAD-ONLY Failures (NEW BREAKS):   {len(head_only)}")
    print(f"  Changed Signatures:                {len(changed_sig)}")
    print("-" * 50)

    if head_only:
        print("[FAIL GATE] The following tests failed in HEAD but passed/were absent in Baseline:")
        for t in head_only:
            print(f"  * {t}")
            msg = head_fails[t]["message"]
            if msg:
                print(f"    Message: {msg[:200]}...")

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
        "gate_pass": len(head_only) == 0
    }


def main():
    parser = argparse.ArgumentParser(description="A/B Test Regression Attribution Comparator")
    parser.add_argument("--baseline", required=True, help="Path to baseline test result XML")
    parser.add_argument("--head", required=True, help="Path to HEAD test result XML")
    parser.add_argument("--suite", default="Unit Tests", help="Suite name (e.g., EditMode, PlayMode)")
    parser.add_argument("--json", help="Optional path to output comparison JSON")
    parser.add_argument("--strict", action="store_true", default=True, help="Exit with code 1 if HEAD-ONLY > 0")

    args = parser.parse_args()

    res = compare_suites(args.baseline, args.head, args.suite)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
        print(f"Report saved to {args.json}")

    if args.strict and not res["gate_pass"]:
        print(f"\n[STRICT GATE FAILED] {res['head_only_count']} HEAD-ONLY failures detected! Aborting.")
        sys.exit(1)
    else:
        print("\n[GATE PASSED] Zero HEAD-ONLY regressions.")


if __name__ == "__main__":
    main()
