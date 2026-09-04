---
name: dual-agent-loop
description: >-
  Universal end-to-end software engineering operating system for an autonomous dual-agent pair (Project Lead + Chief Engineer).
  Covers the full lifecycle from a single-sentence user idea to production-ready delivery: project planning & architecture,
  walking skeleton bootstrapping, pure domain implementation, interface/UI integration, A/B baseline regression test gates
  (HEAD-ONLY = 0), multi-resolution visual evidence, and autonomous CDP reporting.
  Supports ALL software domains: Web full-stack, Backend APIs & microservices, CLI/Systems tools, Mobile apps, and Games.
---

# Universal Dual-Agent Engineering Loop (通用端到端双 Agent 闭环研发系统)

This skill operationalizes a production-grade, universal dual-agent pair programming workflow for **ANY software engineering project**—from a one-line prompt to a fully validated, production-ready deliverable.

It coordinates an external **Project Lead Agent** (planning, architecture, requirements decomposition, visual/code review, acceptance gates) and a local **Chief Engineer Agent** (toolchain bootstrapping, minimal implementation, automated batch test execution, A/B regression attribution, and CDP reporting).

本技能是一套**面向所有编程领域（Web全栈、后端服务、CLI工具、移动端App、游戏研发）**的通用端到端自主研发操作系统。它将“用户一句话描述”无缝转化为生产级成品：外部端（ChatGPT/Claude）负责全局规划与严格验收，本地端（Antigravity/CLI）负责脚手架构建、编码实施、双门禁测试与实机取证，实现两端自主闭环、全流程免人工测试。

---

## 1. Universal Architecture (通用双 Agent 架构)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Project Lead Agent (ChatGPT / Claude Web)                       │
│   • Phase 0: Refines user idea -> Charter, Tech Stack & Architecture                  │
│   • Phase 1-4: Issues Batch Directives (Strict Goal, Non-goals, Acceptance Criteria)   │
│   • Reviews Public Code, Automated Test Diffs, and Multi-resolution Visuals           │
│   • Authorizes Phase Transitions & Grants FROZEN / PASS / CLOSED status                │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ ▲
               1. Directive (Batch Scope)   │ │ 6. Evidence Pack via CDP Bridge
                                            ▼ │    (scripts/chatgpt_cdp_bridge.py)
┌───────────────────────────────────────────┴────────────────────────────────────────────┐
│                        Chief Engineer Agent (Antigravity / Local CLI)                  │
│   • Scope & Rules Guard: Enforces zero scope creep, locks Base SHA                     │
│   • Universal Toolchain: Sets up build/test framework (Web / Backend / CLI / Game)     │
│   • Minimal Implementation: Pure domain logic isolated from presentation / frameworks  │
│   • A/B Regression Gate: Batch execution comparing against Baseline XML                │
│     (Mathematical Gate: HEAD-ONLY Failures == 0)                                       │
│   • Visual / Runtime Evidence: Multi-resolution headless browser / engine screenshots  │
│   • Git & Autonomous Delivery: Commits, pushes to branch, dispatches CDP report        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The 5 End-to-End Lifecycle Phases (端到端五阶段研发生命周期)

