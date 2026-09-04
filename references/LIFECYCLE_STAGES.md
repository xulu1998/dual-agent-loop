# End-to-End Dual-Agent Engineering Lifecycle

The lifecycle is a structured default, not a claim that every project requires identical stages or tools.

## Phase matrix

| Phase | Project Lead focus | Chief Engineer focus | Typical deliverables / gate |
| --- | --- | --- | --- |
| **0. Charter & Architecture** | Clarify user need, scope, constraints, contracts, and acceptance criteria | Inspect repository/environment/toolchain; initialize run state | Charter/architecture notes; Lead approves scope before implementation |
| **1. Walking Skeleton** | Define the smallest meaningful runnable path | Build minimal runnable skeleton; establish smoke checks and baseline reports where practical | Runnable path + baseline evidence |
| **2. Domain Logic** | Define business rules, invariants, and edge cases | Implement bounded domain logic and appropriate automated tests | Required checks pass; strict regression blockers are zero where comparable reports exist |
| **3. Presentation & Integration** | Define API/CLI/UI acceptance criteria | Integrate surfaces; run integration/E2E/runtime checks; collect evidence | Evidence reviewed; accepted contracts/surfaces may be marked FROZEN |
| **4. Hardening & Release** | Define project-specific release bar | Run relevant stress/simulation/package/security/release checks | No unresolved release blockers under the agreed checklist |

## Lifecycle rules

1. **Persist state**  
   Multi-batch work should use `.dual-agent-loop/run-state.json`. Each directive, base/head SHA, evidence artifact, and verdict should be traceable.

2. **Bound each batch**  
   A directive should contain a concrete goal, explicit non-goals, and acceptance criteria. Avoid speculative scope expansion.

3. **Use project-appropriate verification**  
   A CLI, game, backend service, and mobile app do not share the same build, test, visual, or stress strategy.

4. **Use strict attribution when baseline/HEAD reports are comparable**  
   Block new failures, changed failure signatures, missing baseline tests, newly skipped tests, duplicate IDs, and unknown states.

5. **Treat FROZEN as a contract**  
   Accepted APIs/UI/schema/behavior are preserved until the Lead explicitly reopens them.

6. **Evidence before verdict**  
   Prefer reproducible tests, logs, diffs, machine-readable reports, and runtime captures over an agent's unsupported completion statement.

7. **No automatic “production-ready” claim**  
   Passing a lifecycle phase proves only that the agreed phase gate was satisfied. Production readiness is project-specific and depends on the actual release criteria.
