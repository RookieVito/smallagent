# Trip Assistant V0 Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the V0 stage docs for the trip assistant under `阶段/`, covering the full frontend-backend loop with V0 acceptance limited to generation, presentation, and basic itinerary editing.

**Architecture:** The implementation creates two index pages under `阶段/索引页/V0/` and five contract-style design docs under `阶段/设计文档/V0/`. The index pages provide guided reading paths only, while the design docs become the single source of truth for request/response shape, LangGraph workflow boundaries, frontend interaction boundaries, external service boundaries, and V0 acceptance rules.

**Tech Stack:** Markdown documentation, relative intra-project links, LangChain `1.2.15`, LangGraph `1.1.8`

---

### Task 1: Create the planning-path index and backend-facing contracts

**Files:**
- Create: `阶段/索引页/V0/1_规划闭环与数据契约.md`
- Create: `阶段/设计文档/V0/trip-request-and-plan-contract.md`
- Create: `阶段/设计文档/V0/planner-workflow-and-state-contract.md`
- Reference: `docs/superpowers/specs/2026-04-18-trip-assistant-v0-doc-design.md`
- Reference: `模仿/0_模板说明.md`
- Reference: `智能旅行助手.md`

- [ ] **Step 1: Write `阶段/索引页/V0/1_规划闭环与数据契约.md`**

```markdown
**默认仅允许编辑状态标识；若发生目录迁移、文件重命名或模板升级，可同步更新链接与说明文字。**

# 规划闭环与数据契约

本索引页只负责“从用户请求到结构化规划结果”的阅读路径，不展开前端展示、外部服务降级或阶段验收细节。

1. [trip-request-and-plan-contract.md](../../设计文档/V0/trip-request-and-plan-contract.md)：`未开始`
2. [planner-workflow-and-state-contract.md](../../设计文档/V0/planner-workflow-and-state-contract.md)：`未开始`
```

- [ ] **Step 2: Write `阶段/设计文档/V0/trip-request-and-plan-contract.md`**

```markdown
# 目标

定义 V0 中 `TripPlanRequest` 与 `TripPlan` 的最小契约，使前端表单、后端编排和结果展示共享同一组输入输出语义。

# 范围与非目标

本文件只定义用户规划请求和旅行计划结果的最小字段集合、字段语义与结构边界。它不规定 LangGraph 节点如何生成这些字段，不定义外部服务调用过程，也不展开前端页面布局、导出能力或持久化模型。V0 不在本文件支持多城市复杂规划、账号体系或历史行程存档。

# 核心契约

`TripPlanRequest` 是 V0 规划入口的唯一请求形状。最小字段应覆盖：`destination`、`start_date`、`end_date`、`preferences`、`budget_level`、`accommodation_type`。其中 `destination` 与日期区间共同定义旅行范围；`preferences` 用于影响景点与行程风格；`budget_level` 与 `accommodation_type` 用于约束预算估算和酒店推荐方向。

`TripPlan` 是 V0 规划结果的唯一输出形状。最小结果必须能支持前端展示与基础编辑，至少包含：`destination`、`days`、`weather_summary`、`budget_summary`、`map_points`。其中 `days` 是每日行程列表；每个 `day` 至少包含日期、景点列表、建议餐饮、推荐酒店或住宿说明；每个景点至少包含名称、地址、经纬度、建议停留时长和可选票价；`map_points` 必须能支撑地图标记与基础重渲染；`budget_summary` 必须能支撑预算卡片展示；`weather_summary` 必须能支撑结果页天气摘要展示。

字段语义必须保持“面向产品结果”的稳定性。后续工作流、外部服务或前端实现只能消费这些字段，不得在别处重新定义同名字段的不同含义。

# 验收口径

先失败的条件是：请求缺少最小规划字段、结果缺少支撑展示与编辑所需的关键字段、同一字段在前后端被赋予不同语义，或结果结构无法独立表达单次旅行计划。通过后的可观察结果是：前端可以基于 `TripPlanRequest` 提交规划请求；后端可以返回一个足以驱动结果页的 `TripPlan`；后续工作流文档与前端交互文档只需要引用本文件定义的结构，不需要重复定义核心字段。

# 依赖与边界

本文件是 V0 数据口径的上游契约。`planner-workflow-and-state-contract.md` 依赖它来约束最终输出；`frontend-experience-and-editing-contract.md` 依赖它来约束页面展示与基础编辑；`external-service-boundary.md` 只能解释这些字段可能来自哪些服务，不得改写字段语义。本文件只对“请求和结果长什么样”负责，不对“系统如何生成这些结果”负责。
```

- [ ] **Step 3: Write `阶段/设计文档/V0/planner-workflow-and-state-contract.md`**

