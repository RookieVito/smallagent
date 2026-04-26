# Frontend

- Vite + Vue 3 + TypeScript；`npm run dev`、`build`、`preview`、`test`、`test:watch`。
- `vite.config.ts`：`@ -> /src`，`/api` 代理到 `TRIP_PLANNER_API_ORIGIN`（默认 `http://localhost:8010`）。
- `src/types/` 维护前端侧数据契约，与 `docs/RookieVito/openapi.json` 对齐。后端契约变更时，先同步 `types/` 再改视图和服务。
- 结果页结构：5 个固定锚点分区（overview / budget / map / days / weather）+ 侧边导航。地图数据源为后端 `map_points`，不从 attractions 派生。
- 天气展示规则：`overview` + `daily_forecasts`（有数据时显示表格）。预算展示规则：结构化 `BudgetBreakdown`（accommodation / dining / attractions / transport 具名字段）。
- Vitest + `happy-dom`；`tests/setup.ts` mock AMap loader。改动接口、页面交互或类型映射时，优先补 `tests/services` 或 `tests/views` 下最近的测试。
