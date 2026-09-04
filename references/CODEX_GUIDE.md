# Codex / CLI 快速上手指南 (Quickstart Guide for Codex Users)

本指南面向使用 **Codex (CLI)** 或任意第三方终端 Agent 的新用户。你只需要准备好本地环境，给出**一句话需求**，Codex 就会接管本地工程并与浏览器端的 Project Lead (ChatGPT / Claude) 自动闭环完成项目。

---

## 步骤 1：启动带远程调试端口的 Chrome 浏览器

本工作流通过 Chrome 原生调试协议 (CDP) 让本地 Codex 操控浏览器，无需购买任何第三方额外 API Token。

在终端中执行命令启动 Chrome：

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &

# Linux
google-chrome --remote-debugging-port=9222 &

# Windows (PowerShell)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

> **注意**：启动后，在弹出的 Chrome 浏览器中打开 [ChatGPT](https://chatgpt.com) 或 [Claude](https://claude.ai)，进入一个新的会话窗口即可。

---

## 步骤 2：安装依赖与技能

在你的项目根目录执行：

```bash
# 1. 安装 CDP 通信所需的轻量依赖
pip install websockets

# 2. 将技能克隆到你的项目目录下
git clone https://github.com/xulu1998/dual-agent-loop.git dual-agent-loop
```

---

## 步骤 3：启动 Codex 并一句话下达启动指令

进入项目目录并启动 Codex：

```bash
cd my-new-project
codex
```

在 Codex 中直接粘贴以下**启动提示词**（将最后一句话替换为你自己的想法）：

```text
请阅读并加载当前目录下的 dual-agent-loop/SKILL.md。
你现在扮演 Chief Engineer（首席工程师），协助我开发项目。

请按照 dual-agent-loop 的 5 阶段研发规范执行：
1. 运行 dual-agent-loop/scripts/chatgpt_cdp_bridge.py 连接 Chrome 端口 9222 上的 Project Lead。
2. 告诉 Project Lead 我们要做的项目一句话想法是：
   【在这里写你的一句话想法，例如：用 React + FastAPI 做一个自动解析账单并生成可视化图表的全栈网站】
3. 请 Project Lead 启动 Phase 0 需求提炼与架构规划，并下达首个 Batch Directive。
4. 收到指令后，严格遵守最小实现原则、A/B 归因门禁 (HEAD-ONLY = 0) 与 CDP 自动汇报，开始推进！
```

---

## 接下来会发生什么？（你完全不需要做任何繁琐工作）

1. **自动握手**：
   Codex 会执行桥接脚本，通过 WebSocket 把你的想法直接打入 Chrome 里的 ChatGPT/Claude 输入框并回车发送。
2. **Phase 0 架构规划**：
   网页端的 Lead 会拆解出一套完整的技术选型、目录结构、数据模型和里程碑，并通过脚本返回给 Codex。
3. **Phase 1 骨架构建**：
   Codex 在本地初始化工程脚手架（如 Vite/FastAPI/Go/Rust 等），配好自动化测试，运行出初始基线 XML。
4. **Phase 2~3 核心编码与实机验证**：
   Codex 编写核心逻辑与 UI 界面，运行全自动单测比对（保证新引入失败数为 0），捕获无头实机截图，把证据提交给 Lead 审查。
5. **Phase 4 交付**：
   经过 Lead 的逐批次严格验收与签发，最终交付给你一个生产级、跑通所有自动化测试的完整项目！
