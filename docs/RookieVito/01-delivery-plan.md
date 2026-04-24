# B 首批交付 — 实施计划

> 目标：尽快给 A 一套可并行开发的稳定 contract，不依赖后端后续实现。

---

## 现状评估

| 模型 | 状态 | 备注 |
|------|------|------|
| `TripPlanRequest` | 已有基础定义 | 缺少 `openapi_examples`、缺少部分字段文档 |
| `TripPlan` | 已有基础定义 | 缺少图片字段、缺少导出相关字段 |
| `EditRequest` | 已有实现 | 定义在 `api.py` 中，应迁移到 `models/` |
| `WeatherSummary.daily_forecasts` | `list[dict]` | 应定义为强类型 `DailyForecast` |
| `BudgetSummary.breakdown` | `dict[str, Decimal]` | 应定义为强类型结构 |
| OpenAPI/Swagger | FastAPI 自动生成 | 缺少中文描述、示例值、字段稳定性标注 |
| 示例 JSON | 无 | 需要覆盖 8+ 场景 |
| 错误响应约定 | 仅 `503` + `detail` | 需要结构化错误格式 |

---

## 阶段一：模型冻结与强化（Phase 1）

**目标**：冻结 `TripPlanRequest`、`TripPlan`、`EditRequest` 的第一版字段。

### 1.1 强类型化嵌套模型
- [ ] 将 `WeatherSummary.daily_forecasts` 从 `list[dict]` 改为 `list[DailyForecast]`（新增 `DailyForecast` 模型）
- [ ] 将 `BudgetSummary.breakdown` 从 `dict[str, Decimal]` 改为强类型 `BudgetBreakdown`
- [ ] 为所有模型字段添加 `Field(description=...)` 中文说明

### 1.2 新增图片相关字段
- [ ] 在 `Attraction` 中添加 `image_url: str | None = None`
- [ ] 在 `DayPlan` 中添加 `cover_image_url: str | None = None`
- [ ] 在 `TripPlan` 中添加 `cover_image_url: str | None = None`

### 1.3 新增导出相关字段
- [ ] 在 `TripPlan` 中添加 `created_at: datetime | None = None`
- [ ] 在 `TripPlan` 中添加 `plan_version: int = 1`

### 1.4 迁移 `EditRequest` 到 `models/`
- [ ] 将 `EditRequest` 从 `api.py` 迁移到 `trip_planner/models/edit.py`
- [ ] 在 `models/__init__.py` 中统一导出

### 1.5 为所有模型添加 OpenAPI 示例
- [ ] 为 `TripPlanRequest` 添加 `json_schema_extra/examples`
- [ ] 为 `TripPlan` 添加 `json_schema_extra/examples`
- [ ] 为 `EditRequest` 添加 `json_schema_extra/examples`

### 1.6 同步更新 workflow.py
- [ ] 更新 `assemble_plan` 适配新字段
- [ ] 更新 stub 数据适配新模型

### 1.7 同步更新测试
- [ ] 更新 `tests/test_api.py`
- [ ] 更新 `tests/test_workflow.py`
- [ ] 更新 `tests/test_service_boundary.py`
- [ ] 更新 `tests/models/test_plan.py`
- [ ] 更新 `tests/models/test_request.py`

---

## 阶段二：OpenAPI/Swagger 完善（Phase 2）

**目标**：让 Swagger 能完整解释前端如何请求和如何消费结果。

### 2.1 错误响应约定
- [ ] 定义统一错误响应模型 `ErrorResponse`（含 `error_code`、`message`、`details`）
- [ ] 在 `api.py` 中注册全局异常处理器
- [ ] 为 `422` 验证错误和 `503` 运行时错误统一格式

### 2.2 FastAPI 元数据增强
- [ ] 添加 API 描述、标签分组
- [ ] 为每个端点添加 `summary`、`description`、`responses` 文档
- [ ] 添加字段稳定性标注（`x-stable` 扩展字段）

### 2.3 验证 Swagger 可访问
- [ ] 启动服务验证 `/docs` 和 `/openapi.json` 可正常访问
- [ ] 导出 `openapi.json` 到 `docs/RookieVito/openapi.json`

---

## 阶段三：示例 JSON 交付物（Phase 3）

**目标**：提供 2-3 个完整 TripPlan 示例 + 请求示例 + 编辑示例 + 错误示例。

### 3.1 示例文件
- [ ] `trip_plan_example_1.json` — 标准 3 天行程（含全部字段）
- [ ] `trip_plan_example_2.json` — 奢华 5 天行程（含图片字段）
- [ ] `trip_plan_example_3.json` — 编辑后的行程

### 3.2 请求示例
- [ ] `trip_plan_request_example.json` — TripPlanRequest 示例
- [ ] `edit_request_example.json` — EditRequest 示例

### 3.3 错误示例
- [ ] `error_response_example.json` — 各种错误响应示例

---

## 阶段四：Contract 文档与通知机制（Phase 4）

**目标**：A 可以不依赖后续实现直接基于 contract 开发。

### 4.1 字段稳定性说明文档
- [ ] 标注哪些字段是稳定字段（不会变）
- [ ] 标注哪些字段可能变化（实验性）
- [ ] 标注前端只读消费字段
- [ ] 标注编辑接口需回传的字段

### 4.2 变更通知机制
- [ ] 在 `CHANGELOG.md` 或独立 contract changelog 中记录字段变更

---

## 完成标准

- [ ] A 可以不依赖后续实现，直接基于 contract 开发页面
- [ ] OpenAPI 能解释清楚前端如何请求和如何消费结果
- [ ] 示例 JSON 足够覆盖结果页主要区块
- [ ] 共享字段变更有通知机制，不会静默破坏前端
- [ ] 所有测试通过
