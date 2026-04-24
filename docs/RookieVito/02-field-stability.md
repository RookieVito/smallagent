# 字段稳定性说明

> 本文档面向前端（A），标注哪些字段可放心消费、哪些可能变动。
> 每次字段变更后，B 必须先更新本文档和 OpenAPI，再通知 A。

---

## TripPlan（响应顶层）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `destination` | **稳定** | 只读 | 目的地名称，不会改变 |
| `days` | **稳定** | 只读 | 每日行程列表，结构稳定 |
| `weather_summary` | **稳定** | 只读 | 天气汇总，字段可能增加但不会删除 |
| `budget_summary` | **稳定** | 只读 | 预算汇总，结构稳定 |
| `map_points` | **稳定** | 只读 | 地图标记点，结构稳定 |
| `cover_image_url` | **实验性** | 只读 | 行程封面图，可能重命名为 `hero_image_url` |
| `created_at` | **稳定** | 只读 | 创建时间，ISO 8601 格式 |
| `plan_version` | **稳定** | 只读 | 版本号，每次编辑递增 |

## DayPlan（每日行程）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `date` | **稳定** | 只读 | 日期 |
| `attractions` | **稳定** | 只读/编辑 | 景点列表，编辑接口需要回传 |
| `dining_suggestion` | **稳定** | 只读 | 餐饮建议 |
| `accommodation_note` | **稳定** | 只读 | 住宿说明 |
| `cover_image_url` | **实验性** | 只读 | 每日封面图，后续可能变为列表 |

## Attraction（景点）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `name` | **稳定** | 只读/编辑 | 景点名称 |
| `address` | **稳定** | 只读 | 景点地址 |
| `latitude` | **稳定** | 只读 | 纬度 |
| `longitude` | **稳定** | 只读 | 经度 |
| `suggested_duration_minutes` | **稳定** | 只读 | 建议游览时长 |
| `ticket_price` | **稳定** | 只读 | 门票价格，null 表示免费 |
| `image_url` | **实验性** | 只读 | 景点图片，图片补全功能完成前为 null |

## BudgetSummary（预算汇总）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `estimated_total` | **稳定** | 只读 | 预估总费用 |
| `currency` | **稳定** | 只读 | 货币代码，当前固定 CNY |
| `breakdown` | **稳定** | 只读 | 强类型 BudgetBreakdown |

## BudgetBreakdown（预算明细）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `accommodation` | **稳定** | 只读 | 住宿费用 |
| `dining` | **稳定** | 只读 | 餐饮费用 |
| `attractions` | **稳定** | 只读 | 景点门票费用 |
| `transport` | **稳定** | 只读 | 交通费用 |

## WeatherSummary（天气汇总）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `overview` | **稳定** | 只读 | 天气概述 |
| `daily_forecasts` | **稳定** | 只读 | 每日天气预报列表（强类型 DailyForecast） |

## DailyForecast（每日天气）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `date` | **稳定** | 只读 | 日期 YYYY-MM-DD |
| `condition` | **稳定** | 只读 | 天气状况 |
| `high_celsius` | **稳定** | 只读 | 最高温度 |
| `low_celsius` | **稳定** | 只读 | 最低温度 |

## MapPoint（地图标记）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `name` | **稳定** | 只读 | 名称 |
| `latitude` | **稳定** | 只读 | 纬度 |
| `longitude` | **稳定** | 只读 | 经度 |
| `category` | **稳定** | 只读 | 分类标签 |

## TripPlanRequest（请求体）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `destination` | **稳定** | 前端→后端 | 目的地 |
| `start_date` | **稳定** | 前端→后端 | 出发日期 |
| `end_date` | **稳定** | 前端→后端 | 返回日期 |
| `preferences` | **稳定** | 前端→后端 | 偏好列表 |
| `budget_level` | **稳定** | 前端→后端 | budget/moderate/luxury |
| `accommodation_type` | **稳定** | 前端→后端 | hotel/hostel/apartment/resort/any |

## EditRequest（编辑请求体）

| 字段 | 稳定性 | 方向 | 说明 |
|------|--------|------|------|
| `plan` | **稳定** | 前端→后端 | 完整的当前 TripPlan |
| `operation` | **稳定** | 前端→后端 | delete_attraction / move_attraction |
| `day_index` | **稳定** | 前端→后端 | 天索引 |
| `attraction_index` | **稳定** | 前端→后端 | 景点索引 |
| `direction` | **稳定** | 前端→后端 | up/down（仅 move_attraction 时） |

---

## 关键问答

### 导出是否需要额外接口或额外字段？
当前 `TripPlan` 已包含 `created_at` 和 `plan_version`，足以支持导出时的元数据需求。
如果需要 PDF/图片导出，预计会增加独立的 `/api/trip/export` 端点，不会修改 TripPlan 结构。

### 图片补全是否写回 TripPlan？
是。图片补全后，`Attraction.image_url`、`DayPlan.cover_image_url`、`TripPlan.cover_image_url`
会被填充为实际 URL。补全为增强依赖（失败不阻断主链路）。

### 哪些字段是编辑接口要回传的？
`EditRequest.plan` 需要回传**完整的** TripPlan（包含所有嵌套字段）。
当前只支持 `delete_attraction` 和 `move_attraction` 两种操作，操作通过 `day_index` + `attraction_index` 定位。
