# Codex / CLI 快速上手指南

本指南面向使用 **Codex CLI** 或其他本地终端编码 Agent 的用户。目标不是让一个 Agent 同时负责“规划 + 编码 + 自我验收”，而是让本地 Chief Engineer 与浏览器端 Project Lead 建立明确的双角色闭环。

---

## 1. 准备独立 Chrome Profile 并开启 CDP

`dual-agent-loop` 通过 Chrome DevTools Protocol (CDP) 让本地 Agent 与浏览器中的 ChatGPT / Claude 会话通信。

> **Chrome 136+ 必须注意：** 不要只使用 `--remote-debugging-port=9222` 启动默认 Chrome Profile。请同时指定一个独立的 `--user-data-dir`。这既符合新版 Chrome 的远程调试行为，也能避免把日常浏览器会话直接暴露给本地自动化。

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

启动后，在这个**独立 Profile** 中登录 ChatGPT 或 Claude，并打开作为 Project Lead 的会话。

---

## 2. 安装 Skill 与依赖

在目标项目目录中执行：

```bash
git clone https://github.com/xulu1998/dual-agent-loop.git .agents/skills/dual-agent-loop
python -m pip install -r .agents/skills/dual-agent-loop/requirements.txt
```

如果你的 Agent 不使用 `.agents/skills/`，也可以克隆到其他目录，只要它能够读取 `SKILL.md`。

---

## 3. 先做一次 CDP Smoke Test

### ChatGPT

```bash
python .agents/skills/dual-agent-loop/scripts/chatgpt_cdp_bridge.py \
  --pattern chatgpt.com \
  --message "Reply with exactly: DUAL_AGENT_LOOP_OK"
```

### Claude

```bash
python .agents/skills/dual-agent-loop/scripts/chatgpt_cdp_bridge.py \
  --pattern claude.ai \
  --message "Reply with exactly: DUAL_AGENT_LOOP_OK"
```

如果终端收到了浏览器 Agent 的回复，说明传输链路已经工作。

---

## 4. 启动 Codex / CLI Agent

进入项目目录并启动你的本地编码 Agent，例如：

```bash
codex
```

然后粘贴下面的启动指令，并替换项目想法：

```text
请读取 .agents/skills/dual-agent-loop/SKILL.md。

你现在扮演 Chief Engineer（首席工程师）。
浏览器中已有一个 Project Lead 会话，通过 Chrome CDP 9222 端口与其通信。

项目想法：
【在这里写你的一句话需求】

从 Phase 0 开始：
1. 先检查当前仓库和本地环境；
2. 通过 dual-agent-loop/scripts/chatgpt_cdp_bridge.py 把项目想法和环境摘要发送给 Project Lead；
3. 请求 Project Lead 输出清晰的 Charter、架构约束和第一个 bounded batch directive；
4. 收到 Directive 后，只实现当前批次范围；
5. 运行相应测试、回归归因和证据收集；
6. 将结果通过 CDP 汇报给 Project Lead；
7. 未经 Project Lead 验收，不自行宣布整个项目完成。
```

---

## 5. 接下来会发生什么

典型闭环如下：

```text
Project Lead
  ↓ 需求 / 架构 / Directive
Chief Engineer
  ↓ 修改仓库
Tests / Logs / Screenshots
  ↓
Regression attribution / Evidence packet
  ↓
Project Lead review
  ↓
PASS / REJECT / FREEZE / Next Directive
  ↺
```

### Phase 0 — Charter & Architecture

Lead 负责明确需求、范围、约束、架构和验收标准。Engineer 负责环境与仓库体检。

### Phase 1 — Walking Skeleton

Engineer 建立最小可运行骨架、测试入口和基线；Lead 审查是否满足首个可运行里程碑。

### Phase 2 — Domain Logic

核心业务逻辑优先建立清晰边界与自动化测试。每个批次都要避免引入新的 HEAD-only failure。

### Phase 3 — Presentation & Integration

接入 UI / API / CLI 层，并提交实际运行证据。涉及视觉界面时，应由项目自身工具生成截图，再使用仓库中的证据工具检查尺寸和整理报告。

### Phase 4 — Hardening & Release

根据项目类型执行性能、仿真、发布和打包检查。并不是所有项目都需要完全相同的压测方法，应以 Project Lead 在 Phase 0/4 下达的验收标准为准。

---

## 安全提醒

CDP 可以访问当前浏览器会话中 Agent 能够看到和操作的内容，因此：

- 只使用独立 Chrome Profile；
- 不要使用日常主 Profile；
- 不要把 9222 端口暴露到不可信网络；
- 只让你信任的本地 Agent 和脚本连接；
- 将登录状态、Cookies、聊天内容视为敏感数据。

更多说明见仓库根目录的 `SECURITY.md`。
