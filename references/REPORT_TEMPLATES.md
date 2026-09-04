# Standardized Report Templates (标准汇报模板库)

## Template 1: Directive Completion Evidence Pack (批次完工证据包)

```markdown
【PROJECT LEAD DIRECTIVE CLOSEOUT REPORT】

TASK: <Task Name, e.g. ShopCapability Product Rule Implementation>
BASE SHA: <Base Git SHA>
HEAD SHA: <Current Commit SHA>
BRANCH: <Working Branch>
STATUS: IMPLEMENTED / REVIEW PENDING

==================================================
1. IMPLEMENTATION EVIDENCE (实现细节与证据)
==================================================
- Component A: <Summary of changes, class names, file paths>
- Component B: <Summary of changes, class names, file paths>
- Scope Compliance: Verified 0 unauthorized features added.

==================================================
2. AUTOMATED TEST SUITE & A/B ATTRIBUTION (测试门禁)
==================================================
- Unit / EditMode Suite:
  * Total: X | Passed: Y | Failed: Z | Skipped: S
  * HEAD-ONLY Regressions: 0 (PASSED)
- Integration / PlayMode Suite:
  * Total: X | Passed: Y | Failed: Z | Skipped: S
  * HEAD-ONLY Regressions: 0 (PASSED)
- New Tests Added: <Count> new tests, all passing:
  * [List key test names]

==================================================
3. VISUAL REVIEW EVIDENCE (实机视觉审查证据)
==================================================
- Low-Density / Mobile Base (720x1280):
  * Status: PASSED (Zero text clipping, zero button occlusion)
  * Screenshot: <Local path or URL>
- High-Density / Extended (1440x2560):
  * Status: PASSED (Zero layout breakage, safe areas respected)
  * Screenshot: <Local path or URL>

==================================================
4. FROZEN SURFACE INTEGRITY (冻结界面保护检查)
==================================================
- Certified Screens [List IDs]: Verified 0 layout modifications.

==================================================
5. RECOMMENDED NEXT TASK (建议后续任务)
==================================================
- <Concise proposal for the next directive>
```

---

## Template 2: Blocked / Escalation Report (阻塞升级报告)

```markdown
【CHIEF ENGINEER BLOCKED / ESCALATION REPORT】

TASK: <Task Name>
BLOCKING ISSUE: <Brief Title>

1. PROBLEM DESCRIPTION
- <Detailed explanation of what failed or what decision is missing>

2. EVIDENCE
- <Test output, error log, or screenshot demonstrating the conflict>

3. DECISION OPTIONS (A / B / C)
- Option A: <Description, pros & cons>
- Option B: <Description, pros & cons>

4. CURRENT ACTION
- Work halted on this component to avoid unauthorized side effects. Awaiting Lead directive.
```
