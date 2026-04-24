# B 首批交付 — 实施计划

> 目标：尽快给 A 一套可并行开发的稳定 contract，不依赖后端后续实现。

---

## 现状评估

| 模型 | 状态 | 备注 |
|------|------|------|
| `TripPlanRequest` | **已冻结** | 6 个字段，全部稳定 |
| `TripPlan` | **已冻结** | 8 个顶层字段，含图片/导出字段 |
| `EditRequest` | **已冻结** | 5 个字段，已迁移到 `models/edit.py` |
| `WeatherSummary.daily_forecasts` | **已强类型化** | `list[DailyForecast]` |
| `BudgetSummary.breakdown` | **已强类型化** | `BudgetBreakdown` |
| OpenAPI/Swagger | **已完善** | 18 schemas，含中文描述和标签 |
| 示例 JSON | **已交付** | 3 个 TripPlan + 请求/编辑/错误示例 |
| 错误响应约定 | **已统一** | `ErrorResponse` 结构化格式 |

---

## 阶段一：模型冻结与强化 ✅

### 1.1 强类型化嵌套模型 ✅
- [x] `WeatherSummary.daily_forecasts` → `list[DailyForecast]`
- [x] `BudgetSummary.breakdown` → `BudgetBreakdown`
- [x] 所有模型字段添加 `Field(description=...)` 中文说明

### 1.2 新增图片相关字段 ✅
- [x] `Attraction.image_url`
- [x] `DayPlan.cover_image_url`
- [x] `TripPlan.cover_image_url`

### 1.3 新增导出相关字段 ✅
- [x] `TripPlan.created_at`
- [x] `TripPlan.plan_version`

### 1.4 迁移 `EditRequest` 到 `models/` ✅
- [x] 迁移到 `trip_planner/models/edit.py`
- [x] 在 `models/__init__.py` 中统一导出

### 1.5 为所有模型添加 OpenAPI 示例 ✅
- [x] 所有字段有 Field description
- [x] ge/le 约束（经纬度、时长）

### 1.6 同步更新 workflow.py ✅
- [x] `assemble_plan` 适配 BudgetBreakdown 和 DailyForecast
- [x] stub 数据适配新模型

### 1.7 同步更新测试 ✅
- [x] `tests/test_api.py` — 127 → 增加新字段断言
- [x] `tests/test_workflow.py` — 适配强类型
- [x] `tests/test_service_boundary.py` — 更新字段边界
- [x] `tests/models/test_plan.py` — 10 个测试
- [x] `tests/models/test_request.py` — 5 个测试
- [x] `tests/models/test_edit.py` — 8 个测试（新增）

---

## 阶段二：OpenAPI/Swagger 完善 ✅

### 2.1 错误响应约定 ✅
- [x] `ErrorResponse` 模型（error_code + message + details）
- [x] 全局 `RequestValidationError` / `ValidationError` 处理器
- [x] 422 和 503 统一结构化格式

### 2.2 FastAPI 元数据增强 ✅
- [x] `openapi_tags` 标签分组
- [x] 每个端点 `summary` + `description` + `responses`
- [x] 字段 `ge/le` 约束

### 2.3 验证 Swagger 可访问 ✅
- [x] `/openapi.json` 正常返回 18 个 schemas
- [x] 导出 `docs/RookieVito/openapi.json`

---

## 阶段三：示例 JSON 交付物 ✅

### 3.1 示例文件 ✅
- [x] `trip_plan_standard_3days.json` — 标准 3 天京都行程
- [x] `trip_plan_luxury_5days_with_images.json` — 奢华 5 天东京行程（含图片）
- [x] `trip_plan_after_edit.json` — 编辑后行程（version 递增）

### 3.2 请求示例 ✅
- [x] `trip_plan_request_examples.json` — 2 个请求体示例
- [x] `edit_request_examples.json` — 3 种编辑操作示例

### 3.3 错误示例 ✅
- [x] `error_response_examples.json` — 4 种错误场景

---

## 阶段四：Contract 文档与通知机制 ✅

### 4.1 字段稳定性说明文档 ✅
- [x] `docs/RookieVito/02-field-stability.md`
- [x] 标注稳定/实验性字段
- [x] 标注前端只读/编辑回传字段
- [x] 回答导出和图片补全策略

### 4.2 变更通知机制 ✅
- [x] `docs/RookieVito/CONTRACT_CHANGELOG.md`
- [x] v0.1.0 初始冻结记录

---

## 完成标准

- [x] A 可以不依赖后续实现，直接基于 contract 开发页面
- [x] OpenAPI 能解释清楚前端如何请求和如何消费结果
- [x] 示例 JSON 足够覆盖结果页主要区块
- [x] 共享字段变更有通知机制，不会静默破坏前端
- [x] 所有测试通过（198/198）
