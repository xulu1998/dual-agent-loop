import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "compare_attribution.py"
spec = importlib.util.spec_from_file_location("compare_attribution", MODULE_PATH)
compare_attribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare_attribution)


def junit(cases):
    body = []
    for name, state, message in cases:
        if state == "pass":
            body.append(f'<testcase classname="demo" name="{name}"/>')
        elif state == "fail":
            body.append(
                f'<testcase classname="demo" name="{name}"><failure message="{message}">{message}</failure></testcase>'
            )
        elif state == "skip":
            body.append(f'<testcase classname="demo" name="{name}"><skipped/></testcase>')
        else:
            raise ValueError(state)
    return "<testsuite>" + "".join(body) + "</testsuite>"


def nunit(cases):
    body = []
    for name, state, message in cases:
        if state == "pass":
            body.append(f'<test-case fullname="demo.{name}" result="Passed"/>')
        elif state == "fail":
            body.append(
                f'<test-case fullname="demo.{name}" result="Failed"><failure><message>{message}</message><stack-trace>{message} stack</stack-trace></failure></test-case>'
            )
        elif state == "skip":
            body.append(f'<test-case fullname="demo.{name}" result="Skipped"/>')
        else:
            raise ValueError(state)
    return "<test-run>" + "".join(body) + "</test-run>"


class AttributionGateTests(unittest.TestCase):
    def compare(self, baseline_xml, head_xml):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "baseline.xml"
            head = Path(tmp) / "head.xml"
            base.write_text(textwrap.dedent(baseline_xml), encoding="utf-8")
            head.write_text(textwrap.dedent(head_xml), encoding="utf-8")
            return compare_attribution.compare_suites(str(base), str(head), "fixture")

    def test_preexisting_identical_failure_is_allowed(self):
        base = junit([("ok", "pass", ""), ("legacy", "fail", "known")])
        head = junit([("ok", "pass", ""), ("legacy", "fail", "known")])
        result = self.compare(base, head)
        self.assertTrue(result["gate_pass"])
        self.assertEqual(result["attribution"]["identical_failures"], ["demo.legacy"])

    def test_new_failure_blocks(self):
        base = junit([("a", "pass", "")])
        head = junit([("a", "fail", "boom")])
        result = self.compare(base, head)
        self.assertFalse(result["gate_pass"])
        self.assertEqual(result["attribution"]["head_only_failures"], ["demo.a"])

    def test_changed_failure_signature_blocks(self):
        base = junit([("legacy", "fail", "old reason")])
        head = junit([("legacy", "fail", "different reason")])
        result = self.compare(base, head)
        self.assertFalse(result["gate_pass"])
        self.assertEqual(len(result["attribution"]["changed_failures"]), 1)

    def test_missing_test_blocks_instead_of_being_counted_as_fixed(self):
        base = junit([("a", "pass", ""), ("legacy", "fail", "known")])
        head = junit([("a", "pass", "")])
        result = self.compare(base, head)
        self.assertFalse(result["gate_pass"])
        self.assertEqual(result["inventory"]["missing_tests"], ["demo.legacy"])
        self.assertEqual(result["attribution"]["fixed_failures"], [])

    def test_new_skip_blocks(self):
        base = junit([("a", "pass", "")])
        head = junit([("a", "skip", "")])
        result = self.compare(base, head)
        self.assertFalse(result["gate_pass"])
        self.assertEqual(result["attribution"]["new_skips"], ["demo.a"])

    def test_fixed_failure_is_allowed_when_test_remains_in_inventory(self):
        base = junit([("legacy", "fail", "known")])
        head = junit([("legacy", "pass", "")])
        result = self.compare(base, head)
        self.assertTrue(result["gate_pass"])
        self.assertEqual(result["attribution"]["fixed_failures"], ["demo.legacy"])

    def test_new_passing_test_is_allowed(self):
        base = junit([("a", "pass", "")])
        head = junit([("a", "pass", ""), ("new", "pass", "")])
        result = self.compare(base, head)
        self.assertTrue(result["gate_pass"])
        self.assertEqual(result["inventory"]["new_tests"], ["demo.new"])

    def test_new_skipped_test_blocks(self):
        base = junit([("a", "pass", "")])
        head = junit([("a", "pass", ""), ("new", "skip", "")])
        result = self.compare(base, head)
        self.assertFalse(result["gate_pass"])
        self.assertEqual(result["attribution"]["new_skips"], ["demo.new"])

    def test_nunit_is_supported(self):
        base = nunit([("a", "pass", ""), ("legacy", "fail", "known")])
        head = nunit([("a", "pass", ""), ("legacy", "fail", "known")])
        result = self.compare(base, head)
        self.assertTrue(result["gate_pass"])
        self.assertEqual(result["baseline"]["summary"]["total"], 2)

    def test_duplicate_test_identifiers_block(self):
        xml = """
        <testsuite>
          <testcase classname="demo" name="dup"/>
          <testcase classname="demo" name="dup"/>
        </testsuite>
        """
        result = self.compare(xml, xml)
        self.assertFalse(result["gate_pass"])
        self.assertEqual(result["blockers"]["duplicate_tests"], ["demo.dup"])

    def test_report_contains_hashes_and_metadata(self):
        base = junit([("a", "pass", "")])
        head = junit([("a", "pass", "")])
        with tempfile.TemporaryDirectory() as tmp:
            base_path = Path(tmp) / "baseline.xml"
            head_path = Path(tmp) / "head.xml"
            base_path.write_text(base, encoding="utf-8")
            head_path.write_text(head, encoding="utf-8")
            result = compare_attribution.compare_suites(
                str(base_path),
                str(head_path),
                "fixture",
                base_sha="abc",
                head_sha="def",
                runner="pytest 9",
            )
        self.assertEqual(result["base_sha"], "abc")
        self.assertEqual(result["head_sha"], "def")
        self.assertEqual(result["runner"], "pytest 9")
        self.assertEqual(len(result["baseline"]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
