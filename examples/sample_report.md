# Example evidence pack

This is an illustrative closeout report showing the structure expected from a Chief Engineer. Project names, SHAs, counts, and paths below are examples.

```markdown
# PROJECT LEAD DIRECTIVE CLOSEOUT REPORT

RUN ID: 8cce8f6e-example
PHASE: phase-2
BATCH ID: 7
DIRECTIVE ID: D-007
TASK: Shop capability rule update
BASE SHA: b5fa94917d0bbdbfad82baaf1181b296c8f50851
HEAD SHA: 5ffe0f415f6d7c04426e7cbbcd08deae79aaa0bc
BRANCH: feat/shop-capability
STATUS: EVIDENCE READY / AWAITING REVIEW

## 1. Scope / implementation

- Implemented only the three rules named by D-007.
- No frozen UI or public schema files modified.
- Changed files:
  - Core/Phase11ShopVisit.cs
  - Core/Phase6Gate11Domain.cs
  - Tests/Editor/Phase16ShopCapabilityProductRuleTests.cs

## 2. Project verification

New directive tests:

- 30 added
- 30 passed

Full EditMode HEAD report:

- total: 250
- passed: 245
- failed: 3
- skipped: 2

The repository baseline already contained the same three failing test IDs.

## 3. Strict baseline-vs-HEAD attribution

Evidence file: artifacts/editmode-attribution.json

- Baseline XML SHA-256: <baseline hash>
- HEAD XML SHA-256: <head hash>
- Runner: Unity/Tuanjie NUnit-compatible EditMode runner
- New failures: 0
- Changed failure signatures: 0
- Missing baseline tests: 0
- New skips: 0
- Duplicate test IDs: 0
- Unknown states: 0
- Identical pre-existing failures: 3
- Fixed baseline failures: 0
- New passing tests: 30

STRICT ATTRIBUTION GATE: PASS

Note: this establishes attribution for the compared test inventory. It does not prove complete software correctness.

## 4. Runtime / visual evidence

Capture mechanism: project engine runtime

- artifacts/screen-720x1280.png — reviewed for target mobile layout
- artifacts/screen-1440x2560.png — reviewed for target high-density layout

No frozen surface was intentionally changed by this directive.

## 5. Durable handoff state

`.dual-agent-loop/run-state.json` contains:

- current batch: 7
- directive: D-007
- BASE SHA / HEAD SHA
- attribution evidence path
- screenshot evidence paths
- status: awaiting-review

## 6. Requested Lead verdict

Please return one explicit verdict:

PASS / REJECT / BLOCKED / CLOSED
```
