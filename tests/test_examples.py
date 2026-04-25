"""阶段三测试 — 验证示例 JSON 文件的完整性和正确性。"""

import json
import os

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError


EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "RookieVito", "examples")


def _load(filename: str) -> dict | list:
    with open(os.path.join(EXAMPLES_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def client():
    from trip_planner.api import app
    return TestClient(app)


class TestTripPlanExamplesExist:
    def test_standard_3days_exists(self):
        _load("trip_plan_standard_3days.json")

    def test_luxury_5days_with_images_exists(self):
        _load("trip_plan_luxury_5days_with_images.json")

    def test_after_edit_exists(self):
        _load("trip_plan_after_edit.json")


class TestTripPlanExamplesCoverage:
    """验证示例 JSON 覆盖交付清单要求的所有展示板块。"""

    @pytest.fixture(params=[
        "trip_plan_standard_3days.json",
        "trip_plan_luxury_5days_with_images.json",
        "trip_plan_after_edit.json",
    ])
    def plan(self, request):
        return _load(request.param)

    def test_has_destination(self, plan: dict):
        assert plan["destination"]

    def test_has_days(self, plan: dict):
        assert isinstance(plan["days"], list)
        assert len(plan["days"]) >= 1

    def test_has_map_points(self, plan: dict):
        assert isinstance(plan["map_points"], list)
        assert len(plan["map_points"]) >= 1
        for pt in plan["map_points"]:
            assert "latitude" in pt
            assert "longitude" in pt

    def test_has_budget_summary(self, plan: dict):
        bs = plan["budget_summary"]
        assert float(bs["estimated_total"]) > 0
        assert "currency" in bs
        assert "breakdown" in bs

    def test_budget_breakdown_has_categories(self, plan: dict):
        bb = plan["budget_summary"]["breakdown"]
        for cat in ["accommodation", "dining", "attractions", "transport"]:
            assert cat in bb

    def test_has_weather_summary(self, plan: dict):
        ws = plan["weather_summary"]
        assert ws["overview"]
        assert isinstance(ws["daily_forecasts"], list)

    def test_weather_forecasts_have_required_fields(self, plan: dict):
        for f in plan["weather_summary"]["daily_forecasts"]:
            assert "date" in f
            assert "condition" in f
            assert "high_celsius" in f
            assert "low_celsius" in f

    def test_has_daily_itinerary(self, plan: dict):
        for day in plan["days"]:
            assert day["attractions"]
            assert day["dining_suggestion"]
            assert day["accommodation_note"]

    def test_attractions_have_coordinates(self, plan: dict):
        for day in plan["days"]:
            for attr in day["attractions"]:
                assert "latitude" in attr
                assert "longitude" in attr
                assert "suggested_duration_minutes" in attr

    def test_has_created_at(self, plan: dict):
        assert plan["created_at"] is not None

    def test_has_plan_version(self, plan: dict):
        assert plan["plan_version"] >= 1

    def test_json_valid_against_pydantic_model(self, plan: dict):
        from trip_planner.models.plan import TripPlan
        validated = TripPlan.model_validate(plan)
        assert validated.destination == plan["destination"]


class TestLuxuryExampleWithImages:
    """验证含图片字段的奢华行程示例。"""

    @pytest.fixture
    def plan(self) -> dict:
        return _load("trip_plan_luxury_5days_with_images.json")

    def test_has_cover_image_url(self, plan: dict):
        assert plan["cover_image_url"] is not None
        assert plan["cover_image_url"].startswith("http")

    def test_days_have_cover_image(self, plan: dict):
        for day in plan["days"]:
            assert day["cover_image_url"] is not None

    def test_attractions_have_image_url(self, plan: dict):
        for day in plan["days"]:
            for attr in day["attractions"]:
                assert attr["image_url"] is not None


class TestEditedPlanExample:
    """验证编辑后行程示例。"""

    @pytest.fixture
    def edited(self) -> dict:
        return _load("trip_plan_after_edit.json")

    @pytest.fixture
    def original(self) -> dict:
        return _load("trip_plan_standard_3days.json")

    def test_version_incremented(self, edited: dict, original: dict):
        assert edited["plan_version"] == original["plan_version"] + 1

    def test_destination_unchanged(self, edited: dict, original: dict):
        assert edited["destination"] == original["destination"]

    def test_attraction_count_decreased(self, edited: dict, original: dict):
        original_count = len(original["days"][0]["attractions"])
        edited_count = len(edited["days"][0]["attractions"])
        assert edited_count == original_count - 1


class TestRequestExamples:
    def test_request_examples_exist(self):
        data = _load("trip_plan_request_examples.json")
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_request_examples_validatable(self):
        from trip_planner.models.request import TripPlanRequest
        data = _load("trip_plan_request_examples.json")
        for req in data:
            TripPlanRequest.model_validate(req)


class TestEditRequestExamples:
    def test_edit_examples_exist(self):
        data = _load("edit_request_examples.json")
        assert isinstance(data, dict)
        assert "delete_attraction" in data
        assert "move_attraction_up" in data
        assert "move_attraction_down" in data

    def test_edit_examples_validatable(self):
        from trip_planner.models.edit import EditRequest
        data = _load("edit_request_examples.json")
        for key, req in data.items():
            EditRequest.model_validate(req)


class TestErrorExamples:
    def test_error_examples_exist(self):
        data = _load("error_response_examples.json")
        assert isinstance(data, dict)

    def test_each_error_has_required_fields(self):
        data = _load("error_response_examples.json")
        for key, err in data.items():
            assert "error_code" in err, f"{key} missing error_code"
            assert "message" in err, f"{key} missing message"


class TestExamplesAgainstLiveAPI:
    """验证示例请求通过真实 API 能产生有效响应。"""

    def test_standard_request_produces_valid_response(self, client: TestClient):
        req = _load("trip_plan_request_examples.json")[0]
        resp = client.post("/api/trip/plan", json=req)
        assert resp.status_code == 200
        data = resp.json()
        assert data["destination"] == req["destination"]

    def test_edit_request_produces_valid_response(self, client: TestClient):
        data = _load("edit_request_examples.json")
        resp = client.post("/api/trip/edit", json=data["delete_attraction"])
        assert resp.status_code == 200
        assert "days" in resp.json()
