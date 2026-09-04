---
name: dual-agent-loop
description: >-
  End-to-end dual-agent software engineering workflow for a Project Lead + Chief Engineer pair.
  Covers requirements refinement, architecture, walking-skeleton bootstrapping, domain implementation,
  interface/UI integration, baseline-vs-HEAD regression attribution gates (HEAD-ONLY = 0),
  visual evidence handling, and CDP-based reporting. Designed to adapt across web, backend,
  CLI, mobile, and game projects with project-specific tooling.
---

# Dual-Agent Engineering Loop

This skill operationalizes a **reviewable dual-agent software engineering workflow** from an initial product idea through implementation, evidence collection, review gates, and release preparation.

It coordinates:

- an external **Project Lead Agent** (planning, architecture, requirements decomposition, review, acceptance gates), and
- a local **Chief Engineer Agent** (repository inspection, bounded implementation, automated test execution, regression attribution, evidence collection, and CDP reporting).

The intent is not to claim that one workflow automatically solves every software project. The lifecycle is designed to generalize across web, backend, CLI, mobile, and game development, while each project still supplies the correct stack-specific build, test, screenshot, packaging, and release tools.

本技能是一套**双 Agent 闭环软件研发工作流**。Project Lead 负责需求、架构和验收；Chief Engineer 负责仓库修改、测试、证据收集和汇报。它可以适配 Web、后端、CLI、移动端和游戏等项目，但具体工具链与验收门禁必须根据真实项目技术栈配置。

---

## 1. Dual-Agent Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 Project Lead Agent (ChatGPT / Claude Web)                  │
│  • Refines requirements and architecture                                  │
│  • Defines bounded directives and acceptance criteria                      │
│  • Reviews tests, logs, diffs, screenshots, and other evidence            │
│  • Approves, rejects, freezes, or reopens surfaces                         │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │ ▲
                 Directive / Review  │ │ Evidence Pack via CDP
                                     ▼ │
┌────────────────────────────────────┴────────────────────────────────────────┐
│                  Chief Engineer Agent (Local Coding Agent)                 │
│  • Inspects repository and toolchain                                       │
│  • Locks batch scope and BASE SHA                                           │
│  • Implements the smallest compliant change                                │
│  • Runs project-appropriate automated checks                               │
│  • Computes baseline-vs-HEAD regression attribution                         │
│  • Collects runtime / visual evidence                                       │
│  • Reports results through the CDP bridge                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Five Lifecycle Phases

| Phase | Project Lead | Chief Engineer | Typical gate |
| --- | --- | --- | --- |
| **0. Charter & Architecture** | Refine scope, constraints, architecture, contracts, acceptance criteria | Inspect repository, environment, available tooling | Architecture and scope approved |
| **1. Walking Skeleton** | Define the first runnable milestone | Build the smallest runnable skeleton and establish test baseline | Smoke path works and baseline is captured |
| **2. Domain Logic** | Define business rules and edge cases | Implement bounded domain logic behind testable boundaries | Required domain tests pass; HEAD-ONLY regressions = 0 |
| **3. Presentation & Integration** | Define API / CLI / UI acceptance criteria | Integrate presentation layers and collect runtime evidence | Integration/visual evidence reviewed |
| **4. Hardening & Release** | Define project-specific hardening and release checklist | Run appropriate stress/simulation/package/release checks | No unresolved release-blocking defects |

Do not force identical hardening methods across unrelated project types. For example, a CLI, mobile app, web service, and game may require very different Phase 4 evidence.

---

## 3. Standard Batch Loop

1. **Directive Locking**  
   Record the current BASE SHA, batch goal, explicit non-goals, affected surfaces, and acceptance criteria.

2. **Contract / Freeze Check**  
   Identify whether the batch touches an accepted or `FROZEN` interface, UI surface, schema, or behavior.

3. **Minimal Implementation**  
   Implement only what the current directive requires. Avoid speculative abstractions or unrelated refactors unless necessary for correctness.

4. **Automated Verification + Regression Attribution**  
   Run the project-specific test command. When baseline and HEAD test reports are available, use `scripts/compare_attribution.py` and require:

   ```text
   HEAD-ONLY Failures = Failures(HEAD) - Failures(Baseline) = 0
   ```

   The included parser handles common NUnit-style and JUnit-style XML. Jest, Vitest, Pytest, or other runners can participate when configured to emit compatible JUnit XML.

5. **Runtime / Visual Evidence**  
   For UI or visual projects, use the project's actual runtime tooling to capture screenshots at relevant target sizes. Then use `scripts/capture_screen.py` to inspect image dimensions and format evidence references.

6. **Git + CDP Report**  
   Commit/push according to the target repository's workflow, create an evidence-backed report, and send it to the Project Lead using `scripts/chatgpt_cdp_bridge.py`. Await the Lead's review before declaring the whole project complete.

---

## 4. Tooling

- **CDP bridge** — [`scripts/chatgpt_cdp_bridge.py`](./scripts/chatgpt_cdp_bridge.py)  
  Sends text to a browser-based ChatGPT / Claude conversation and reads the resulting response through Chrome DevTools Protocol. Browser DOM changes can require selector updates.

- **Regression attribution** — [`scripts/compare_attribution.py`](./scripts/compare_attribution.py)  
  Compares baseline and HEAD test reports and identifies newly introduced failures. Supports common NUnit/JUnit-style XML; other runners should emit compatible JUnit XML.

- **Screenshot evidence inspector** — [`scripts/capture_screen.py`](./scripts/capture_screen.py)  
  Inspects existing screenshot dimensions and formats evidence references. It does **not** itself launch Playwright, Puppeteer, mobile emulators, or game engines; the target project should provide the real capture mechanism.

- **Lifecycle details** — [`references/LIFECYCLE_STAGES.md`](./references/LIFECYCLE_STAGES.md)
- **Project initialization guidance** — [`references/PROJECT_INITIALIZER.md`](./references/PROJECT_INITIALIZER.md)
- **Workflow specification** — [`references/WORKFLOW_SPEC.md`](./references/WORKFLOW_SPEC.md)
- **Report templates** — [`references/REPORT_TEMPLATES.md`](./references/REPORT_TEMPLATES.md)
- **Codex / CLI guide** — [`references/CODEX_GUIDE.md`](./references/CODEX_GUIDE.md)
- **Example evidence packet** — [`examples/sample_report.md`](./examples/sample_report.md)

---

## 5. CDP Safety Requirements

When using the browser bridge:

1. Launch Chrome with a **dedicated `--user-data-dir`**.
2. Do not attach the workflow to your everyday Chrome profile.
3. Do not expose the CDP port to untrusted networks.
4. Only connect trusted local agents and scripts.
5. Treat authenticated browser content, cookies, and chat history as sensitive.

See [`SECURITY.md`](./SECURITY.md) and the root [`README.md`](./README.md) for current Chrome 136+ launch examples.
