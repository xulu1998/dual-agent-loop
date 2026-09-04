# Project Initializer and Verification Adapters

This guide shows how a Chief Engineer can map `dual-agent-loop` onto different software stacks. The workflow is shared; the actual build/test/runtime tools remain project-specific.

## 1. Web applications

Typical tools:

- unit/integration: Vitest / Jest / Pytest / framework-native runner
- E2E/visual capture: Playwright / Puppeteer
- regression attribution: configure the test runner to emit JUnit-compatible XML

Example:

```bash
npm test -- --reporter=junit --outputFile=artifacts/head-tests.xml
python scripts/compare_attribution.py \
  --baseline artifacts/baseline-tests.xml \
  --head artifacts/head-tests.xml \
  --base-sha <BASE_SHA> \
  --head-sha <HEAD_SHA> \
  --runner "vitest" \
  --json artifacts/attribution.json
```

Example Playwright capture (the target project owns the capture code):

```javascript
await page.setViewportSize({ width: 720, height: 1280 });
await page.screenshot({ path: 'artifacts/screen-720x1280.png' });
```

Use target sizes that matter to the real application; 720×1280 / 1440×2560 are examples, not universal requirements.

## 2. Backend services

Typical tools:

- Go: `go test`, optionally converted with `go-junit-report`
- Rust: `cargo test` plus a JUnit adapter when attribution is required
- Python: `pytest --junitxml=...`
- Java: native JUnit XML from Maven/Gradle test tooling
- load/stress: k6, Locust, project-specific harnesses

The strict attribution gate blocks more than new failures. It also blocks missing baseline tests, new skips, changed failure signatures, duplicate IDs, and unknown states.

## 3. CLI / systems tools

Verification should cover the behavior that matters to the CLI:

- stdout/stderr
- exit codes
- invalid arguments
- filesystem side effects
- cross-platform paths/encodings where relevant
- deterministic integration scenarios

If the runner can emit JUnit/NUnit-family XML, it can feed the attribution gate. If not, use native project checks and record their evidence rather than inventing unsupported XML.

## 4. Mobile / game projects

Examples:

- Unity / Tuanjie: batchmode test execution and engine-owned screenshot capture
- Godot: project-supported headless testing/runtime capture
- Flutter: `flutter test` / integration_test with project-specific reporting
- native mobile: platform test runners and emulator/device evidence

The repository's `capture_screen.py` does not launch engines or emulators. It only inspects screenshot files already produced by the target project's real tooling.

## 5. Baseline discipline

Before relying on regression attribution:

1. record the actual baseline Git SHA;
2. generate the baseline report from that designated state;
3. keep the baseline XML/hash as evidence;
4. generate HEAD with equivalent runner configuration;
5. include runner/version when possible;
6. do not delete or skip tests to reduce blocker counts.

For a self-contained example, run `examples/regression_gate_demo/`.
