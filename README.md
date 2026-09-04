# Dual-Agent Engineering Loop (双 Agent 闭环研发工作流)

[English](#english-overview) | [简体中文](#简体中文介绍)

---

## 简体中文介绍

`dual-agent-loop` 是一个为自主软件工程设计的**高可靠双 Agent 协同工作流与技能包（Antigravity / Claude Code Skill）**。

在复杂工程实践中，单一 Agent 容易发生幻觉、越权实现未规划功能、因小改动引发全局测试雪崩、或陷入无效重复改动。本工作流将职责严格拆分为两个角色，并通过 **CDP（Chrome 开发者工具协议）** 打通二者之间的自动化通信：

### 核心角色分工

| 角色 | 载体 | 职责与权限 |
| :--- | :--- | :--- |
| **Project Lead<br>(项目负责人)** | 浏览器端（ChatGPT / Claude Web） | **最高决策与审查权威**：下发阶段批次指令（明确目标、禁止项、验收准则），通过 GitHub 审查代码和实机截图，签发 `PASS / CLOSED` 状态。 |
| **Chief Engineer<br>(首席工程师)** | 本地终端（Antigravity / Claude Code / Codex） | **最小实现与自动化验证执行者**：严格遵守指令范围做最小实现，无头模式运行自动化测试，执行 A/B 归因门禁（`HEAD-ONLY = 0`），多分辨率实机截图取证，并通过 CDP 自动向 Lead 汇报。 |

### 6 步标准闭环 (The Loop)

```
1. 接收并锁定指令 (Directive Lock: Base SHA, Goal, Non-goals)
                    │
                    ▼
2. 规则与红线检查 (Rulebook, AGENTS.md, 冻结界面保护)
                    │
                    ▼
3. 最小可验证实现 (Minimal Implementation: 领域逻辑优先，无平台耦合)
                    │
                    ▼
4. 双门禁自动化验证 (Batchmode Tests + A/B 归因: HEAD-ONLY Failures == 0)
                    │
                    ▼
5. 多分辨率视觉取证 (720x1280 & 1440x2560 实机截图，无遮挡溢出)
                    │
                    ▼
6. Git Push & CDP 自动汇报 (提交到 GitHub，通过 WebSocket 向 Lead 交付证据包)
```

---

## English Overview

`dual-agent-loop` is an enterprise-grade autonomous pair-programming skill for agents (Antigravity, Claude Code, Codex). It orchestrates an external **Project Lead Agent** (decision-maker & reviewer) and a local **Chief Engineer Agent** (implementer & test runner) connected directly via Chrome DevTools Protocol (CDP).

### Key Features
- **Hierarchical Governance**: Decouples design and acceptance from execution.
- **CDP Bridge**: Autonomous communication between local CLI agents and browser-based AI chats (ChatGPT / Claude) without third-party API costs.
- **A/B Baseline Regression Attribution**: Enforces strict mathematical test gates:
  $$\text{HEAD-ONLY Failures} = \text{Failures}(\text{HEAD}) \setminus \text{Failures}(\text{Baseline}) = 0$$
- **Visual Review Gates**: Multi-resolution screenshot verification (e.g. mobile 720×1280 and high-DPI 1440×2560) to protect frozen/certified UI layouts.
- **Progressive Skill Design**: Compatible with the Antigravity Customization Specification (`SKILL.md`).

---

## 目录结构 (Directory Structure)

```text
dual-agent-loop/
├── SKILL.md                          # Antigravity Skill 标准定义入口
├── README.md                         # 中英文完整使用说明
├── LICENSE                           # MIT License
├── scripts/
│   ├── chatgpt_cdp_bridge.py        # Chrome 远程调试 WebSocket 桥接脚本
│   ├── compare_attribution.py       # NUnit/JUnit XML A/B 归因分析门禁工具
│   └── capture_screen.py            # 实机视觉取证与多分辨率校验工具
├── references/
│   ├── WORKFLOW_SPEC.md             # 详细 SOP 工程规范与角色定义
│   └── REPORT_TEMPLATES.md          # 完工汇报与阻塞升级标准模板
└── examples/
    └── sample_report.md             # 真实商业游戏项目中的证据包示例
```

---

## 快速开始 (Quick Start)

### 1. 启动 Chrome 远程调试 (Launch Chrome with Remote Debugging)

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &

# Linux
google-chrome --remote-debugging-port=9222 &

# Windows
chrome.exe --remote-debugging-port=9222
```
并在浏览器中打开 ChatGPT 或 Claude 对应项目的会话标签页。

### 2. 作为 Antigravity Skill 安装 (Install as a Skill)

将此仓库克隆或添加到你的 Agent 技能目录中：

```bash
# 项目级技能 (Workspace Skill)
git clone https://github.com/xulu1998/dual-agent-loop.git .agents/skills/dual-agent-loop

# 或者全局技能 (Global Customization)
git clone https://github.com/xulu1998/dual-agent-loop.git ~/.gemini/config/skills/dual-agent-loop
```

### 3. 使用脚本工具 (Using the CLI Tools)

#### A. 发送完工报告并等待决策 (Submit Report & Await Directive)
```bash
python3 scripts/chatgpt_cdp_bridge.py --file my_report.md
```

#### B. 执行自动化测试 A/B 归因门禁 (A/B Test Regression Gate)
```bash
python3 scripts/compare_attribution.py \
  --baseline builds/baseline-tests.xml \
  --head builds/current-tests.xml \
  --strict
```

---

## 开源许可证 (License)

本项目采用 [MIT License](./LICENSE)。
