---
name: dual-agent-loop
description: >-
  Reviewable dual-agent software engineering workflow for a Project Lead + Chief Engineer pair.
  Coordinates bounded directives, durable run/batch state, implementation, evidence collection,
  strict baseline-vs-HEAD regression attribution, and independent review. Includes an experimental
  browser CDP transport; project-specific tools and approved transports should be used where appropriate.
---

# Dual-Agent Engineering Loop

Use this skill when a project intentionally separates:

- **Project Lead** — requirements, architecture, batch scope, acceptance criteria, review, verdicts;
- **Chief Engineer** — repository inspection, implementation, automated verification, evidence collection, and handoff.

The purpose is not to make the coding agent maximally autonomous. The purpose is to make each batch **bounded, recoverable, evidence-backed, and independently reviewed**.

---

## 1. Role boundary

### Project Lead

The Lead:

- refines ambiguous requirements;
- defines explicit GOAL / NON-GOALS / ACCEPTANCE criteria;
- decides architecture and contract changes;
- reviews evidence rather than trusting completion claims;
- may mark accepted interfaces or UI surfaces as `FROZEN`;
- returns a batch verdict such as PASS / REJECT / BLOCKED / CLOSED.

### Chief Engineer

The Engineer:

- inspects the actual repository and environment before modifying code;
- records the baseline SHA and current batch directive;
- implements the smallest compliant change;
- runs stack-appropriate checks;
- produces machine-readable evidence where practical;
- does not silently delete/skip tests to make a gate green;
- does not self-approve product quality.

---

## 2. Durable run state is mandatory for multi-batch work

For a new run, initialize:

```bash
python scripts/run_state.py \
  --state .dual-agent-loop/run-state.json \
  init --phase phase-0 --project <project-name> --base-sha <BASE_SHA>
```

The ledger stores at least:

```text
run_id
phase
batch_id
status
base_sha
head_sha
directive
evidence
verdict
history
```

For each new bounded directive:

```bash
python scripts/run_state.py \
  directive --id <DIRECTIVE_ID> --base-sha <BASE_SHA> --text "<directive summary>"
```

Update status/evidence/verdict as the batch progresses. If a terminal or browser restarts, inspect the ledger before continuing instead of reconstructing state from memory.

The ledger is not a full orchestrator. It is the durable handoff record.

---

## 3. Standard batch loop

1. **Recover / initialize state**  
   Read `.dual-agent-loop/run-state.json` if present. Confirm current phase, batch, directive, base SHA, and prior verdict.

2. **Lock directive and non-goals**  
   Do not start implementation until the batch goal and acceptance criteria are unambiguous enough to test/review.

3. **Check contracts and frozen surfaces**  
   Identify accepted API/UI/schema/behavior surfaces. Do not modify a frozen surface unless the current Lead directive explicitly reopens it.

4. **Implement the smallest compliant change**  
   Avoid unrelated refactors and speculative abstractions unless they are necessary for correctness.

5. **Run project-specific verification**  
   Execute the real build/test/lint/integration/runtime commands appropriate to the repository.

6. **Run strict regression attribution when comparable reports exist**  
   Use `scripts/compare_attribution.py` with baseline and HEAD NUnit/JUnit-family XML.

   The default strict gate blocks:

   ```text
   new failures                 > 0
   changed failure signatures   > 0
   missing baseline tests       > 0
   newly skipped tests          > 0
   duplicate test identifiers   > 0
   unknown test states          > 0
   ```

   A pre-existing failure is non-blocking only if the same test remains in the inventory and the captured failure signature remains unchanged.

   Do not describe this as mathematical proof of complete correctness. It is regression-attribution evidence.

7. **Collect runtime / visual evidence where relevant**  
   The target project must perform the real screenshot/runtime capture. `scripts/capture_screen.py` only inspects and formats existing screenshot evidence.

8. **Persist evidence and HEAD SHA**  
   Record the evidence paths/hashes and update run status before reporting to the Lead.

9. **Report and await independent verdict**  
   Send the bounded evidence pack using the configured transport. Record PASS / REJECT / BLOCKED / CLOSED in the state ledger.

10. **Advance only after verdict**  
    A PASS may unlock the next batch. A REJECT must produce a new bounded corrective batch. Do not silently reinterpret a rejected directive.

---

## 4. Five lifecycle phases

| Phase | Lead focus | Engineer focus | Typical evidence |
| --- | --- | --- | --- |
| **0. Charter & Architecture** | Scope, constraints, architecture, contracts | Environment/repository inspection | Charter, architecture, toolchain findings |
| **1. Walking Skeleton** | First runnable milestone | Minimal runnable skeleton, first baseline | Smoke result, baseline reports |
| **2. Domain Logic** | Rules and edge cases | Bounded domain implementation | Unit/integration evidence + strict attribution |
| **3. Presentation & Integration** | API/CLI/UI acceptance | Integration and runtime evidence | API samples, E2E output, screenshots |
| **4. Hardening & Release** | Project-specific release bar | Stress/simulation/package/release checks | Release checklist and reproducible artifacts |

Do not force the same test runner, screenshot method, or stress strategy across unrelated project types.

---

## 5. Experimental CDP transport

`scripts/chatgpt_cdp_bridge.py` is an **experimental transport adapter** for a browser-based Lead.

It currently:

- targets an explicit allowed hostname rather than a URL substring;
- refuses to fall back to unrelated browser tabs;
- captures a pre-send assistant snapshot;
- returns only a response detected after the send;
- supports retry and selector override options.

Requirements:

1. use a dedicated Chrome `--user-data-dir`;
2. keep CDP local-only;
3. only automate services/accounts you are authorized to automate;
4. check the applicable third-party terms/policies;
5. prefer an approved API/MCP/integration when the environment requires one;
6. treat selector breakage as a hard failure, not a reason to broaden automation to arbitrary pages.

See `SECURITY.md`.

---

## 6. Repository tools

- `scripts/compare_attribution.py` — strict baseline-vs-HEAD test inventory/state attribution
- `scripts/run_state.py` — durable run/batch state ledger
- `scripts/chatgpt_cdp_bridge.py` — experimental browser transport
- `scripts/capture_screen.py` — screenshot evidence inspector
- `tests/` — self-tests for the gate, CDP target/response logic, and run state
- `examples/regression_gate_demo/` — reproducible good/bad attribution fixtures
- `references/WORKFLOW_SPEC.md` — detailed role/protocol notes
- `references/PROJECT_INITIALIZER.md` — stack-adaptation guidance
- `references/REPORT_TEMPLATES.md` — evidence/report structures

---

## 7. Completion rule

A local Engineer may say **implementation complete** only when the requested code change is done and required local checks have run.

The **batch** is not accepted until:

- required evidence is recorded;
- strict regression blockers are zero where that gate applies;
- the Lead returns a verdict;
- the verdict is persisted in the run-state ledger.

The overall project is not automatically “production-ready” merely because one or more batches pass.
