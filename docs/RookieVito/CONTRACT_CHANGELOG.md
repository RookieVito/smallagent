# Contract Changelog

> 记录所有可能影响前端（A）的字段变更。每次变更后 B 必须更新本文档并通知 A。

---

## v0.1.0 (2026-04-24) — 初始 contract 冻结

### 新增
- `TripPlanRequest`：行程规划请求体（6 个字段）
- `TripPlan`：完整旅行计划响应体（8 个字段）
- `EditRequest`：行程编辑请求体（5 个字段）
- `Attraction.image_url`：景点图片 URL（当前为 null）
- `DayPlan.cover_image_url`：每日封面图 URL（当前为 null）
- `TripPlan.cover_image_url`：行程封面图 URL（当前为 null）
- `TripPlan.created_at`：计划创建时间
- `TripPlan.plan_version`：版本号（编辑时递增）

### 强类型化
- `WeatherSummary.daily_forecasts`：`list[dict]` → `list[DailyForecast]`
- `BudgetSummary.breakdown`：`dict[str, Decimal]` → `BudgetBreakdown`

### 错误响应
- 统一错误格式：`{error_code, message, details}`
- `VALIDATION_ERROR`（422）：请求参数验证失败
- `PLAN_FAILED`（503）：主链路服务不可用

### API 端点
- `POST /api/trip/plan`：创建旅行计划
- `POST /api/trip/edit`：编辑旅行计划（delete_attraction / move_attraction）
- `GET /health`：健康检查

### 实验性字段（可能变更）
- `cover_image_url`（TripPlan、DayPlan、Attraction）：图片补全完成后稳定，之前可能重命名