```markdown
# 目标

定义基于 `langchain==1.2.15` 与 `langgraph==1.1.8` 的 V0 规划工作流边界，使景点检索、天气查询、酒店推荐与行程整合能够在统一状态流中协作，并最终产出 `TripPlan`。

# 技术栈

- `langchain==1.2.15`
- `langgraph==1.1.8`

# 范围与非目标

本文件只定义 V0 规划工作流的最小节点集合、共享状态边界和最终整合责任。它不展开具体 prompt、模型选择细节、重试策略实现、服务端模块结构或前端 API 路由细节。V0 不在本文件引入多代理自治协商、长期记忆、持久线程恢复或复杂并行调度。

# 核心契约

V0 工作流必须围绕统一的规划状态运行。该状态至少包含：标准化后的用户请求、候选景点信息、天气信息、酒店信息、规划草案和最终 `TripPlan`。工作流的最小节点集合为：请求标准化、景点检索、天气查询、酒店推荐、规划整合。前四个节点负责补齐规划素材，规划整合节点负责结合用户原始偏好与素材信息生成最终结果。

节点责任必须单一。景点检索只负责产出候选景点及其展示所需字段；天气查询只负责产出旅行期天气摘要；酒店推荐只负责产出住宿候选；规划整合只负责把这些信息收敛为 `TripPlan`，并确保结果满足上游输入输出契约。允许实现层选择顺序执行或有限并行，但不能让节点越权改写彼此的责任范围。

工作流的完成条件是成功写入最终 `TripPlan`。若关键节点失败且无法形成可展示结果，则本次规划失败；若非关键增强信息缺失但主链路仍可完成，则允许降级为缺少增强字段的结果。

# 验收口径

先失败的条件是：工作流缺少最小节点集合、节点之间没有共享状态口径、最终结果不是由统一整合节点产出、或工作流无法稳定映射到 `TripPlan`。通过后的可观察结果是：V0 规划链路可以用明确的状态传递描述；每个节点的输入输出边界清晰；后续实现可以直接用 LangGraph 映射这些节点，而不需要重新发明职责划分。

# 依赖与边界

本文件依赖 `trip-request-and-plan-contract.md` 中的请求与结果字段定义。`external-service-boundary.md` 负责解释各节点依赖哪些外部能力；`frontend-experience-and-editing-contract.md` 只消费最终 `TripPlan`，不直接感知节点内部状态。本文件只对“工作流如何最小化组织”负责，不对“节点内部如何调用模型或服务”负责。
```

- [ ] **Step 4: Run structure checks for Task 1 docs**

Run: `rtk rg -n '^# ' 阶段/索引页/V0/1_规划闭环与数据契约.md 阶段/设计文档/V0/trip-request-and-plan-contract.md 阶段/设计文档/V0/planner-workflow-and-state-contract.md`
Expected: headings for one index page and two five-section design docs, plus one `技术栈` section in the workflow doc

- [ ] **Step 5: Commit Task 1**

```bash
git add 阶段/索引页/V0/1_规划闭环与数据契约.md 阶段/设计文档/V0/trip-request-and-plan-contract.md 阶段/设计文档/V0/planner-workflow-and-state-contract.md
git commit -m "docs: add V0 planning path contracts"
```

### Task 2: Create the interaction-path index and frontend contract

**Files:**
- Create: `阶段/索引页/V0/2_应用交互与集成边界.md`
- Create: `阶段/设计文档/V0/frontend-experience-and-editing-contract.md`
- Reference: `docs/superpowers/specs/2026-04-18-trip-assistant-v0-doc-design.md`
- Reference: `智能旅行助手.md`

- [ ] **Step 1: Write `阶段/索引页/V0/2_应用交互与集成边界.md`**

```markdown
**默认仅允许编辑状态标识；若发生目录迁移、文件重命名或模板升级，可同步更新链接与说明文字。**

# 应用交互与集成边界

本索引页只负责“如何把规划结果变成用户可用闭环”的阅读路径，不重复展开规划工作流或请求输出字段的正文。

1. [frontend-experience-and-editing-contract.md](../../设计文档/V0/frontend-experience-and-editing-contract.md)：`未开始`
2. [external-service-boundary.md](../../设计文档/V0/external-service-boundary.md)：`未开始`
3. [v0-acceptance-and-non-goals.md](../../设计文档/V0/v0-acceptance-and-non-goals.md)：`未开始`
```

- [ ] **Step 2: Write `阶段/设计文档/V0/frontend-experience-and-editing-contract.md`**

