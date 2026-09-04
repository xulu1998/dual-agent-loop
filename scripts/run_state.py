#!/usr/bin/env python3
"""Small durable state ledger for a dual-agent engineering run.

This is intentionally not a full orchestrator. It persists the minimum handoff
state needed to recover after a terminal/browser restart and to make each batch
traceable: run, phase, batch, directive, base SHA, evidence, and Lead verdict.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone


SCHEMA_VERSION = 1
VALID_PHASES = {"phase-0", "phase-1", "phase-2", "phase-3", "phase-4"}
VALID_STATUSES = {
    "initialized",
    "directive-received",
    "implementing",
    "evidence-ready",
    "awaiting-review",
    "passed",
    "rejected",
    "blocked",
    "closed",
}
VALID_VERDICTS = {"pass", "reject", "blocked", "closed"}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_state(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        state = json.load(handle)
    if state.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported run-state schema: {state.get('schema_version')}; expected {SCHEMA_VERSION}"
        )
    return state


def save_state(path: str, state):
    """Atomically replace the state file to reduce corruption on interruption."""
    target = os.path.abspath(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    state["updated_at"] = now_iso()

    fd, temp_path = tempfile.mkstemp(prefix=".run-state-", suffix=".json", dir=os.path.dirname(target))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temp_path, target)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def _append_history(state, event: str, details=None):
    state.setdefault("history", []).append(
        {"at": now_iso(), "event": event, "details": details or {}}
    )


def init_state(path: str, phase: str, base_sha: str | None, project: str | None):
    if os.path.exists(path):
        raise FileExistsError(f"State already exists: {path}")
    if phase not in VALID_PHASES:
        raise ValueError(f"Invalid phase: {phase}")

    state = {
        "schema_version": SCHEMA_VERSION,
        "run_id": str(uuid.uuid4()),
        "project": project,
        "phase": phase,
        "batch_id": 0,
        "status": "initialized",
        "base_sha": base_sha,
        "head_sha": None,
        "directive": None,
        "evidence": [],
        "verdict": None,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "history": [],
    }
    _append_history(state, "run-initialized", {"phase": phase, "base_sha": base_sha})
    save_state(path, state)
    return state


def set_directive(path: str, directive_id: str, base_sha: str | None, text: str | None):
    state = load_state(path)
    state["batch_id"] = int(state.get("batch_id", 0)) + 1
    state["base_sha"] = base_sha or state.get("base_sha")
    state["directive"] = {
        "id": directive_id,
        "text": text,
        "received_at": now_iso(),
    }
    state["evidence"] = []
    state["verdict"] = None
    state["status"] = "directive-received"
    _append_history(
        state,
        "directive-received",
        {"batch_id": state["batch_id"], "directive_id": directive_id, "base_sha": state["base_sha"]},
    )
    save_state(path, state)
    return state


def set_status(path: str, status: str, head_sha: str | None = None):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    state = load_state(path)
    state["status"] = status
    if head_sha:
        state["head_sha"] = head_sha
    _append_history(state, "status-changed", {"status": status, "head_sha": head_sha})
    save_state(path, state)
    return state


def set_phase(path: str, phase: str):
    if phase not in VALID_PHASES:
        raise ValueError(f"Invalid phase: {phase}")
    state = load_state(path)
    old = state.get("phase")
    state["phase"] = phase
    _append_history(state, "phase-changed", {"from": old, "to": phase})
    save_state(path, state)
    return state


def add_evidence(path: str, kind: str, evidence_path: str, sha256: str | None, note: str | None):
    state = load_state(path)
    item = {
        "kind": kind,
        "path": evidence_path,
        "sha256": sha256,
        "note": note,
        "recorded_at": now_iso(),
    }
    state.setdefault("evidence", []).append(item)
    state["status"] = "evidence-ready"
    _append_history(state, "evidence-added", item)
    save_state(path, state)
    return state


def set_verdict(path: str, verdict: str, note: str | None):
    if verdict not in VALID_VERDICTS:
        raise ValueError(f"Invalid verdict: {verdict}")
    state = load_state(path)
    state["verdict"] = {"value": verdict, "note": note, "at": now_iso()}
    state["status"] = {
        "pass": "passed",
        "reject": "rejected",
        "blocked": "blocked",
        "closed": "closed",
    }[verdict]
    _append_history(state, "lead-verdict", state["verdict"])
    save_state(path, state)
    return state


def print_state(state):
    print(json.dumps(state, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Durable dual-agent run-state ledger")
    parser.add_argument("--state", default=".dual-agent-loop/run-state.json")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--phase", default="phase-0", choices=sorted(VALID_PHASES))
    init.add_argument("--base-sha")
    init.add_argument("--project")

    directive = sub.add_parser("directive")
    directive.add_argument("--id", required=True, dest="directive_id")
    directive.add_argument("--base-sha")
    directive.add_argument("--text")

    status = sub.add_parser("status")
    status.add_argument("value", choices=sorted(VALID_STATUSES))
    status.add_argument("--head-sha")

    phase = sub.add_parser("phase")
    phase.add_argument("value", choices=sorted(VALID_PHASES))

    evidence = sub.add_parser("evidence")
    evidence.add_argument("--kind", required=True)
    evidence.add_argument("--path", required=True, dest="evidence_path")
    evidence.add_argument("--sha256")
    evidence.add_argument("--note")

    verdict = sub.add_parser("verdict")
    verdict.add_argument("value", choices=sorted(VALID_VERDICTS))
    verdict.add_argument("--note")

    sub.add_parser("show")
    args = parser.parse_args()

    try:
        if args.command == "init":
            state = init_state(args.state, args.phase, args.base_sha, args.project)
        elif args.command == "directive":
            state = set_directive(args.state, args.directive_id, args.base_sha, args.text)
        elif args.command == "status":
            state = set_status(args.state, args.value, args.head_sha)
        elif args.command == "phase":
            state = set_phase(args.state, args.value)
        elif args.command == "evidence":
            state = add_evidence(
                args.state, args.kind, args.evidence_path, args.sha256, args.note
            )
        elif args.command == "verdict":
            state = set_verdict(args.state, args.value, args.note)
        else:
            state = load_state(args.state)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
        return

    print_state(state)


if __name__ == "__main__":
    main()
