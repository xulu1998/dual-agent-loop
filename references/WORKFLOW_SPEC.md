# Dual-Agent Engineering Loop Specification

This document defines the role boundary and batch protocol used by `dual-agent-loop`.

## 1. Roles

### Project Lead

Authority:

- product/scope decisions;
- architecture and contract decisions;
- acceptance criteria;
- review verdicts;
- freeze/reopen decisions for accepted surfaces.

Responsibilities:

- issue bounded directives with GOAL, NON-GOALS, and ACCEPTANCE criteria;
- review evidence rather than trusting completion claims;
- return PASS / REJECT / BLOCKED / CLOSED verdicts.

### Chief Engineer

Authority:

- local repository edits;
- local build/test/runtime commands;
- evidence generation;
- Git operations permitted by the target repository.

Responsibilities:

- lock BASE SHA before a batch;
- implement the smallest compliant change;
- run the real project verification commands;
- preserve accepted/frozen contracts unless explicitly reopened;
- persist batch state and evidence;
- never self-approve final product quality.

---

## 2. Durable handoff state

Multi-batch work should persist state in `.dual-agent-loop/run-state.json` using `scripts/run_state.py`.

Minimum state:

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

The state ledger is the recovery record after browser/terminal interruption. Chat history alone is not the source of truth for the current batch.

---

## 3. Strict regression attribution

When comparable baseline and HEAD test reports are available, run `scripts/compare_attribution.py`.

The strict default gate blocks any of the following:

```text
new failures
changed failure signatures
missing baseline tests
newly skipped/ignored tests
duplicate test identifiers
unknown test states
```

A baseline failure is considered unchanged only when:

1. the same test identifier is still present;
2. the HEAD state is still Failed;
3. the captured failure message/stack signature matches.

A baseline test that disappears is **missing**, not “fixed.”
A PASS → SKIP transition is a blocker.
A FAIL → different FAIL transition is a blocker.

This is regression-attribution evidence, not a mathematical proof that the software is correct.

---

## 4. Frozen surfaces

If the Lead marks an API, schema, behavior, screen, or component as `FROZEN`:

- do not change it outside the active directive;
- if a new requirement cannot fit the frozen contract, stop and escalate;
- do not silently resize/rewrite UI or mutate public contracts just to make a new batch pass.

---

## 5. Transport boundary

The included `scripts/chatgpt_cdp_bridge.py` is an **experimental** browser transport.

Properties:

- local CDP endpoint only;
- explicit hostname targeting;
- no fallback to unrelated browser pages;
- pre-send assistant snapshot;
- only a post-send response is returned;
- selector override for UI changes.

CDP/DOM automation is not a stable first-party protocol. Use a dedicated browser profile, check the applicable service policies, and prefer an approved API/MCP/integration when required by the environment.

The workflow is designed so transport can be replaced without changing the role/gate model.

---

## 6. Batch protocol

```text
recover state
→ receive bounded directive
→ persist directive + BASE SHA
→ check frozen contracts
→ implement minimal change
→ run project checks
→ run strict attribution (when applicable)
→ collect evidence
→ persist HEAD SHA + evidence
→ send report
→ receive Lead verdict
→ persist verdict
→ next batch / correction / close
```

A rejected batch must not be silently reframed as passed work. A new corrective directive should be explicit and traceable.
