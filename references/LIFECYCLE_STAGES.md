# End-to-End Autonomous Software Engineering Lifecycle (端到端自主研发生命周期规范)

本规范定义了双 Agent 架构下，从**人类用户的一句话原始想法**到**生产级交付成品**的 5 个连续阶段。

---

## 阶段矩阵 (Lifecycle Matrix)

| 阶段 | 负责人 Lead Agent 职责 (规划 / 评审 / 决策) | 工程师 Engineer Agent 职责 (实施 / 测试 / 验证) | 阶段产出物与交付门禁 (Deliverables & Gates) |
| :--- | :--- | :--- | :--- |
| **Phase 0: 需求提炼与技术选型<br>(Discovery & Architecture)** | 1. 拆解用户一句话需求为用户故事与用例。<br>2. 拟定技术栈选型矩阵 (Web / 后端 / App / 游戏)。<br>3. 产出里程碑计划与初始数据字典。 | 1. 本地环境体检 (Node/Python/Go/Rust/Unity/Docker)。<br>2. 验证依赖网络连通性与编译器工具链。<br>3. 初始化 Git 仓库与分支规范。 | 交付物：`PROJECT_CHARTER.md`、`ARCHITECTURE.md`。<br>门禁：Lead 签发 `ARCHITECTURE_APPROVED`。 |
| **Phase 1: 最小可运行骨架<br>(Walking Skeleton & Toolchain)** | 1. 制定骨架工程规范 (项目目录、依赖版本)。<br>2. 审查工程师提交的 Hello-World / 空跑状态。 | 1. 脚手架初始化 (CLI, API Server, 或 GUI Canvas)。<br>2. 搭建自动化测试管线 (CI / 本地批处理脚本)。<br>3. 建立 Baseline 测试 XML 基准文件。 | 交付物：基础可编译代码仓库、基线测试 XML。<br>门禁：`Smoke Test = PASS`，基线 XML 固化。 |
| **Phase 2: 领域与数据层驱动<br>(Core Domain & Data Model)** | 1. 下达数据结构契约与核心计算规则 (Rulebook)。<br>2. 审查单测用例是否完全覆盖业务边缘条件。 | 1. 编写纯领域逻辑 (Domain Logic, 无第三方平台依赖)。<br>2. 编写 100% 覆盖的单元测试。<br>3. 执行 A/B 归因门禁：`HEAD-ONLY = 0`。 | 交付物：核心算法/模型、全覆盖单元测试套件。<br>门禁：`Unit Tests 100% PASS`，Lead 批准领域状态。 |
| **Phase 3: 接口与功能集成<br>(API, UI & Presentation)** | 1. 制定界面布局标准、API 契约或 CLI 命令交互流。<br>2. 通过实机截图审查 UI 或检查 API Schema。 | 1. 实现接口层、Presentation 层或 Web/UI 控件。<br>2. 运行集成测试与 E2E 流程用例。<br>3. 捕获多分辨率截图或 API 响应样本取证。 | 交付物：完整功能集成代码、Visual/API 证据。<br>门禁：Lead 签发 `COMMERCIALIZED / FROZEN`。 |
| **Phase 4: 稳定性、压测与发布<br>(Hardening, Stress & Release)** | 1. 下发长期模拟参数、压力阈值与发布检查清单。<br>2. 最终代码审查与版本 Tag 签发。 | 1. 运行长周期确定性模拟 (如 2,000 轮循环/并发压测)。<br>2. 格式化代码、清理调试桩、移除未引用素材。<br>3. 构建发布包 (Docker / WebGL / 二进制 / APK)。 | 交付物：生产级发布制品、Release Notes、最终标签。<br>门禁：Zero P0/P1 Defects，用户一键即可运行。 |

---

## 阶段流转核心原则 (Operational Tenets)

1. **单向门禁流转**：
   上一阶段未被 Lead 签发 `PASS / CLOSED` 前，工程师严禁提前编写下一阶段代码。
2. **零回归原则 (Zero Regression)**：
   任何阶段的测试必须继承前面所有阶段沉淀的测试用例。每次变更后 `HEAD-ONLY Failures` 必须严格为 0。
3. **冻结保护机制 (Frozen Freeze)**：
   一旦某一功能或 UI 被 Lead 签发为 `FROZEN`，后续阶段只能围绕其扩展，严禁倒流破坏既有排版和接口契约。
