# 目标

定义 V0 中 `TripPlanRequest` 与 `TripPlan` 的最小契约，使前端表单、后端编排和结果展示共享同一组输入输出语义。

# 范围与非目标

本文件只定义用户规划请求和旅行计划结果的最小字段集合、字段语义与结构边界。它不规定 LangGraph 节点如何生成这些字段，不定义外部服务调用过程，也不展开前端页面布局、导出能力或持久化模型。V0 不在本文件支持多城市复杂规划、账号体系或历史行程存档。

# 核心契约

`TripPlanRequest` 是 V0 规划入口的唯一请求形状。最小字段应覆盖：`destination`、`start_date`、`end_date`、`preferences`、`budget_level`、`accommodation_type`。其中 `destination` 与日期区间共同定义旅行范围；`preferences` 用于影响景点与行程风格；`budget_level` 与 `accommodation_type` 用于约束预算估算和酒店推荐方向。

`TripPlan` 是 V0 规划结果的唯一输出形状。最小结果必须能独立表达一次可展示、可编辑的旅行计划，至少包含：`destination`、`days`、`weather_summary`、`budget_summary`、`map_points`。其中 `days` 是每日行程列表；每个 `day` 至少包含日期、景点列表、建议餐饮、推荐酒店或住宿说明；每个景点至少包含名称、地址、经纬度、建议停留时长和可选票价；`map_points` 必须能独立表达本次行程涉及的位置集合与基础定位信息；`budget_summary` 必须能独立表达本次旅行的预算汇总；`weather_summary` 必须能独立表达旅行期间的天气概览。

字段语义必须保持“面向产品结果”的稳定性。后续工作流、外部服务或前端实现只能消费这些字段，不得在别处重新定义同名字段的不同含义。

# 验收口径

先失败的条件是：请求缺少最小规划字段、结果缺少支撑展示与编辑所需的关键字段、同一字段在前后端被赋予不同语义，或结果结构无法独立表达单次旅行计划。通过后的可观察结果是：前端可以基于 `TripPlanRequest` 提交规划请求；后端可以返回一个足以驱动结果页的 `TripPlan`；后续工作流文档与前端交互文档只需要引用本文件定义的结构，不需要重复定义核心字段。

# 依赖与边界

本文件是 V0 数据口径的上游契约。`planner-workflow-and-state-contract.md` 依赖它来约束最终输出；`frontend-experience-and-editing-contract.md` 依赖它来约束页面展示与基础编辑；`external-service-boundary.md` 只能解释这些字段可能来自哪些服务，不得改写字段语义。本文件只对“请求和结果长什么样”负责，不对“系统如何生成这些结果”负责。
