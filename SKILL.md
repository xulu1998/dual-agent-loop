---
name: dual-agent-loop
description: >-
  Standard Operating Procedure (SOP) and automation toolkit for an autonomous dual-agent software engineering loop.
  Coordinates a Project Lead Agent (e.g., ChatGPT / Claude web via Chrome DevTools Protocol) and an Engineer Agent (e.g., Antigravity / Claude Code / Codex).
  Enforces directive-locking, minimal implementations, automated batch test gates with A/B baseline attribution (HEAD-ONLY = 0), multi-resolution visual evidence capture, and CDP-based autonomous reporting.
  Use this skill whenever setting up or running multi-agent pair programming, hierarchical agent collaboration, or headless game/app test automation.
---

# Dual-Agent Engineering Loop (双 Agent 闭环研发工作流)

This skill operationalizes a production-grade, hierarchical dual-agent pair programming workflow. It coordinates an external **Project Lead Agent** (decision-maker, external reviewer) and a local **Chief Engineer Agent** (implementer, test runner, evidence gatherer) connected via Chrome DevTools Protocol (CDP).

本项目技能封装了一套经过工业级项目验证的高效双 Agent（负责人 + 首席工程师）闭环协作工作流，通过 CDP（Chrome 开发者协议）打通外部审查端与本地执行端，实现全自动指令接收、最小实现、A/B 归因门禁测试、多分辨率视觉取证与自主闭环汇报。

---

## Architecture Overview (架构总览)

```
┌────────────────────────────────────────────────────────────────────────┐
│            Project Lead Agent (ChatGPT / Claude Web UI)                │
│   • Issues Batch Directives (Goal, Non-goals, Acceptance Gates)        │
│   • Reviews Public Code, Test Diffs, and Multi-resolution Visuals      │
│   • Grants PASS / REWORK / FROZEN / CLOSED status                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ ▲
        1. Directive (Batch Scope)  │ │ 6. Evidence Pack via CDP Bridge
                                    ▼ │    (scripts/chatgpt_cdp_bridge.py)
┌───────────────────────────────────┴────────────────────────────────────┐
│            Chief Engineer Agent (Antigravity / Local CLI)              │
│   • Rules & Scope Guard: Zero scope creep, lock base commit SHA        │
│   • Minimal Implementation: Pure domain logic, no platform coupling   │
│   • Automated Test Gate: Batchmode execution, A/B baseline delta       │
│     (Strict gate: HEAD-ONLY Failures == 0)                             │
│   • Visual Evidence: Multi-resolution headless/playmode screenshots    │
│   • Git & Reporting: Atomic commit, push, and CDP bridge delivery      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## The 6-Step Loop Execution Guide (6 步标准循环执行指南)

### Step 1: Directive Locking (指令接收与边界锁定)
1. Read the Project Lead's directive.
2. Record `BASE SHA`, `GOAL`, `NON-GOALS`, and explicit `ACCEPTANCE CRITERIA`.
3. Verify if any protected/frozen assets (e.g. frozen UI layouts, core APIs) are touched. If risk of breaking frozen surfaces exists, halt immediately and request clarification.

### Step 2: Rules & Contract Verification (规则书与契约校验)
1. Check domain rulebooks and reference matrices before touching code.
2. Confirm domain constraints (e.g. data-driven numbers, zero hardcoded magic constants, platform decoupling).
3. Confirm localization/internationalization rules (e.g. China-first simplified Chinese rules, RMB currency symbols).

### Step 3: Minimal Implementation (最小化可验证实现)
1. Implement only the exact scope authorized by the directive.
2. Separate pure domain logic from presentation or engine framework layers.
3. Write unit test cases verifying each new rule and edge case.

### Step 4: Automated Test Gate & A/B Baseline Attribution (双门禁测试与 A/B 归因)
Run headless batch tests and compare the output XML against the base commit XML using [compare_attribution.py](./scripts/compare_attribution.py):
- **EditMode / Unit Tests**: Fast domain verification.
- **PlayMode / Integration Tests**: Lifecycle and state persistence verification.
- **Strict Acceptance Gate**:
  - `HEAD-ONLY Failures` MUST equal **0**.
  - Any pre-existing baseline failures must have matching signatures in the baseline XML.

### Step 5: Multi-Resolution Visual Review (多分辨率视觉取证)
For UI-impacting tasks, capture automated screenshots at standard screen ratios (e.g., `720×1280` and `1440×2560`) using [capture_screen.py](./scripts/capture_screen.py) or in-engine screenshot routines:
- Verify no clipping, overflow, missing assets, or button occlusion.
- Store artifacts and provide paths/URLs in the final report.

### Step 6: Git Push & CDP Autonomous Reporting (提交推送与 CDP 自动化汇报)
1. Commit with standard conventional commits: `feat:`, `fix:`, `docs:`, `test:`.
2. Push to remote working branch: `git push origin <branch>`.
3. Send the structured evidence report to the Lead using [chatgpt_cdp_bridge.py](./scripts/chatgpt_cdp_bridge.py).
4. Await the Lead's verdict (`PASS / CLOSED` or `REWORK`).

---

## Bundled Tools & Scripts (附带自动化脚本)

- **[scripts/chatgpt_cdp_bridge.py](./scripts/chatgpt_cdp_bridge.py)**:
  Python WebSocket client interacting with Chrome DevTools Protocol (`port 9222`) to inspect ChatGPT/Claude tabs, submit text reports, and stream back lead responses.
- **[scripts/compare_attribution.py](./scripts/compare_attribution.py)**:
  NUnit/JUnit XML diffing utility. Computes `HEAD-ONLY` vs `Baseline-Only` failure deltas to enforce zero-regression gates.
- **[scripts/capture_screen.py](./scripts/capture_screen.py)**:
  Cross-platform screenshot and visual verification helper.

---

## Reference Manuals (参考文档)
- [references/WORKFLOW_SPEC.md](./references/WORKFLOW_SPEC.md): Comprehensive dual-agent SOP, role definitions, and failure handling.
- [references/REPORT_TEMPLATES.md](./references/REPORT_TEMPLATES.md): Standardized report schemas for discovery, implementation closeout, and blocked escalations.
- [examples/sample_report.md](./examples/sample_report.md): Real-world evidence report example from an engine game project.
