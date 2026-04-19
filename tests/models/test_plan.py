from datetime import date
from decimal import Decimal

from trip_planner.models.plan import (
    Attraction,
    BudgetSummary,
    DayPlan,
    MapPoint,
    TripPlan,
    WeatherSummary,
)


def _make_attraction() -> Attraction:
    return Attraction(
        name="金阁寺",
        address="京都市北区金阁寺町1",
        latitude=35.0394,
        longitude=135.7292,
        suggested_duration_minutes=90,
        ticket_price=Decimal("500"),
    )


def test_attraction_optional_ticket():
    a = Attraction(
        name="嵐山",
        address="京都市右京区",
        latitude=35.0094,
        longitude=135.6780,
        suggested_duration_minutes=120,
    )
    assert a.ticket_price is None


def test_trip_plan_structure():
    plan = TripPlan(
        destination="京都",
        days=[
            DayPlan(
                date=date(2025, 5, 1),
                attractions=[_make_attraction()],
                dining_suggestion="锦市场附近的京料理",
                accommodation_note="推荐四条河原町附近商务酒店",
            )
        ],
        weather_summary=WeatherSummary(overview="晴天为主，气温 18-24°C"),
        budget_summary=BudgetSummary(
            estimated_total=Decimal("3000"),
            breakdown={"accommodation": Decimal("1200"), "dining": Decimal("800")},
        ),
        map_points=[
            MapPoint(name="金阁寺", latitude=35.0394, longitude=135.7292, category="attraction")
        ],
    )
    assert len(plan.days) == 1
    assert plan.budget_summary.currency == "CNY"


def test_trip_plan_json_roundtrip():
    plan = TripPlan(
        destination="京都",
        days=[],
        weather_summary=WeatherSummary(overview="晴"),
        budget_summary=BudgetSummary(estimated_total=Decimal("1234.56")),
        map_points=[],
    )
    restored = TripPlan.model_validate_json(plan.model_dump_json())
    assert restored.budget_summary.estimated_total == Decimal("1234.56")