```markdown
# 目标

定义 V0 前端闭环体验的最小契约，使用户能够完成规划请求输入、结果浏览、地图查看、预算查看和基础行程编辑。

# 范围与非目标

本文件只定义前端 V0 的页面职责、结果页必须覆盖的展示板块和基础编辑边界。它不展开组件库选型、样式系统、动效设计、导出交互、用户登录或持久化保存。V0 不在本文件支持跨天重排、复杂拖拽规划、多人协同编辑或离线缓存。

# 核心契约

前端 V0 至少包含两个核心页面角色：规划输入页与结果展示页。规划输入页必须允许用户填写目的地、出发日期、结束日期、偏好、预算等级和住宿偏好，并将这些字段映射为 `TripPlanRequest`。结果展示页必须至少展示：行程概览、预算摘要、地图标记、每日行程与天气摘要。

基础编辑能力只允许对已生成结果做局部调整。最小允许操作为：删除单日中的景点、调整同一天内景点顺序、保存修改并刷新页面展示结果。基础编辑不能要求用户重新触发完整规划工作流，也不能隐式扩展为跨天移动景点、重新推荐酒店或重新估算整条路线。

前端必须以 `TripPlan` 为唯一结果输入源。任何展示组件都应消费统一结果字段，不能在页面层重新发明另一套结果结构。

# 验收口径

先失败的条件是：前端缺少最小输入页或结果页、结果页无法覆盖地图或预算展示、基础编辑超出已确认边界、或页面依赖未在 `TripPlan` 中定义的隐藏字段。通过后的可观察结果是：用户能发起规划请求；结果页能完整展示 V0 所需信息；用户能执行局部编辑并看到结果刷新；前端交互边界不会误导实现层提前支持导出或复杂重排。

# 依赖与边界

本文件依赖 `trip-request-and-plan-contract.md` 中定义的输入输出字段。地图、图片等外部依赖是否为必需能力由 `external-service-boundary.md` 约束；整体阶段通过标准由 `v0-acceptance-and-non-goals.md` 统一定义。本文件只对“用户能看到和编辑什么”负责，不对“结果从哪里来”负责。
```

- [ ] **Step 3: Run structure checks for Task 2 docs**

Run: `rtk rg -n '^# ' 阶段/索引页/V0/2_应用交互与集成边界.md 阶段/设计文档/V0/frontend-experience-and-editing-contract.md`
Expected: one index page title and one five-section design doc

- [ ] **Step 4: Commit Task 2**

```bash
git add 阶段/索引页/V0/2_应用交互与集成边界.md 阶段/设计文档/V0/frontend-experience-and-editing-contract.md
git commit -m "docs: add V0 interaction path docs"
```

### Task 3: Create service-boundary and acceptance docs

**Files:**
- Create: `阶段/设计文档/V0/external-service-boundary.md`
- Create: `阶段/设计文档/V0/v0-acceptance-and-non-goals.md`
- Reference: `docs/superpowers/specs/2026-04-18-trip-assistant-v0-doc-design.md`
- Reference: `智能旅行助手.md`
- Reference: `requirements.txt`

- [ ] **Step 1: Write `阶段/设计文档/V0/external-service-boundary.md`**

```markdown
# 目标

定义 V0 规划闭环中外部服务的责任边界，使实现层能够区分主链路依赖、结果增强依赖和可降级依赖。

# 范围与非目标

本文件只定义外部服务在 V0 中承担的角色、失败影响和降级边界。它不展开各平台 API 参数、密钥配置、服务注册步骤或 SDK 封装细节。V0 不在本文件承诺导出服务、持久化数据库服务或额外的第三方内容供应商。

# 核心契约

V0 的外部依赖至少分为三类：LLM 推理能力、地图与地点类服务、可选结果增强服务。LLM 推理能力是规划主链路依赖，用于整合行程与生成结构化结果；地图与地点类服务是主链路依赖，用于提供景点、酒店和地理坐标等规划素材；图片增强等可选服务属于结果增强依赖，只用于提升展示完整性，不得成为主流程成功的前提。

主链路依赖失败时，系统允许失败返回，但不得伪造完整规划结果。增强依赖失败时，允许降级为缺少图片或附加素材的 `TripPlan`，只要核心展示字段仍然完整。外部服务只能为既有契约字段提供数据，不得引入未在上游文档确认的新核心字段。

# 验收口径

先失败的条件是：主链路与增强依赖没有被区分、可选能力被错误提升为硬依赖、或外部服务结果直接扩展了未定义的核心结构。通过后的可观察结果是：实现层清楚哪些服务缺失会阻断规划、哪些服务缺失可以降级；前后端可以围绕统一结果结构处理外部依赖成功与失败。

# 依赖与边界

本文件依赖 `trip-request-and-plan-contract.md` 中的结果结构，以及 `planner-workflow-and-state-contract.md` 中的节点职责。`frontend-experience-and-editing-contract.md` 只消费最终结果，不直接约束服务调用。本文件只对“外部能力在系统中扮演什么角色”负责，不对“如何实现这些调用”负责。
```

- [ ] **Step 2: Write `阶段/设计文档/V0/v0-acceptance-and-non-goals.md`**