| 阶段 (Phase) | Project Lead 职责 (规划与验收) | Chief Engineer 职责 (实施与测试) | 交付物与流转门禁 (Deliverables & Gates) |
| :--- | :--- | :--- | :--- |
| **Phase 0: 需求提炼与架构设计<br>(Charter & Architecture)** | 拆解用户一句话为功能清单、技术选型（Web/Go/Python/Unity 等）与数据契约。 | 校验本地工具链（Node/Go/Python/Docker/Compiler）、初始化代码仓库与基线配置。 | 产出 `PROJECT_CHARTER.md` & `ARCHITECTURE.md`。<br>门禁：Lead 签发 `ARCHITECTURE_APPROVED`。 |
| **Phase 1: 最小可运行骨架<br>(Walking Skeleton)** | 确立骨架结构、目录组织与初始 Smoke 验收标准。 | 搭建最小可运行 Hello-World，接入自动化测试管线，生成首版 Baseline 测试 XML。 | 产出基础可编译代码与基准测试结果。<br>门禁：`Smoke Test = PASS`，基线 XML 固化。 |
| **Phase 2: 领域与数据层驱动<br>(Core Domain & Data Logic)** | 制定业务规则书（Rulebook）、算法边界与单测覆盖标准。 | 编写纯领域逻辑（无平台耦合），编写全覆盖单元测试，运行 A/B 归因门禁。 | 核心逻辑代码与单测套件。<br>门禁：`Unit Tests 100% PASS`，`HEAD-ONLY = 0`。 |
| **Phase 3: 接口与界面集成<br>(API, Presentation & UI)** | 拟定 API Schema、CLI 交互流或 UI 布局设计规范。 | 实现接口层 / UI 视图，运行集成测试，捕获多分辨率实机截图（Web/App/Game）。 | 完整集成应用、实机截图取证包。<br>门禁：Lead 审查截图/API，签发 `COMMERCIALIZED / FROZEN`。 |
| **Phase 4: 压测、加固与发布<br>(Hardening, Stress & Release)** | 下发压测参数（如 2,000 轮循环 / 并发压测）与发布检查清单。 | 执行长周期确定性模拟或并发测试，代码整洁加固，构建最终发布二进制/容器。 | 生产级发布包、Release Notes、最终 Tag。<br>门禁：Zero P0/P1 缺陷，用户一键即可运行。 |

---

## 3. The 6-Step Autonomous Loop (日常批次标准 6 步闭环)

1. **Directive Locking (指令接收与边界锁定)**:
   记录 `BASE SHA`、目标范围、禁止项（Non-goals）与明确验收条件。
2. **Rules & Contract Check (规则书与冻结保护检查)**:
   核对业务契约；检查涉及的既有 UI/API 是否处于 `FROZEN` 保护状态，绝不擅自破坏排版。
3. **Minimal Implementation (最小化实现)**:
   编写纯领域与业务逻辑，不添加未授权的未来设计，严禁反向耦合第三方平台。
4. **A/B Test Gate (自动化双门禁与 A/B 归因)**:
   批量运行测试并与 Baseline XML 比对（使用 `scripts/compare_attribution.py`），**强制 `HEAD-ONLY Failures == 0`**。
5. **Visual / Runtime Proof (多分辨率实机取证)**:
   对 UI 相关的项目，自动采样移动端基线（如 `720×1280`）与高密度屏（如 `1440×2560`）实机渲染截图，验证无截断重叠。
6. **Git Push & CDP Reporting (自主提交与交付)**:
   提交并推送到 GitHub，通过 `scripts/chatgpt_cdp_bridge.py` 自动化将结构化证据包投递给 Project Lead，等待裁决。

---

## 4. Universal Project Tooling Guide (通用工具链与参考手册)

- **CDP 通信网关**: [scripts/chatgpt_cdp_bridge.py](./scripts/chatgpt_cdp_bridge.py)
  支持全自动与网页端 ChatGPT / Claude 通信，无需第三方 API Token。
- **A/B 归因门禁工具**: [scripts/compare_attribution.py](./scripts/compare_attribution.py)
  通用 NUnit / JUnit / Jest / Vitest / Go / Pytest XML 结果对比，数学级证明零回归。
- **多分辨率视觉校验**: [scripts/capture_screen.py](./scripts/capture_screen.py)
  支持 Web (Playwright/Puppeteer)、移动端与游戏引擎截图的尺寸与排版审计。
- **研发生命周期详细规程**: [references/LIFECYCLE_STAGES.md](./references/LIFECYCLE_STAGES.md)
- **多技术栈适配指南 (Web/后端/CLI/游戏)**: [references/PROJECT_INITIALIZER.md](./references/PROJECT_INITIALIZER.md)
- **标准汇报与升级模板**: [references/REPORT_TEMPLATES.md](./references/REPORT_TEMPLATES.md)
- **真实交付证据包示例**: [examples/sample_report.md](./examples/sample_report.md)
