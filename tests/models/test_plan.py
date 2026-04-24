from datetime import date, datetime
from decimal import Decimal

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


def _make_attraction(**overrides) -> Attraction:
    base = dict(
        name="金阁寺",
        address="京都市北区金阁寺町1",
        latitude=35.0394,
        longitude=135.7292,
        suggested_duration_minutes=90,
        ticket_price=Decimal("500"),
    )
    base.update(overrides)
    return Attraction(**base)


def test_attraction_optional_ticket():
    a = _make_attraction(ticket_price=None)
    assert a.ticket_price is None


def test_attraction_optional_image_url():
    a = _make_attraction()
    assert a.image_url is None
    a_with_img = _make_attraction(image_url="https://example.com/image.jpg")
    assert a_with_img.image_url == "https://example.com/image.jpg"


def test_daily_forecast_strong_type():
    df = DailyForecast(date="2025-05-01", condition="晴", high_celsius=24, low_celsius=16)
    assert df.date == "2025-05-01"
    assert df.condition == "晴"


def test_budget_breakdown_strong_type():
    bb = BudgetBreakdown(
        accommodation=Decimal("1200"),
        dining=Decimal("800"),
        attractions=Decimal("400"),
        transport=Decimal("200"),
    )
    assert bb.accommodation == Decimal("1200")
    total = bb.accommodation + bb.dining + bb.attractions + bb.transport
    assert total == Decimal("2600")


def test_budget_summary_with_strong_breakdown():
    bb = BudgetBreakdown(
        accommodation=Decimal("1200"),
        dining=Decimal("800"),
        attractions=Decimal("400"),
        transport=Decimal("200"),
    )
    bs = BudgetSummary(estimated_total=Decimal("3000"), breakdown=bb)
    assert bs.breakdown.accommodation == Decimal("1200")


def test_weather_summary_with_strong_forecasts():
    forecasts = [
        DailyForecast(date="2025-05-01", condition="晴", high_celsius=24, low_celsius=16),
        DailyForecast(date="2025-05-02", condition="多云", high_celsius=22, low_celsius=14),
    ]
    ws = WeatherSummary(overview="晴天为主", daily_forecasts=forecasts)
    assert len(ws.daily_forecasts) == 2
    assert ws.daily_forecasts[0].condition == "晴"


def test_day_plan_optional_cover_image():
    dp = DayPlan(
        date=date(2025, 5, 1),
        attractions=[_make_attraction()],
        dining_suggestion="锦市场附近的京料理",
        accommodation_note="四条河原町附近酒店",
    )
    assert dp.cover_image_url is None


def test_trip_plan_structure():
    bb = BudgetBreakdown(
        accommodation=Decimal("1200"), dining=Decimal("800"),
        attractions=Decimal("400"), transport=Decimal("200"),
    )
    plan = TripPlan(
        destination="京都",
        days=[
            DayPlan(
                date=date(2025, 5, 1),
                attractions=[_make_attraction()],
                dining_suggestion="锦市场附近的京料理",
                accommodation_note="四条河原町附近商务酒店",
            )
        ],
        weather_summary=WeatherSummary(overview="晴天为主，气温 18-24°C"),
        budget_summary=BudgetSummary(estimated_total=Decimal("3000"), breakdown=bb),
        map_points=[
            MapPoint(name="金阁寺", latitude=35.0394, longitude=135.7292, category="attraction")
        ],
    )
    assert len(plan.days) == 1
    assert plan.budget_summary.currency == "CNY"
    assert plan.plan_version == 1
    assert plan.cover_image_url is None
    assert plan.created_at is None


def test_trip_plan_with_new_fields():
    plan = TripPlan(
        destination="京都",
        days=[],
        weather_summary=WeatherSummary(overview="晴"),
        budget_summary=BudgetSummary(
            estimated_total=Decimal("1234.56"),
            breakdown=BudgetBreakdown(
                accommodation=Decimal("500"), dining=Decimal("300"),
                attractions=Decimal("200"), transport=Decimal("100"),
            ),
        ),
        map_points=[],
        cover_image_url="https://example.com/cover.jpg",
        created_at=datetime(2025, 5, 1, 12, 0, 0),
        plan_version=3,
    )
    assert plan.cover_image_url == "https://example.com/cover.jpg"
    assert plan.created_at == datetime(2025, 5, 1, 12, 0, 0)
    assert plan.plan_version == 3


def test_trip_plan_json_roundtrip():
    bb = BudgetBreakdown(
        accommodation=Decimal("500"), dining=Decimal("300"),
        attractions=Decimal("200"), transport=Decimal("100"),
    )
    plan = TripPlan(
        destination="京都",
        days=[],
        weather_summary=WeatherSummary(overview="晴"),
        budget_summary=BudgetSummary(estimated_total=Decimal("1234.56"), breakdown=bb),
        map_points=[],
    )
    restored = TripPlan.model_validate_json(plan.model_dump_json())
    assert restored.budget_summary.estimated_total == Decimal("1234.56")
    assert restored.budget_summary.breakdown.accommodation == Decimal("500")
