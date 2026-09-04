# Reproducible regression-gate demo

This tiny fixture demonstrates the strict baseline-vs-HEAD gate without requiring any external test runner.

The baseline intentionally contains one known legacy failure. A valid HEAD is allowed to preserve that exact pre-existing failure while adding new passing tests. The strict gate blocks new failures, changed failure signatures, missing baseline tests, and newly skipped tests.

## Passing case

```bash
python scripts/compare_attribution.py \
  --baseline examples/regression_gate_demo/baseline.xml \
  --head examples/regression_gate_demo/head-good.xml \
  --suite "demo" \
  --base-sha BASE_DEMO \
  --head-sha HEAD_GOOD_DEMO \
  --runner "fixture" \
  --json /tmp/dual-agent-loop-good.json
```

Expected result:

```text
GATE: PASS
```

Why it passes:

- the known baseline failure remains present with the same failure signature;
- all baseline tests remain in the HEAD inventory;
- the new test passes;
- no test becomes newly skipped.

## Failing case

```bash
python scripts/compare_attribution.py \
  --baseline examples/regression_gate_demo/baseline.xml \
  --head examples/regression_gate_demo/head-bad.xml \
  --suite "demo" \
  --base-sha BASE_DEMO \
  --head-sha HEAD_BAD_DEMO \
  --runner "fixture" \
  --json /tmp/dual-agent-loop-bad.json
```

Expected result: the process exits with status `1` and reports multiple blockers.

The bad HEAD intentionally contains:

- a new failure (`demo.Cart.adds_item`);
- a changed signature for the pre-existing legacy failure;
- a missing baseline test (`demo.Cart.removes_item`);
- a newly skipped test (`demo.Cart.new_discount_rule`).

This example is meant to make the attribution behavior auditable. It is not a claim that XML comparison alone proves full software correctness.
