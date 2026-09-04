# Universal Project Initializer & Templates (通用项目初始化与适配指南)

本指南指导工程师 Agent 如何根据 Project Lead 的架构指令，对不同领域的编程项目建立起**自动化测试与验证骨架**。

---

## 1. Web 全栈项目 (Next.js / React / Vue + Node.js / FastAPI / Go)

### 验证管线标准：
- **测试框架**：`vitest` / `jest` / `pytest`
- **E2E 与视觉审查**：`playwright` (无头浏览器模式，支持直接截图 720×1280 与 1440×2560)
- **A/B 归因门禁命令示例**：
  ```bash
  # 运行并生成 JUnit 格式测试结果
  npm test -- --reporter=junit --outputFile=builds/head-tests.xml
  
  # A/B 门禁对比
  python3 scripts/compare_attribution.py --baseline builds/baseline-tests.xml --head builds/head-tests.xml --strict
  ```
- **Playwright 视觉截图规范**：
  ```javascript
  // 自动化视觉审查脚本 (e.g. tests/visual.spec.ts)
  await page.setViewportSize({ width: 720, height: 1280 });
  await page.screenshot({ path: 'builds/screen-720x1280.png' });
  await page.setViewportSize({ width: 1440, height: 2560 });
  await page.screenshot({ path: 'builds/screen-1440x2560.png' });
  ```

---

## 2. 后端服务与微服务 (Go / Rust / Python / Java Spring)

### 验证管线标准：
- **测试框架**：`go test` / `cargo test` / `pytest`
- **长期压测与模拟**：`k6` / `locust` / 自动化内存与并发死锁检测
- **输出标准**：通过 `go-junit-report` 或 `cargo2junit` 转换为通用 XML 进行 A/B 比对。
- **验证命令示例**：
  ```bash
  # Go 示例
  go test -v ./... | go-junit-report > builds/head-tests.xml
  python3 scripts/compare_attribution.py --baseline builds/baseline-tests.xml --head builds/head-tests.xml --strict
  ```

---

## 3. CLI 命令行与系统级工具 (Rust / C++ / Python / Go)

### 验证管线标准：
- **CLI 行为测试**：针对标准输入、标准输出、退出码、异常参数编写确定性集成用例。
- **多平台验证**：针对跨平台文件路径、终端宽度做格式适配检查。

---

## 4. 客户端与游戏 (Unity / Tuanjie / Unreal / Godot / Flutter)

### 验证管线标准：
- **无头批量模式 (Headless Batchmode)**：
  - Unity / Tuanjie: `-batchmode -runTests -testPlatform EditMode/PlayMode`
  - Godot: `--headless --run-tests`
- **实机分辨率取证**：
  通过 `ScreenCapture.CaptureScreenshot` 在标准分辨率下采样，保存至 `builds/` 供 Lead 审查。
