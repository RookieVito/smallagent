from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from trip_planner.config import get_settings
from trip_planner.models.edit import EditRequest
from trip_planner.models.plan import TripPlan
from trip_planner.models.request import TripPlanRequest
from trip_planner.workflow import run_planner

_settings = get_settings()

app = FastAPI(
    title=_settings.app_title,
    version=_settings.app_version,
    description=_settings.app_description,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/trip/plan", response_model=TripPlan)
def create_trip_plan(request: TripPlanRequest) -> JSONResponse | TripPlan:
    try:
        plan = run_planner(request)
        # 由服务端生成 created_at
        plan_dict = plan.model_dump()
        plan_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        plan_dict["plan_version"] = _settings.default_plan_version
        return TripPlan.model_validate(plan_dict)
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"detail": str(exc)})


# ---------------------------------------------------------------------------
# 统一验证错误处理器
# ---------------------------------------------------------------------------


def _safe_validation_errors(errors: list[dict]) -> list[dict]:
    """递归清理验证错误，确保所有值可 JSON 序列化。"""
    cleaned = []
    for err in errors:
        item = {}
        for k, v in err.items():
            if isinstance(v, Exception):
                item[k] = str(v)
            elif isinstance(v, dict):
                item[k] = _safe_validation_errors([v])[0] if v else {}
            else:
                item[k] = v
        cleaned.append(item)
    return cleaned


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": _safe_validation_errors(exc.errors()),
        },
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(_request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": _safe_validation_errors(exc.errors()),
        },
    )


# ---------------------------------------------------------------------------
# 编辑端点
# ---------------------------------------------------------------------------


@app.post("/api/trip/edit", response_model=TripPlan)
def edit_trip_plan(req: EditRequest) -> TripPlan:
    plan = req.plan.model_copy(deep=True)
    # 编辑后 plan_version 递增
    plan.plan_version += 1
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
