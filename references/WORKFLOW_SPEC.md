# Dual-Agent Engineering Loop Specification (双 Agent 闭环工程规范)

## 1. Principles & Roles (角色划分与原则)

### 1.1 Project Lead Agent (项目负责人 / 决策与评审端)
- **Authority**: Holds product design authority, scope authority, and frozen UI certification authority.
- **Access Model**: Typically runs in a browser session (ChatGPT Plus / Team / Claude Pro). Has access to GitHub remote repo (commits, files, PRs) and images uploaded or linked.
- **Responsibilities**:
  - Issues unambiguous batch directives with clear GOAL, NON-GOALS, and ACCEPTANCE GATES.
  - Reviews automated test evidence and multi-resolution screenshots.
  - Marks feature phases and UI screens as `COMMERCIALIZED / FROZEN`.
  - Signs off on rulebook updates with `PASS / CLOSED`.

### 1.2 Chief Engineer Agent (首席工程师 / 实现与验证端)
- **Authority**: Local workspace coding, headless engine execution, test runner, git author.
- **Access Model**: Runs locally via Antigravity / Claude Code / Codex CLI with terminal, file edit, and process execution capabilities.
- **Responsibilities**:
  - Minimal implementation: implements only what the directive specifies; no scope creep.
  - Zero-regression test enforcement: runs full batch test suites and enforces `HEAD-ONLY = 0`.
  - Visual proof: captures real runtime screenshots across minimum (e.g. 720x1280) and high-density (e.g. 1440x2560) viewports.
  - Delivers structured evidence packs to the Lead via CDP bridge.

---

## 2. A/B Regression Attribution Gate (A/B 归因门禁机制)

In long-running legacy or fast-iterating codebases, some pre-existing tests may fail. The Engineer Agent must NEVER ignore failures or falsely claim 100% pass without evidence. Instead, use mathematical A/B attribution:

$$\text{Regressions} = \text{Failures}(\text{HEAD}) \setminus \text{Failures}(\text{Baseline})$$

1. **Baseline XML**: Test results generated from the designated `BASE SHA`.
2. **HEAD XML**: Test results generated from the current working tree.
3. **HEAD-ONLY Failures**: Must be **EXACTLY 0**. Any failure that did not exist in the baseline is a blocker.
4. **Identical Failures**: Failures with matching stack traces/messages present in both runs are proven pre-existing and do not block the current batch.

---

## 3. UI Protection & Frozen Surface Rules (冻结界面保护红线)

1. Any screen, dialog, or UI component signed off as `COMMERCIALIZED / FROZEN` must not have its layout, anchor presets, font sizes, or asset bindings modified.
2. If new domain features require text updates on a frozen screen (e.g. detailed appraisal feedback, error messages):
   - The engineer must verify text fits within existing text bounding boxes.
   - If text clipping or overflow occurs, the engineer MUST NOT alter the UI layout; instead, halt and report a layout capacity escalation to the Lead.

---

## 4. Communication Protocol (Chrome DevTools Protocol)

The bridge utilizes Chrome DevTools Protocol (`--remote-debugging-port=9222`):
- Connects via WebSocket to the target LLM tab (`ws://127.0.0.1:9222/devtools/page/<ID>`).
- Submits reports directly into the DOM input field (`Runtime.evaluate`).
- Dispatches Enter or clicks the Send button.
- Periodically polls the assistant message element until generation finishes.
- Emits the complete Project Lead directive to stdout for immediate consumption by the engineer agent.
