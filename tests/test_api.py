"""FastAPI 后端 API 测试 — 覆盖 plan 端点、edit 端点和健康检查。"""

from datetime import date

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from trip_planner.api import app
    return TestClient(app)


def _valid_payload(**overrides) -> dict:
    base = {
        "destination": "京都",
        "start_date": "2025-05-01",
        "end_date": "2025-05-04",
        "preferences": ["历史文化", "美食"],
        "budget_level": "moderate",
        "accommodation_type": "hotel",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 正常路径
# ---------------------------------------------------------------------------

class TestPlanEndpointSuccess:
    def test_returns_200(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        assert resp.status_code == 200

    def test_response_has_destination(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        assert resp.json()["destination"] == "京都"

    def test_response_has_days(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        data = resp.json()
        assert "days" in data
        assert isinstance(data["days"], list)
        assert len(data["days"]) > 0

    def test_days_count_matches_trip_duration(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        assert len(resp.json()["days"]) == 3

    def test_response_has_weather_summary(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        data = resp.json()
        assert "weather_summary" in data
        assert data["weather_summary"]["overview"] != ""

    def test_response_has_budget_summary(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        data = resp.json()
        assert "budget_summary" in data
        assert float(data["budget_summary"]["estimated_total"]) > 0

    def test_response_has_map_points(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        data = resp.json()
        assert "map_points" in data
        assert len(data["map_points"]) >= 1

    def test_each_day_has_required_fields(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        for day in resp.json()["days"]:
            assert "date" in day
            assert "attractions" in day
            assert "dining_suggestion" in day
            assert "accommodation_note" in day

    def test_each_attraction_has_coordinates(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        for day in resp.json()["days"]:
            for attr in day["attractions"]:
                assert "latitude" in attr
                assert "longitude" in attr

    def test_budget_currency_is_cny(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        assert resp.json()["budget_summary"]["currency"] == "CNY"

    def test_budget_breakdown_is_strong_type(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        breakdown = resp.json()["budget_summary"]["breakdown"]
        assert isinstance(breakdown, dict)
        assert "accommodation" in breakdown
        assert "dining" in breakdown
        assert "attractions" in breakdown
        assert "transport" in breakdown

    def test_weather_daily_forecasts_are_strong_type(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        forecasts = resp.json()["weather_summary"]["daily_forecasts"]
        assert isinstance(forecasts, list)
        for f in forecasts:
            assert "date" in f
            assert "condition" in f
            assert "high_celsius" in f
            assert "low_celsius" in f

    def test_luxury_budget_higher_than_budget_level(self, client: TestClient):
        r_budget = client.post("/api/trip/plan", json=_valid_payload(budget_level="budget"))
        r_luxury = client.post("/api/trip/plan", json=_valid_payload(budget_level="luxury"))
        assert r_luxury.status_code == 200
        total_budget = float(r_budget.json()["budget_summary"]["estimated_total"])
        total_luxury = float(r_luxury.json()["budget_summary"]["estimated_total"])
        assert total_luxury > total_budget

    def test_content_type_is_json(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        assert "application/json" in resp.headers["content-type"]

    def test_response_has_created_at(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        data = resp.json()
        assert "created_at" in data
        assert data["created_at"] is not None

    def test_response_has_plan_version(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        data = resp.json()
        assert "plan_version" in data
        assert data["plan_version"] == 1

    def test_response_has_cover_image_url_null(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        data = resp.json()
        assert "cover_image_url" in data
        assert data["cover_image_url"] is None

    def test_attraction_has_image_url_null(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        for day in resp.json()["days"]:
            for attr in day["attractions"]:
                assert "image_url" in attr

    def test_day_has_cover_image_url_null(self, client: TestClient):
        resp = client.post("/api/trip/plan", json=_valid_payload())
        for day in resp.json()["days"]:
            assert "cover_image_url" in day


# ---------------------------------------------------------------------------
# 请求验证失败 → 422
# ---------------------------------------------------------------------------

class TestPlanEndpointValidation:
    def test_missing_destination_returns_422(self, client: TestClient):
        payload = _valid_payload()
        del payload["destination"]
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_missing_start_date_returns_422(self, client: TestClient):
        payload = _valid_payload()
        del payload["start_date"]
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_missing_end_date_returns_422(self, client: TestClient):
        payload = _valid_payload()
        del payload["end_date"]
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_missing_preferences_returns_422(self, client: TestClient):
        payload = _valid_payload()
        del payload["preferences"]
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_missing_budget_level_returns_422(self, client: TestClient):
        payload = _valid_payload()
        del payload["budget_level"]
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_missing_accommodation_type_returns_422(self, client: TestClient):
        payload = _valid_payload()
        del payload["accommodation_type"]
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_end_before_start_returns_422(self, client: TestClient):
        payload = _valid_payload(start_date="2025-05-05", end_date="2025-05-01")
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_same_day_returns_422(self, client: TestClient):
        payload = _valid_payload(start_date="2025-05-01", end_date="2025-05-01")
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_empty_destination_returns_422(self, client: TestClient):
        payload = _valid_payload(destination="   ")
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_empty_preferences_list_returns_422(self, client: TestClient):
        payload = _valid_payload(preferences=[])
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_invalid_budget_level_returns_422(self, client: TestClient):
        payload = _valid_payload(budget_level="ultra_rich")
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_invalid_accommodation_type_returns_422(self, client: TestClient):
        payload = _valid_payload(accommodation_type="treehouse")
        assert client.post("/api/trip/plan", json=payload).status_code == 422

    def test_422_has_structured_error_format(self, client: TestClient):
        payload = _valid_payload(budget_level="invalid")
        resp = client.post("/api/trip/plan", json=payload)
        body = resp.json()
        assert resp.status_code == 422
        assert "error_code" in body
        assert "message" in body
        assert "details" in body
        assert body["error_code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# 健康检查端点
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient):
        assert client.get("/health").status_code == 200

    def test_health_response_body(self, client: TestClient):
        resp = client.get("/health")
        assert resp.json()["status"] == "ok"
