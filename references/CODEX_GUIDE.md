# Codex / CLI Quick Start

This guide is for Codex CLI and similar local coding agents acting as the **Chief Engineer** in `dual-agent-loop`.

The workflow separates implementation from independent planning/review. It does not require the browser transport; the included CDP bridge is only one experimental option.

---

## 1. Install the skill and run its self-tests

From the target project directory:

```bash
git clone https://github.com/xulu1998/dual-agent-loop.git .agents/skills/dual-agent-loop
python -m pip install -r .agents/skills/dual-agent-loop/requirements.txt
python -m unittest discover \
  -s .agents/skills/dual-agent-loop/tests \
  -p "test_*.py" -v
```

---

## 2. Initialize durable run state

Before the first multi-batch handoff:

```bash
python .agents/skills/dual-agent-loop/scripts/run_state.py \
  --state .dual-agent-loop/run-state.json \
  init --phase phase-0 --project my-project --base-sha "$(git rev-parse HEAD)"
```

The state file records run/phase/batch/directive/SHA/evidence/verdict history so a browser or terminal restart does not force the agents to reconstruct the current batch from chat memory.

---

## 3. Optional: start the experimental CDP transport

If you choose the browser bridge, use a dedicated Chrome profile.

### macOS

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.dual-agent-loop/chrome-profile"
```

### Linux

```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/dual-agent-loop-chrome
```

### Windows PowerShell

```powershell
& "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  "--user-data-dir=$env:TEMP\dual-agent-loop-chrome"
```

Open only the intended Project Lead service in that isolated profile.

Smoke test for ChatGPT:

```bash
python .agents/skills/dual-agent-loop/scripts/chatgpt_cdp_bridge.py \
  --host chatgpt.com \
  --message "Reply with exactly: DUAL_AGENT_LOOP_OK"
```

For Claude:

```bash
python .agents/skills/dual-agent-loop/scripts/chatgpt_cdp_bridge.py \
  --host claude.ai \
  --message "Reply with exactly: DUAL_AGENT_LOOP_OK"
```

The bridge deliberately refuses to fall back to unrelated browser pages. It also waits for a response detected after the send instead of returning the previous assistant message.

CDP/DOM automation is experimental and can break when browser applications change. Check the applicable third-party service policies and prefer an approved API/MCP/integration when required by your environment.

---

## 4. Start Codex / your local coding agent

A practical launch instruction is:

```text
Read .agents/skills/dual-agent-loop/SKILL.md and act as the Chief Engineer.

Before doing new work:
1. inspect the repository and local toolchain;
2. read or initialize .dual-agent-loop/run-state.json;
3. confirm the current phase, batch, directive, BASE SHA, and previous verdict;
4. use the configured Project Lead transport to request/receive a bounded directive;
5. persist the directive before modifying code;
6. implement only the current batch scope;
7. run project-specific build/test/integration/runtime checks;
8. when comparable baseline/HEAD XML exists, run the strict regression attribution gate;
9. persist HEAD SHA and evidence artifacts;
10. send the evidence-backed report to the Project Lead;
11. persist the Lead verdict before advancing.

Do not self-approve the product and do not silently delete/skip tests to make a gate pass.
```

---

## 5. Strict regression gate

The gate is stricter than `HEAD-ONLY failures = 0` alone.

It blocks:

```text
new failures
changed failure signatures
missing baseline tests
newly skipped tests
duplicate test identifiers
unknown test states
```

Example:

```bash
python .agents/skills/dual-agent-loop/scripts/compare_attribution.py \
  --baseline artifacts/baseline.xml \
  --head artifacts/head.xml \
  --base-sha "$(git rev-parse <baseline-ref>)" \
  --head-sha "$(git rev-parse HEAD)" \
  --runner "<runner/version>" \
  --json artifacts/attribution.json
```

A baseline failure is non-blocking only if the same test still exists and its captured failure signature is unchanged.

Try the repository's reproducible fixture first:

```bash
python .agents/skills/dual-agent-loop/scripts/compare_attribution.py \
  --baseline .agents/skills/dual-agent-loop/examples/regression_gate_demo/baseline.xml \
  --head .agents/skills/dual-agent-loop/examples/regression_gate_demo/head-good.xml
```

---

## 6. Typical batch flow

```text
Project Lead
  ↓ bounded directive
run-state ledger records directive + BASE SHA
  ↓
Chief Engineer implements
  ↓
real project checks + strict attribution + runtime evidence
  ↓
run-state ledger records HEAD SHA + evidence
  ↓
Project Lead review
  ↓
PASS / REJECT / BLOCKED / CLOSED
  ↓
run-state ledger records verdict
  ↺
```

The state ledger is intentionally simple. It improves recovery and traceability but is not yet a full autonomous orchestrator.

---

## Security

- Use a dedicated Chrome profile for CDP.
- Do not expose the debugging port to untrusted networks.
- Never allow the bridge to fall back to arbitrary tabs.
- Treat authenticated browser content as sensitive.
- Only automate services/accounts you are authorized to automate.
- Check applicable third-party terms/policies.

See `SECURITY.md` for details.
