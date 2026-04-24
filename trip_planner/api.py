from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

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
    openapi_tags=[
        {"name": "健康检查", "description": "服务健康状态"},
        {"name": "行程规划", "description": "创建和编辑旅行计划"},
    ],
)


# ---------------------------------------------------------------------------
# 响应模型
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """统一错误响应格式。"""

    error_code: str = Field(description="错误码，如 VALIDATION_ERROR / PLAN_FAILED")
    message: str = Field(description="面向开发者的错误摘要")
    details: list[dict] | None = Field(default=None, description="详细错误条目（验证错误时存在）")


# ---------------------------------------------------------------------------
# 健康检查
# ---------------------------------------------------------------------------


@app.get(
    "/health",
    tags=["健康检查"],
    summary="健康检查",
    description="返回服务运行状态，用于负载均衡探活。",
    responses={200: {"description": "服务正常"}},
)
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# 行程规划
# ---------------------------------------------------------------------------


@app.post(
    "/api/trip/plan",
    tags=["行程规划"],
    summary="创建旅行计划",
    description="提交旅行偏好，后端生成完整的多日行程计划，包含景点、天气、预算和地图数据。",
    response_model=TripPlan,
    responses={
        200: {"description": "规划成功，返回完整 TripPlan"},
        422: {"description": "请求参数验证失败", "model": ErrorResponse},
        503: {
            "description": "主链路服务不可用（景点/天气），规划失败",
            "model": ErrorResponse,
        },
    },
)
def create_trip_plan(request: TripPlanRequest) -> JSONResponse | TripPlan:
    try:
        plan = run_planner(request)
        plan_dict = plan.model_dump()
        plan_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        plan_dict["plan_version"] = _settings.default_plan_version
        return TripPlan.model_validate(plan_dict)
    except RuntimeError as exc:
        return JSONResponse(
            status_code=503,
            content={
                "error_code": "PLAN_FAILED",
                "message": str(exc),
                "details": None,
            },
        )


@app.post(
    "/api/trip/edit",
    tags=["行程规划"],
    summary="编辑旅行计划",
    description="对已有行程计划执行景点级别的编辑操作：删除景点或调整景点顺序。返回编辑后的完整 TripPlan，plan_version 自增。",
    response_model=TripPlan,
    responses={
        200: {"description": "编辑成功，返回更新后的 TripPlan"},
        422: {"description": "请求参数验证失败或索引越界", "model": ErrorResponse},
    },
)
def edit_trip_plan(req: EditRequest) -> TripPlan:
    plan = req.plan.model_copy(deep=True)
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
