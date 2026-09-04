# Evidence and Escalation Templates

## Template 1: Directive closeout evidence pack

```markdown
# PROJECT LEAD DIRECTIVE CLOSEOUT REPORT

RUN ID: <run_id>
PHASE: <phase>
BATCH ID: <batch_id>
DIRECTIVE ID: <directive_id>
TASK: <task name>
BASE SHA: <baseline Git SHA>
HEAD SHA: <current Git SHA>
BRANCH: <working branch>
STATUS: EVIDENCE READY / AWAITING REVIEW

## 1. Scope and implementation evidence

- Goal: <bounded goal>
- Non-goals preserved: <yes/no + notes>
- Files/components changed: <paths + concise summary>
- Frozen contracts touched: <none / explicitly reopened by directive>

## 2. Automated verification

Project-specific checks:

- Build/lint/unit/integration/E2E: <commands + result>

Strict baseline-vs-HEAD attribution (when comparable XML exists):

- Baseline report SHA-256: <hash>
- HEAD report SHA-256: <hash>
- Runner: <runner/version>
- New failures: 0
- Changed failure signatures: 0
- Missing baseline tests: 0
- New skips: 0
- Duplicate test IDs: 0
- Unknown test states: 0
- Pre-existing identical failures: <count>
- Fixed baseline failures: <count>
- New passing tests: <count/list>
- Attribution JSON: <path>

If any strict blocker is non-zero, this report is BLOCKED rather than ready for PASS.

## 3. Runtime / visual evidence (if applicable)

- Capture mechanism: <Playwright / engine / emulator / other>
- Evidence files: <paths/URLs>
- Relevant target sizes/platforms: <project-specific>
- Observed issues: <none / list>

## 4. Durable state

- State file: `.dual-agent-loop/run-state.json`
- Current status: awaiting-review
- Evidence entries persisted: <yes/no>

## 5. Requested Lead verdict

Please return one explicit verdict:

- PASS
- REJECT (with corrective directive)
- BLOCKED (decision/input required)
- CLOSED
```

---

## Template 2: Blocked / escalation report

```markdown
# CHIEF ENGINEER BLOCKED / ESCALATION REPORT

RUN ID: <run_id>
BATCH ID: <batch_id>
DIRECTIVE ID: <directive_id>
BASE SHA: <base sha>
HEAD SHA: <head sha if any>

## Blocking issue

<short title>

## Evidence

- failing command / test / log / screenshot / contract conflict
- exact artifact paths
- strict attribution blockers if relevant

## Why the Engineer stopped

<explain which directive, frozen contract, missing decision, or safety boundary prevents a valid implementation>

## Decision options

- Option A: <trade-off>
- Option B: <trade-off>
- Option C: <trade-off if useful>

## Current action

Work is halted on the blocked scope. No silent contract expansion or test deletion/skipping has been used to bypass the blocker.
```
