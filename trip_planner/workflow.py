"""V0 规划工作流骨架 — 所有节点使用 stub 数据，不调用真实外部服务。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Callable

from langgraph.graph import END, START, StateGraph
from langgraph.types import RunnableConfig

from trip_planner.config import get_settings
from trip_planner.models.enums import BudgetLevel
from trip_planner.models.plan import (
    Attraction,
    BudgetBreakdown,
    BudgetSummary,
    DailyForecast,
    DayPlan,
    MapPoint,
    TripPlan,
    WeatherSummary,
)
from trip_planner.models.request import TripPlanRequest
from trip_planner.models.state import PlannerState

_settings = get_settings()


# ---------------------------------------------------------------------------
# 服务层协议
# 每个字段是一个可替换的函数，测试时注入 mock，生产时替换为真实调用。
# ---------------------------------------------------------------------------


@dataclass
class Services:
    fetch_attractions: Callable[[TripPlanRequest], list[dict]] = field(
        default_factory=lambda: _default_fetch_attractions
    )
    fetch_weather: Callable[[TripPlanRequest], dict] = field(
        default_factory=lambda: _default_fetch_weather
    )
    fetch_hotels: Callable[[TripPlanRequest], list[dict]] = field(
        default_factory=lambda: _default_fetch_hotels
    )


# ---------------------------------------------------------------------------
# 默认 stub 实现
# ---------------------------------------------------------------------------


def _default_fetch_attractions(req: TripPlanRequest) -> list[dict]:
    dest = req.destination
    return [
        {
            "name": f"{dest}景点A",
            "address": f"{dest}市中心区1号",
            "latitude": 35.0,
            "longitude": 135.0,
            "suggested_duration_minutes": 90,
            "ticket_price": "50.00",
        },
        {
            "name": f"{dest}景点B",
            "address": f"{dest}市郊区2号",
            "latitude": 35.01,
            "longitude": 135.01,
            "suggested_duration_minutes": 60,
            "ticket_price": None,
        },
        {
            "name": f"{dest}古寺",
            "address": f"{dest}古寺路3号",
            "latitude": 35.02,
            "longitude": 134.99,
            "suggested_duration_minutes": 80,
            "ticket_price": "30.00",
        },
        {
            "name": f"{dest}市场街",
            "address": f"{dest}市场街4号",
            "latitude": 34.99,
            "longitude": 135.02,
            "suggested_duration_minutes": 120,
            "ticket_price": None,
        },
        {
            "name": f"{dest}地标塔",
            "address": f"{dest}地标广场5号",
            "latitude": 35.03,
            "longitude": 135.03,
            "suggested_duration_minutes": 60,
            "ticket_price": "80.00",
        },
        {
            "name": f"{dest}花园",
            "address": f"{dest}花园路6号",
            "latitude": 34.98,
            "longitude": 134.98,
            "suggested_duration_minutes": 90,
            "ticket_price": None,
        },
    ]


def _default_fetch_weather(req: TripPlanRequest) -> dict:
    forecasts = []
    for i in range(req.trip_days):
        day_date = date.fromordinal(req.start_date.toordinal() + i)
        forecasts.append({
            "date": str(day_date),
            "condition": "晴" if i % 2 == 0 else "多云",
            "high_celsius": 24,
            "low_celsius": 16,
        })
    return {
        "overview": f"{req.destination} 旅行期间以晴天为主，气温适宜",
        "daily_forecasts": forecasts,
    }


def _default_fetch_hotels(req: TripPlanRequest) -> list[dict]:
    acc_type = req.accommodation_type.value
    return [
        {
            "name": f"{req.destination}精选{acc_type}",
            "address": f"{req.destination}市中心",
            "price_per_night": "300.00",
            "type": acc_type,
        }
    ]


# ---------------------------------------------------------------------------
# 节点函数 — 从 config["configurable"]["services"] 读取服务层
# ---------------------------------------------------------------------------


def _get_services(config: RunnableConfig) -> Services:
    return config.get("configurable", {}).get("services", Services())


def normalize_request(state: PlannerState) -> dict:
    """标准化入站请求：确保 destination 和 preferences 无多余空白。"""
    req = state.request
    if req is None:
        return {"errors": ["normalize_request: request 为空"]}
    normalized = req.model_copy(
        update={
            "destination": req.destination.strip(),
            "preferences": [p.strip() for p in req.preferences if p.strip()],
        }
    )
    return {"request": normalized}


def fetch_attractions(state: PlannerState, config: RunnableConfig) -> dict:
    """检索目的地候选景点（主链路依赖）。"""
    if state.request is None:
        return {"errors": ["fetch_attractions: request 缺失，跳过"]}
    svc = _get_services(config)
    try:
        result = svc.fetch_attractions(state.request)
    except Exception as exc:
        return {"errors": [f"fetch_attractions: {exc}"], "candidate_attractions": []}
    return {"candidate_attractions": result}


def fetch_weather(state: PlannerState, config: RunnableConfig) -> dict:
    """查询旅行期天气（主链路依赖）。"""
    if state.request is None:
        return {"errors": ["fetch_weather: request 缺失，跳过"]}
    svc = _get_services(config)
    try:
        result = svc.fetch_weather(state.request)
    except Exception as exc:
        return {"errors": [f"fetch_weather: {exc}"], "weather_data": {}}
    return {"weather_data": result}


def fetch_hotels(state: PlannerState, config: RunnableConfig) -> dict:
    """检索住宿候选（可降级依赖：失败时写入空列表而非阻断主链路）。"""
    if state.request is None:
        return {"errors": ["fetch_hotels: request 缺失，跳过"]}
    svc = _get_services(config)
    try:
        result = svc.fetch_hotels(state.request)
    except Exception:
        return {"hotel_candidates": []}
    return {"hotel_candidates": result}


def assemble_plan(state: PlannerState) -> dict:
    """收敛所有素材，生成最终 TripPlan；主链路素材不足时写入 errors。"""
    missing: list[str] = []
    if not state.candidate_attractions:
        missing.append("candidate_attractions 为空")
    if not state.weather_data:
        missing.append("weather_data 为空")
    if missing:
        return {"errors": [f"assemble_plan: 主链路素材缺失 — {', '.join(missing)}"]}

    req = state.request
    if req is None:
        return {"errors": ["assemble_plan: request 缺失"]}

    trip_days = req.trip_days
    attractions_per_day = max(1, len(state.candidate_attractions) // trip_days)
    days: list[DayPlan] = []
    for i in range(trip_days):
        day_date = date.fromordinal(req.start_date.toordinal() + i)
        slice_start = i * attractions_per_day
        raw_attrs = state.candidate_attractions[
            slice_start : slice_start + attractions_per_day
        ]
        if not raw_attrs:
            raw_attrs = state.candidate_attractions[:1]
        attractions = [
            Attraction(
                name=a["name"],
                address=a["address"],
                latitude=float(a["latitude"]),
                longitude=float(a["longitude"]),
                suggested_duration_minutes=int(a["suggested_duration_minutes"]),
                ticket_price=Decimal(a["ticket_price"])
                if a.get("ticket_price")
                else None,
                image_url=a.get("image_url"),
            )
            for a in raw_attrs
        ]
        hotel_note = (
            state.hotel_candidates[0]["name"]
            if state.hotel_candidates
            else f"{req.destination}市内住宿（具体推荐待补充）"
        )
        days.append(
            DayPlan(
                date=day_date,
                attractions=attractions,
                dining_suggestion=f"第{i + 1}天：推荐当地特色餐厅",
                accommodation_note=hotel_note,
            )
        )

    # 天气汇总：daily_forecasts 转为强类型 DailyForecast
    raw_forecasts = state.weather_data.get("daily_forecasts", [])
    daily_forecasts = [
        DailyForecast(
            date=f["date"],
            condition=f["condition"],
            high_celsius=f["high_celsius"],
            low_celsius=f["low_celsius"],
        )
        for f in raw_forecasts
        if isinstance(f, dict)
    ]
    weather_summary = WeatherSummary(
        overview=state.weather_data.get("overview", ""),
        daily_forecasts=daily_forecasts,
    )

    # 预算汇总：使用强类型 BudgetBreakdown
    budget_map = {
        BudgetLevel.BUDGET: Decimal("1000"),
        BudgetLevel.MODERATE: Decimal("3000"),
        BudgetLevel.LUXURY: Decimal("8000"),
    }
    estimated = budget_map.get(req.budget_level, Decimal("3000")) * trip_days
    breakdown = BudgetBreakdown(
        accommodation=estimated * Decimal("0.4"),
        dining=estimated * Decimal("0.3"),
        attractions=estimated * Decimal("0.2"),
        transport=estimated * Decimal("0.1"),
    )
    budget_summary = BudgetSummary(
        estimated_total=estimated,
        currency=_settings.default_currency,
        breakdown=breakdown,
    )

    map_points = [
        MapPoint(
            name=a["name"],
            latitude=float(a["latitude"]),
            longitude=float(a["longitude"]),
            category="attraction",
        )
        for a in state.candidate_attractions
    ]

    plan = TripPlan(
        destination=req.destination,
        days=days,
        weather_summary=weather_summary,
        budget_summary=budget_summary,
        map_points=map_points,
    )
    return {"trip_plan": plan}


# ---------------------------------------------------------------------------
# 图构建
# ---------------------------------------------------------------------------


def _build_graph() -> StateGraph:
    g = StateGraph(state_schema=PlannerState)

    g.add_node(normalize_request)
    g.add_node(fetch_attractions)
    g.add_node(fetch_weather)
    g.add_node(fetch_hotels)
    g.add_node(assemble_plan)

    g.add_edge(START, "normalize_request")

    g.add_edge("normalize_request", "fetch_attractions")
    g.add_edge("normalize_request", "fetch_weather")
    g.add_edge("normalize_request", "fetch_hotels")

    g.add_edge("fetch_attractions", "assemble_plan")
    g.add_edge("fetch_weather", "assemble_plan")
    g.add_edge("fetch_hotels", "assemble_plan")

    g.add_edge("assemble_plan", END)
    return g


_app = _build_graph().compile()


# ---------------------------------------------------------------------------
# 公开入口
# ---------------------------------------------------------------------------


def run_planner(request: TripPlanRequest, services: Services | None = None) -> TripPlan:
    """执行规划工作流，返回 TripPlan；主链路失败时抛出 RuntimeError。"""
    config: RunnableConfig = {}
    if services is not None:
        config = {"configurable": {"services": services}}

    result = _app.invoke(PlannerState(request=request).model_dump(), config=config)
    final_state = PlannerState.model_validate(result)

    if final_state.trip_plan is None:
        error_detail = (
            "; ".join(final_state.errors) if final_state.errors else "未知错误"
        )
        raise RuntimeError(f"规划失败: {error_detail}")

    return final_state.trip_plan
