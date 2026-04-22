# B 首批交付清单

本文档给 `B` 使用。目标是尽快给 `A` 一套可并行开发的稳定 contract，而不是等后端全部做完。

## 第一优先级

- 冻结第一版 `TripPlanRequest`
- 冻结第一版 `TripPlan`
- 冻结第一版 `EditRequest`
- 明确关键嵌套模型的字段与含义
- 保证 `OpenAPI/Swagger` 可访问

## 必须先交给 A 的产物

- 一份可访问的 `OpenAPI/Swagger`
- 2 到 3 个稳定的 `TripPlan` 示例 JSON
- `TripPlanRequest` 示例请求体
- `EditRequest` 示例请求体
- 错误响应的最小约定

## 示例 JSON 必须覆盖这些内容

- 行程概览
- 地图点位
- 预算明细
- 天气信息
- 每日行程
- 编辑后返回结果
- 若后续要做图片展示，需要包含图片相关字段
- 若后续要做导出，需要包含导出所依赖字段

## 你主要改这些位置

- `trip_planner/api.py`
- `trip_planner/workflow.py`
- `trip_planner/models/`
- `tests/test_api.py`
- `tests/test_workflow.py`
- `tests/test_service_boundary.py`

## 你需要优先说清楚的事情

- 哪些字段是稳定字段
- 哪些字段还可能变化
- 哪些字段是前端只读消费
- 哪些字段是编辑接口要回传的
- 导出是否需要额外接口或额外字段
- 图片补全是否写回 `TripPlan`

## Swagger 该怎么用

- 用它固定 HTTP 请求和响应
- 用它固定字段名、必填项、字面量取值
- 不要指望它表达内部工作流节点或 LangGraph 状态
- 每次共享字段改动后，先更新 `OpenAPI`，再通知 `A`

## 你不要晚到最后才做的事情

- 示例 JSON
- 错误响应约定
- 图片字段约定
- 导出相关字段约定
- 编辑接口参数约定

## 你的第一轮完成标准

- `A` 已经可以不依赖你后续实现，直接基于你给的 contract 开发页面
- `OpenAPI` 能解释清楚前端如何请求和如何消费结果
- 示例 JSON 足够覆盖结果页主要区块
- 共享字段变更有通知机制，不会静默破坏前端
