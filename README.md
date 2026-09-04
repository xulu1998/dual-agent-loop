# Universal Dual-Agent Engineering Loop (通用端到端双 Agent 闭环研发系统)

[English](#english-overview) | [简体中文](#简体中文介绍)

---

## 简体中文介绍

`dual-agent-loop` 是一个为**全品类软件工程项目（Web全栈、后端微服务、系统CLI工具、移动端应用、数字游戏）**设计的通用端到端双 Agent 自主研发生命周期操作系统与技能包（Antigravity / Claude Code Skill）。

### 🌟 核心理念：从“用户一句话描述”到“高质量交付成品”
在传统单 Agent 模式下，代码模型极易出现“脑补过度”、“破坏既有结构”、“缺乏客观测试就谎称已完成”的问题。
本系统将软件生命周期完整拆分，由 **双端分工协作** 驱动：
- **Project Lead（项目负责人 / ChatGPT / Claude 网页端）**：主管**产品规划、技术选型、架构拆解、实机审查与门禁验收**。
- **Chief Engineer（首席工程师 / Antigravity / 本地终端）**：主管**环境体检、脚手架搭建、纯领域编码、批处理自动化测试与 CDP 汇报**。

二者通过 **Chrome DevTools Protocol (CDP)** 建立本地到浏览器的无缝直连，实现无需人工充当传话筒、全流程自驱动的闭环工程流。

---

### 🔄 端到端 5 大生命周期阶段 (The 5 Lifecycle Phases)

```
[ 用户一句话想法 ]
        │
        ▼
Phase 0: 需求提炼与技术选型 (Charter & Architecture)
  • Lead: 拆解需求 -> 功能规范、技术栈选择 (Web/Go/Rust/Python/Unity)、数据契约
  • Engineer: 本地环境诊断、Git 仓库初始化 -> 签发 ARCHITECTURE_APPROVED
        │
        ▼
Phase 1: 最小可运行骨架 (Walking Skeleton & Pipeline)
  • Engineer: 搭建最小可运行工程、配置 CI/自动化测试套件、生成首版 Baseline XML
  • Lead: 审查骨架与初始 Smoke 结果 -> 固化 Baseline
        │
        ▼
Phase 2: 领域模型与数据层驱动 (Domain Logic & Unit Tests)
  • Lead: 明确业务规则书 (Rulebook)、核心计算公式与边界条件
  • Engineer: 纯领域逻辑实现 (零第三方耦合) + 100% 单测覆盖 + A/B 归因测试 (HEAD-ONLY=0)
        │
        ▼
Phase 3: 接口与界面呈现集成 (API, Presentation & UI)
  • Lead: 下达 API Schema、CLI 交互或 UI 视觉设计标准
  • Engineer: 实现 UI / 接口层、E2E 集成测试、双分辨率实机截图取证 (720p & 2K)
  • Lead: 审查实机截图 -> 签发 COMMERCIALIZED / FROZEN 保护状态
        │
        ▼
Phase 4: 压测、加固与打包发布 (Hardening, Sim & Production Release)
  • Lead: 下发长周期模拟 / 并发压测指标与发布清单
  • Engineer: 2,000 轮确定性模拟 / 负载压测、代码加固、产出最终 Release 制品
        │
        ▼
[ 生产就绪的完整可用制品 ]
```

---

### 🛡️ 工程师行为准则与门禁红线 (Golden Rules)

1. **数学级零回归门禁 (Strict A/B Attribution Gate)**：
   测试结果绝不允许仅靠肉眼粗看。每次修改后，自动解析当前测试 XML 与基准 XML 进行差集计算：
   $$\text{HEAD-ONLY Failures} = \text{Failures}(\text{HEAD}) \setminus \text{Failures}(\text{Baseline}) = 0$$
   只要当前分支引入了哪怕 1 个新失败，门禁立即熔断，必须修复。
2. **冻结界面与契约不可侵犯 (Frozen Protection)**：
   一旦某一功能或页面被 Lead 签发为 `FROZEN`，后续开发中严禁破坏其排版、尺寸和既有交互。
3. **真实多分辨率实机取证 (Visual Review)**：
   涉及 UI 的项目（Web、App、游戏），必须由脚本自动采样移动端基准屏（如 720×1280）与长屏/高分屏（如 1440×2560）截图，杜绝文字溢出、截断与遮挡。
4. **拒绝任何人工测试负担**：
   凡是能通过代码、日志、单元测试、E2E、无头仿真证明的事情，绝不让用户手工去点去测。

---

## English Overview

`dual-agent-loop` is an end-to-end autonomous software engineering operating system and skill package for **ANY software domain** (Web full-stack, backend APIs, systems CLI tools, mobile apps, and video games).

It operationalizes an autonomous pair-programming loop between:
- **Project Lead Agent** (in Chrome browser via ChatGPT / Claude Web UI): Handles requirements refinement, system architecture, batch directive issuance, visual inspection, and final signoff.
- **Chief Engineer Agent** (in local terminal via Antigravity / Claude Code / Codex): Handles repository setup, pure domain coding, batch automated test suites, mathematical A/B attribution gates (`HEAD-ONLY = 0`), multi-resolution visual sampling, and autonomous CDP reporting.

Both agents communicate bi-directionally through the **Chrome DevTools Protocol (CDP)** over WebSockets without extra API token overhead.

---

## 目录结构 (Directory Structure)

```text
dual-agent-loop/
├── SKILL.md                          # Antigravity Skill 标准规范入口
├── README.md                         # 详细中英双语使用手册
├── LICENSE                           # MIT License
├── scripts/
│   ├── chatgpt_cdp_bridge.py        # Chrome 远程调试 WebSocket 双端通信网关
│   ├── compare_attribution.py       # 通用 NUnit/JUnit/Jest/Vitest/Pytest A/B 归因门禁工具
│   └── capture_screen.py            # 实机视觉取证与多分辨率尺寸分析工具
├── references/
│   ├── LIFECYCLE_STAGES.md          # 端到端 5 阶段研发生命周期详细规程
│   ├── PROJECT_INITIALIZER.md       # 多技术栈项目初始化与适配指南 (Web/后端/CLI/游戏)
│   ├── WORKFLOW_SPEC.md             # 详细 SOP 工程规范与角色边界
│   └── REPORT_TEMPLATES.md          # 完工汇报与阻塞升级标准模板
└── examples/
    └── sample_report.md             # 真实工业级项目证据包范例
```

---

## 快速上手 (Quick Start)

### 1. 启动 Chrome 远程调试端口

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &

# Linux
google-chrome --remote-debugging-port=9222 &

# Windows
chrome.exe --remote-debugging-port=9222
```
并在打开的 Chrome 中登录 ChatGPT 或 Claude，打开对应项目的对话窗口。

### 2. 作为技能安装使用 (Install Skill)

在任意目标项目的工作区中克隆即可（Antigravity 会自动发现并装载）：

```bash
git clone https://github.com/xulu1998/dual-agent-loop.git .agents/skills/dual-agent-loop
```

### 3. 一句话启动端到端项目循环

你只需要对你的工程师 Agent 说：
> *“请激活 `dual-agent-loop` 技能。我们的项目想法是：[描述你的一句话想法]。请通过 CDP 连接 Chrome 中的 Project Lead，从 Phase 0 需求与架构规划开始，推进端到端闭环研发。”*

两端 Agent 将自动开始：
1. **Lead** 梳理产品方案与架构，生成 `PROJECT_CHARTER.md`；
2. **Engineer** 建立本地脚手架与自动化测试流水线；
3. **循环推进** 纯领域逻辑、UI/接口集成与全自动门禁比对；
4. 直至 **Phase 4** 产出通过全部测试与视觉审查的成品代码库。

---

## 开源协议 (License)

本项目基于 [MIT License](./LICENSE) 开源。欢迎 Star、Fork 并根据团队工作流定制！
