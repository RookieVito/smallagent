from typing import Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, model_validator

from trip_planner.models.plan import TripPlan
from trip_planner.models.request import TripPlanRequest
from trip_planner.workflow import Services, run_planner

app = FastAPI(title="智能旅行助手 API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/trip/plan", response_model=TripPlan)
def create_trip_plan(request: TripPlanRequest) -> JSONResponse | TripPlan:
    try:
        return run_planner(request)
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"detail": str(exc)})


# ---------------------------------------------------------------------------
# 编辑端点
# ---------------------------------------------------------------------------

class EditRequest(BaseModel):
    plan: TripPlan
    operation: Literal["delete_attraction", "move_attraction"]
    day_index: int
    attraction_index: int
    direction: Literal["up", "down"] | None = None

    @model_validator(mode="after")
    def validate_bounds_and_direction(self) -> "EditRequest":
        days = self.plan.days
        if self.day_index < 0 or self.day_index >= len(days):
            raise ValueError(
                f"day_index {self.day_index} 越界（共 {len(days)} 天）"
            )
        attractions = days[self.day_index].attractions
        if self.attraction_index < 0 or self.attraction_index >= len(attractions):
            raise ValueError(
                f"attraction_index {self.attraction_index} 越界（第 {self.day_index} 天共 {len(attractions)} 个景点）"
            )
        if self.operation == "move_attraction" and self.direction is None:
            raise ValueError("move_attraction 操作必须提供 direction")
        return self


@app.post("/api/trip/edit", response_model=TripPlan)
def edit_trip_plan(req: EditRequest) -> TripPlan:
    # 深拷贝，不修改原始对象
    plan = req.plan.model_copy(deep=True)
    attractions = plan.days[req.day_index].attractions

    if req.operation == "delete_attraction":
        attractions.pop(req.attraction_index)

    elif req.operation == "move_attraction":
        idx = req.attraction_index
        if req.direction == "up" and idx > 0:
            attractions[idx], attractions[idx - 1] = attractions[idx - 1], attractions[idx]
        elif req.direction == "down" and idx < len(attractions) - 1:
            attractions[idx], attractions[idx + 1] = attractions[idx + 1], attractions[idx]

    return plan
