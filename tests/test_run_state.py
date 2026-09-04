import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_state.py"
spec = importlib.util.spec_from_file_location("run_state", MODULE_PATH)
run_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_state)


class RunStateTests(unittest.TestCase):
    def test_full_batch_handoff_is_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "state.json")
            state = run_state.init_state(path, "phase-0", "base0", "demo")
            self.assertEqual(state["batch_id"], 0)
            self.assertEqual(state["status"], "initialized")

            state = run_state.set_directive(path, "D-001", "base1", "Implement one bounded change")
            self.assertEqual(state["batch_id"], 1)
            self.assertEqual(state["directive"]["id"], "D-001")

            state = run_state.set_status(path, "implementing", "head1")
            self.assertEqual(state["head_sha"], "head1")

            state = run_state.add_evidence(path, "regression", "artifacts/gate.json", "abc123", None)
            self.assertEqual(state["status"], "evidence-ready")
            self.assertEqual(len(state["evidence"]), 1)

            state = run_state.set_verdict(path, "pass", "accepted")
            self.assertEqual(state["status"], "passed")
            self.assertEqual(state["verdict"]["value"], "pass")

            reloaded = run_state.load_state(path)
            self.assertEqual(reloaded["run_id"], state["run_id"])
            self.assertGreaterEqual(len(reloaded["history"]), 5)

    def test_new_directive_resets_batch_evidence_and_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "state.json")
            run_state.init_state(path, "phase-1", "base", "demo")
            run_state.set_directive(path, "D-001", None, None)
            run_state.add_evidence(path, "test", "one.json", None, None)
            run_state.set_verdict(path, "pass", None)
            state = run_state.set_directive(path, "D-002", None, None)
            self.assertEqual(state["batch_id"], 2)
            self.assertEqual(state["evidence"], [])
            self.assertIsNone(state["verdict"])

    def test_invalid_phase_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "state.json")
            with self.assertRaises(ValueError):
                run_state.init_state(path, "phase-9", None, None)

    def test_init_does_not_overwrite_existing_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "state.json")
            run_state.init_state(path, "phase-0", None, None)
            with self.assertRaises(FileExistsError):
                run_state.init_state(path, "phase-0", None, None)


if __name__ == "__main__":
    unittest.main()
