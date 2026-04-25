from datetime import date

import pytest

from trip_planner.models import TripPlanRequest
from trip_planner.models.enums import AccommodationType, BudgetLevel


def test_valid_request():
    req = TripPlanRequest(
        destination="京都",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 5),
        preferences=["历史文化", "美食"],
        budget_level=BudgetLevel.MODERATE,
        accommodation_type=AccommodationType.HOTEL,
    )
    assert req.trip_days == 4


def test_end_before_start_raises():
    with pytest.raises(ValueError, match="end_date"):
        TripPlanRequest(
            destination="京都",
            start_date=date(2025, 5, 5),
            end_date=date(2025, 5, 1),
            preferences=["美食"],
            budget_level=BudgetLevel.BUDGET,
            accommodation_type=AccommodationType.ANY,
        )


def test_same_day_raises():
    with pytest.raises(ValueError):
        TripPlanRequest(
            destination="京都",
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 1),
            preferences=["美食"],
            budget_level=BudgetLevel.BUDGET,
            accommodation_type=AccommodationType.ANY,
        )


def test_empty_destination_raises():
    with pytest.raises(ValueError, match="destination"):
        TripPlanRequest(
            destination="   ",
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 5),
            preferences=["美食"],
            budget_level=BudgetLevel.BUDGET,
            accommodation_type=AccommodationType.ANY,
        )


def test_json_roundtrip():
    req = TripPlanRequest(
        destination="京都",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 5),
        preferences=["历史文化"],
        budget_level=BudgetLevel.LUXURY,
        accommodation_type=AccommodationType.RESORT,
    )
    restored = TripPlanRequest.model_validate_json(req.model_dump_json())
    assert restored == req
