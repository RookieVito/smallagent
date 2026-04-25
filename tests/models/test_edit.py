from datetime import date
from decimal import Decimal

import pytest

from trip_planner.models.edit import EditRequest
from trip_planner.models.plan import (
    Attraction,
    BudgetBreakdown,
    BudgetSummary,
    DayPlan,
    TripPlan,
    WeatherSummary,
)


def _make_trip_plan(**overrides) -> TripPlan:
    base = dict(
        destination="京都",
        days=[
            DayPlan(
                date=date(2025, 5, 1),
                attractions=[
                    Attraction(
                        name="金阁寺", address="京都市北区", latitude=35.039, longitude=135.729,
                        suggested_duration_minutes=90, ticket_price=Decimal("500"),
                    ),
                    Attraction(
                        name="嵐山", address="京都市右京区", latitude=35.009, longitude=135.678,
                        suggested_duration_minutes=120, ticket_price=None,
                    ),
                ],
                dining_suggestion="锦市场京料理",
                accommodation_note="四条河原町酒店",
            ),
            DayPlan(
                date=date(2025, 5, 2),
                attractions=[
                    Attraction(
                        name="伏见稻荷", address="京都市伏见区", latitude=34.967, longitude=135.773,
                        suggested_duration_minutes=60, ticket_price=None,
                    ),
                ],
                dining_suggestion="宇治抹茶甜品",
                accommodation_note="京都站附近酒店",
            ),
        ],
        weather_summary=WeatherSummary(overview="晴天为主"),
        budget_summary=BudgetSummary(
            estimated_total=Decimal("6000"),
            breakdown=BudgetBreakdown(
                accommodation=Decimal("2400"), dining=Decimal("1800"),
                attractions=Decimal("1200"), transport=Decimal("600"),
            ),
        ),
        map_points=[],
    )
    base.update(overrides)
    return TripPlan(**base)


class TestEditRequestValidation:
    def test_valid_delete_attraction(self):
        req = EditRequest(
            plan=_make_trip_plan(),
            operation="delete_attraction",
            day_index=0,
            attraction_index=0,
        )
        assert req.operation == "delete_attraction"

    def test_valid_move_attraction(self):
        req = EditRequest(
            plan=_make_trip_plan(),
            operation="move_attraction",
            day_index=0,
            attraction_index=1,
            direction="up",
        )
        assert req.direction == "up"

    def test_day_index_out_of_bounds(self):
        with pytest.raises(ValueError, match="day_index"):
            EditRequest(
                plan=_make_trip_plan(),
                operation="delete_attraction",
                day_index=99,
                attraction_index=0,
            )

    def test_attraction_index_out_of_bounds(self):
        with pytest.raises(ValueError, match="attraction_index"):
            EditRequest(
                plan=_make_trip_plan(),
                operation="delete_attraction",
                day_index=0,
                attraction_index=99,
            )

    def test_move_attraction_requires_direction(self):
        with pytest.raises(ValueError, match="direction"):
            EditRequest(
                plan=_make_trip_plan(),
                operation="move_attraction",
                day_index=0,
                attraction_index=0,
            )

    def test_invalid_operation(self):
        with pytest.raises(Exception):
            EditRequest(
                plan=_make_trip_plan(),
                operation="teleport_attraction",
                day_index=0,
                attraction_index=0,
            )

    def test_negative_day_index(self):
        with pytest.raises(ValueError, match="day_index"):
            EditRequest(
                plan=_make_trip_plan(),
                operation="delete_attraction",
                day_index=-1,
                attraction_index=0,
            )

    def test_json_roundtrip(self):
        req = EditRequest(
            plan=_make_trip_plan(),
            operation="delete_attraction",
            day_index=0,
            attraction_index=0,
        )
        restored = EditRequest.model_validate_json(req.model_dump_json())
        assert restored.operation == req.operation
        assert restored.day_index == req.day_index
