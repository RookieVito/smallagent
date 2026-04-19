from datetime import date
from decimal import Decimal

import pytest

from trip_planner.models.enums import AccommodationType, BudgetLevel
from trip_planner.models.plan import TripPlan
from trip_planner.models.request import TripPlanRequest
from trip_planner.models.state import PlannerState
from trip_planner.workflow import (
    assemble_plan,
    fetch_attractions,
    fetch_hotels,
    fetch_weather,
    normalize_request,
    run_planner,
)


@pytest.fixture
def kyoto_request() -> TripPlanRequest:
    return TripPlanRequest(
        destination="京都",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 4),
        preferences=["历史文化", "美食"],
        budget_level=BudgetLevel.MODERATE,
        accommodation_type=AccommodationType.HOTEL,
    )


@pytest.fixture
def base_state(kyoto_request: TripPlanRequest) -> PlannerState:
    return PlannerState(request=kyoto_request)


# ---------------------------------------------------------------------------
# normalize_request
# ---------------------------------------------------------------------------

def test_normalize_request_ok(base_state: PlannerState):
    result = normalize_request(base_state)
    assert "errors" not in result or result.get("errors") == []


def test_normalize_request_no_request():
    result = normalize_request(PlannerState())
    assert result["errors"]
    assert "normalize_request" in result["errors"][0]


# ---------------------------------------------------------------------------
# fetch_attractions
# ---------------------------------------------------------------------------

_EMPTY_CONFIG: dict = {}


def test_fetch_attractions_returns_list(base_state: PlannerState):
    result = fetch_attractions(base_state, _EMPTY_CONFIG)
    assert len(result["candidate_attractions"]) >= 1


def test_fetch_attractions_required_fields(base_state: PlannerState):
    for attr in fetch_attractions(base_state, _EMPTY_CONFIG)["candidate_attractions"]:
        assert "name" in attr and "latitude" in attr and "longitude" in attr


def test_fetch_attractions_no_request():
    assert fetch_attractions(PlannerState(), _EMPTY_CONFIG)["errors"]


# ---------------------------------------------------------------------------
# fetch_weather
# ---------------------------------------------------------------------------

def test_fetch_weather_has_overview(base_state: PlannerState):
    result = fetch_weather(base_state, _EMPTY_CONFIG)
    assert result["weather_data"]["overview"]


def test_fetch_weather_no_request():
    assert fetch_weather(PlannerState(), _EMPTY_CONFIG)["errors"]


# ---------------------------------------------------------------------------
# fetch_hotels
# ---------------------------------------------------------------------------

def test_fetch_hotels_returns_list(base_state: PlannerState):
    assert len(fetch_hotels(base_state, _EMPTY_CONFIG)["hotel_candidates"]) >= 1


def test_fetch_hotels_type_matches(base_state: PlannerState):
    assert fetch_hotels(base_state, _EMPTY_CONFIG)["hotel_candidates"][0]["type"] == "hotel"


def test_fetch_hotels_no_request():
    assert fetch_hotels(PlannerState(), _EMPTY_CONFIG)["errors"]


# ---------------------------------------------------------------------------
# assemble_plan
# ---------------------------------------------------------------------------

def _full_state(request: TripPlanRequest) -> PlannerState:
    return PlannerState(
        request=request,
        candidate_attractions=[
            {
                "name": "金阁寺",
                "address": "京都市北区",
                "latitude": 35.039,
                "longitude": 135.729,
                "suggested_duration_minutes": 90,
                "ticket_price": "500",
            },
            {
                "name": "嵐山",
                "address": "京都市右京区",
                "latitude": 35.009,
                "longitude": 135.678,
                "suggested_duration_minutes": 120,
                "ticket_price": None,
            },
        ],
        weather_data={"overview": "晴天为主", "daily_forecasts": []},
        hotel_candidates=[
            {"name": "京都精选酒店", "address": "四条", "price_per_night": "800", "type": "hotel"}
        ],
    )


def test_assemble_plan_produces_trip_plan(kyoto_request: TripPlanRequest):
    result = assemble_plan(_full_state(kyoto_request))
    assert isinstance(result["trip_plan"], TripPlan)


def test_assemble_plan_day_count(kyoto_request: TripPlanRequest):
    result = assemble_plan(_full_state(kyoto_request))
    assert len(result["trip_plan"].days) == kyoto_request.trip_days


def test_assemble_plan_map_points(kyoto_request: TripPlanRequest):
    result = assemble_plan(_full_state(kyoto_request))
    assert len(result["trip_plan"].map_points) == 2


def test_assemble_plan_budget_currency(kyoto_request: TripPlanRequest):
    result = assemble_plan(_full_state(kyoto_request))
    assert result["trip_plan"].budget_summary.currency == "CNY"


def test_assemble_plan_fails_without_attractions(kyoto_request: TripPlanRequest):
    state = PlannerState(request=kyoto_request, weather_data={"overview": "晴"})
    result = assemble_plan(state)
    assert result.get("errors") and result.get("trip_plan") is None


def test_assemble_plan_fails_without_weather(kyoto_request: TripPlanRequest):
    state = PlannerState(
        request=kyoto_request,
        candidate_attractions=[
            {"name": "A", "address": "B", "latitude": 35.0, "longitude": 135.0,
             "suggested_duration_minutes": 60, "ticket_price": None}
        ],
    )
    result = assemble_plan(state)
    assert result.get("errors")


def test_assemble_plan_degrades_without_hotels(kyoto_request: TripPlanRequest):
    state = PlannerState(
        request=kyoto_request,
        candidate_attractions=[
            {"name": "A", "address": "B", "latitude": 35.0, "longitude": 135.0,
             "suggested_duration_minutes": 60, "ticket_price": None}
        ],
        weather_data={"overview": "晴"},
    )
    result = assemble_plan(state)
    assert isinstance(result.get("trip_plan"), TripPlan)
    assert "京都" in result["trip_plan"].days[0].accommodation_note


# ---------------------------------------------------------------------------
# run_planner 集成测试
# ---------------------------------------------------------------------------

def test_run_planner_returns_trip_plan(kyoto_request: TripPlanRequest):
    plan = run_planner(kyoto_request)
    assert isinstance(plan, TripPlan)
    assert plan.destination == "京都"


def test_run_planner_day_count(kyoto_request: TripPlanRequest):
    plan = run_planner(kyoto_request)
    assert len(plan.days) == kyoto_request.trip_days


def test_run_planner_weather_summary(kyoto_request: TripPlanRequest):
    assert run_planner(kyoto_request).weather_summary.overview != ""


def test_run_planner_budget_positive(kyoto_request: TripPlanRequest):
    assert run_planner(kyoto_request).budget_summary.estimated_total > Decimal("0")


def test_run_planner_map_points(kyoto_request: TripPlanRequest):
    assert len(run_planner(kyoto_request).map_points) >= 1


def test_run_planner_luxury_higher_than_budget():
    base = dict(
        destination="东京",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 4),
        preferences=["购物"],
        accommodation_type=AccommodationType.HOTEL,
    )
    plan_b = run_planner(TripPlanRequest(**base, budget_level=BudgetLevel.BUDGET))
    plan_l = run_planner(TripPlanRequest(**base, budget_level=BudgetLevel.LUXURY))
    assert plan_l.budget_summary.estimated_total > plan_b.budget_summary.estimated_total


def test_run_planner_json_roundtrip(kyoto_request: TripPlanRequest):
    plan = run_planner(kyoto_request)
    restored = TripPlan.model_validate_json(plan.model_dump_json())
    assert restored.destination == plan.destination
    assert len(restored.days) == len(plan.days)
