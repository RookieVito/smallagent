# Backend

- `trip_planner/` 是后端实现根目录；`api.py` 负责 FastAPI 路由与 HTTP 边界，`workflow.py` 负责 LangGraph 规划工作流，`models/` 负责 Pydantic 数据契约。
- 新增或修改规划能力时，优先保持 `api.py -> workflow.py -> models/` 的分层，不要把服务编排、数据清洗或 schema 逻辑塞回路由函数。
- `workflow.py` 通过 `Services` 注入外部依赖；需要替换 stub 或新增外部调用时，优先扩展该注入边界，保持测试可替换性。
- 当前依赖声明在仓库根 `requirements.txt`，仓库根 Python 使用本地 `.venv`；不要假设这里有独立 `pyproject.toml`。
- 若修改 `models/`、路由返回值或工作流输出，优先同步最近的 `tests/test_api.py`、`tests/test_workflow.py`、`tests/test_service_boundary.py` 与 `tests/models/`，并检查前端 `frontend/src/types/` 是否需要同改。