```markdown
# 目标

统一定义智能旅行助手 V0 的通过标准与明确非目标，避免实现阶段把未确认能力混入本阶段闭环。

# 范围与非目标

本文件只定义 V0 是否通过的统一标准，以及哪些能力明确留给后续阶段。它不重复定义请求输出字段、工作流节点或页面交互细节。V0 不在本文件展开实现计划、测试矩阵或阶段排期。

# 核心契约

智能旅行助手 V0 的目标是实现“前后端完整闭环”，并将能力范围严格限制在“生成 + 展示 + 基础编辑”。通过标准至少包括：用户能够提交结构化旅行请求；后端能够基于 LangGraph 工作流生成 `TripPlan`；前端能够展示行程概览、预算、地图、每日行程和天气摘要；用户能够对单日景点做删除与顺序调整，并在保存后看到页面刷新结果。

以下能力明确不属于 V0 验收范围：PDF 导出、图片导出、地图导出兼容性最终方案、多城市复杂规划、持久化保存、账号体系、复杂协同编辑、跨天重排与自动重规划。实现层可以为后续阶段保留扩展点，但不得把这些能力写成 V0 必须通过的标准。

# 验收口径

先失败的条件是：阶段目标被扩展到导出或复杂规划、基础编辑被误写为复杂重排、或前后端闭环缺失任一核心环节。通过后的可观察结果是：所有 V0 设计文档都围绕同一组阶段边界表述；后续实现和评审可以直接用本文件判断是否越界。

# 依赖与边界

本文件依赖其他四篇设计文档提供的具体契约，但不替代它们的细节定义。它是 V0 范围判断的统一兜底文档，负责在出现冲突时优先收敛范围，而不是继续扩展能力。本文件只对“这一阶段做到哪里算完成”负责，不对“每部分如何实现”负责。
```

- [ ] **Step 3: Run structure checks for Task 3 docs**

Run: `rtk rg -n '^# ' 阶段/设计文档/V0/external-service-boundary.md 阶段/设计文档/V0/v0-acceptance-and-non-goals.md`
Expected: two five-section design docs

- [ ] **Step 4: Commit Task 3**

```bash
git add 阶段/设计文档/V0/external-service-boundary.md 阶段/设计文档/V0/v0-acceptance-and-non-goals.md
git commit -m "docs: add V0 boundary and acceptance docs"
```

### Task 4: Verify link integrity, scope consistency, and repo-local conventions

**Files:**
- Verify: `阶段/索引页/V0/1_规划闭环与数据契约.md`
- Verify: `阶段/索引页/V0/2_应用交互与集成边界.md`
- Verify: `阶段/设计文档/V0/trip-request-and-plan-contract.md`
- Verify: `阶段/设计文档/V0/planner-workflow-and-state-contract.md`
- Verify: `阶段/设计文档/V0/frontend-experience-and-editing-contract.md`
- Verify: `阶段/设计文档/V0/external-service-boundary.md`
- Verify: `阶段/设计文档/V0/v0-acceptance-and-non-goals.md`

- [ ] **Step 1: Verify the index pages point to the expected design docs**

Run: `rtk rg -n '\]\(\.\./\.\./设计文档/V0/' 阶段/索引页/V0/*.md`
Expected: both index pages reference the five design docs via relative links only

- [ ] **Step 2: Verify all design docs keep the expected section structure**

Run: `rtk rg -n '^# (目标|范围与非目标|核心契约|验收口径|依赖与边界|技术栈)$' 阶段/设计文档/V0/*.md`
Expected: every design doc has the five required sections; only the workflow doc may include `技术栈`

- [ ] **Step 3: Verify the V0 scope is consistent across all docs**

Run: `rtk rg -n '生成 \+ 展示 \+ 基础编辑|PDF 导出|图片导出|多城市复杂规划|持久化|跨天重排' 阶段/设计文档/V0/*.md`
Expected: acceptance doc names the non-goals explicitly, and no other doc contradicts that boundary

- [ ] **Step 4: Verify the new docs do not use machine-local absolute paths in their body text**

Run: `rtk rg -n '/home/xia' 阶段/索引页/V0 阶段/设计文档/V0`
Expected: no matches

- [ ] **Step 5: Commit Task 4**

```bash
git add 阶段/索引页/V0/1_规划闭环与数据契约.md 阶段/索引页/V0/2_应用交互与集成边界.md 阶段/设计文档/V0/trip-request-and-plan-contract.md 阶段/设计文档/V0/planner-workflow-and-state-contract.md 阶段/设计文档/V0/frontend-experience-and-editing-contract.md 阶段/设计文档/V0/external-service-boundary.md 阶段/设计文档/V0/v0-acceptance-and-non-goals.md
git commit -m "docs: verify V0 stage documentation set"
```
