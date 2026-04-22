# Frontend

- `frontend/` 是 Vite + Vue 3 + TypeScript 前端；入口脚本见 `package.json`：`npm run dev`、`build`、`preview`、`test`、`test:watch`。
- `vite.config.ts` 约定 `@ -> /src`，并将 `/api` 代理到 `TRIP_PLANNER_API_ORIGIN`；未显式设置时默认 `http://localhost:8010`。
- `src/views/` 承载页面流，`src/services/` 负责调用后端接口，`src/router/` 管路由，`src/types/` 维护前端侧数据契约。
- 若后端 `TripPlan` / `TripPlanRequest` 等契约变更，优先同步检查 `src/types/` 与相关视图、服务测试，而不是在组件里临时兜底。
- 前端测试使用 Vitest + `happy-dom`；`tests/setup.ts` 已 mock AMap loader。改动接口调用、页面交互或类型映射时，优先补 `frontend/tests/services` 或 `frontend/tests/views` 下最近的测试。
