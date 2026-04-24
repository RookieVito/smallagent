"""
V0 验收测试 — 覆盖四个验收标准：

1. 用户能提交结构化旅行请求
2. 后端基于 LangGraph 工作流生成完整 TripPlan
3. 前端所需的五个展示板块字段完整（行程概览、预算、地图、每日行程、天气摘要）
4. 用户能对单日景点做删除与顺序调整，并看到结果刷新
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from trip_planner.api import app
    return TestClient(app)


@pytest.fixture(scope="module")
def trip_plan(client: TestClient) -> dict:
    resp = client.post("/api/trip/plan", json={
        "destination": "北京",
        "start_date": "2025-06-01",
        "end_date": "2025-06-04",
        "preferences": ["历史文化", "美食"],
        "budget_level": "moderate",
        "accommodation_type": "hotel",
    })
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# 验收标准 1：用户能提交结构化旅行请求
# ---------------------------------------------------------------------------

class TestAcceptance1_SubmitRequest:
    def test_plan_endpoint_accepts_valid_request(self, client: TestClient):
        resp = client.post("/api/trip/plan", json={
            "destination": "上海",
            "start_date": "2025-07-01",
            "end_date": "2025-07-03",
            "preferences": ["购物"],
            "budget_level": "budget",
            "accommodation_type": "hostel",
        })
        assert resp.status_code == 200

    def test_plan_endpoint_rejects_incomplete_request(self, client: TestClient):
        resp = client.post("/api/trip/plan", json={"destination": "上海"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 验收标准 2：后端生成完整 TripPlan
# ---------------------------------------------------------------------------

class TestAcceptance2_GenerateTripPlan:
    def test_response_is_trip_plan(self, trip_plan: dict):
        assert trip_plan["destination"] == "北京"

    def test_trip_plan_has_days(self, trip_plan: dict):
        assert len(trip_plan["days"]) == 3

    def test_each_day_has_date(self, trip_plan: dict):
        for day in trip_plan["days"]:
            assert "date" in day

    def test_each_day_has_attractions(self, trip_plan: dict):
        for day in trip_plan["days"]:
            assert len(day["attractions"]) >= 1

    def test_each_attraction_has_coordinates(self, trip_plan: dict):
        for day in trip_plan["days"]:
            for attr in day["attractions"]:
                assert isinstance(attr["latitude"], float)
                assert isinstance(attr["longitude"], float)


# ---------------------------------------------------------------------------
# 验收标准 3：前端五个展示板块字段完整
# ---------------------------------------------------------------------------

class TestAcceptance3_DisplayFields:
    def test_has_itinerary_overview(self, trip_plan: dict):
        assert trip_plan["destination"]
        assert trip_plan["days"]

    def test_has_budget_summary(self, trip_plan: dict):
        b = trip_plan["budget_summary"]
        assert float(b["estimated_total"]) > 0
        assert b["currency"] == "CNY"
        assert b["breakdown"]

    def test_budget_breakdown_has_all_categories(self, trip_plan: dict):
        bb = trip_plan["budget_summary"]["breakdown"]
        assert "accommodation" in bb
        assert "dining" in bb
        assert "attractions" in bb
        assert "transport" in bb

    def test_has_map_points(self, trip_plan: dict):
        assert len(trip_plan["map_points"]) >= 1
        for pt in trip_plan["map_points"]:
            assert "latitude" in pt and "longitude" in pt and "name" in pt

    def test_has_daily_itinerary(self, trip_plan: dict):
        for day in trip_plan["days"]:
            assert day["attractions"]
            assert day["dining_suggestion"]
            assert day["accommodation_note"]

    def test_has_weather_summary(self, trip_plan: dict):
        assert trip_plan["weather_summary"]["overview"] != ""

    def test_has_weather_daily_forecasts(self, trip_plan: dict):
        forecasts = trip_plan["weather_summary"]["daily_forecasts"]
        assert len(forecasts) >= 1
        for f in forecasts:
            assert "date" in f
            assert "condition" in f


# ---------------------------------------------------------------------------
# 验收标准 4：用户能对单日景点做删除与顺序调整
# ---------------------------------------------------------------------------

class TestAcceptance4_EditItinerary:
    def test_edit_endpoint_exists(self, client: TestClient):
        resp = client.post("/api/trip/edit", json={})
        assert resp.status_code != 404
        assert resp.status_code != 405

    def test_delete_attraction_removes_it(self, client: TestClient, trip_plan: dict):
        original_count = len(trip_plan["days"][0]["attractions"])
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 0,
            "attraction_index": 0,
        })
        assert resp.status_code == 200
        edited = resp.json()
        assert len(edited["days"][0]["attractions"]) == original_count - 1

    def test_move_attraction_up_changes_order(self, client: TestClient, trip_plan: dict):
        day = trip_plan["days"][0]
        if len(day["attractions"]) < 2:
            pytest.skip("第 0 天景点不足 2 个，跳过顺序测试")

        name_before = day["attractions"][1]["name"]
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "move_attraction",
            "day_index": 0,
            "attraction_index": 1,
            "direction": "up",
        })
        assert resp.status_code == 200
        edited = resp.json()
        assert edited["days"][0]["attractions"][0]["name"] == name_before

    def test_move_attraction_down_changes_order(self, client: TestClient, trip_plan: dict):
        day = trip_plan["days"][0]
        if len(day["attractions"]) < 2:
            pytest.skip("第 0 天景点不足 2 个，跳过顺序测试")

        name_before = day["attractions"][0]["name"]
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "move_attraction",
            "day_index": 0,
            "attraction_index": 0,
            "direction": "down",
        })
        assert resp.status_code == 200
        edited = resp.json()
        assert edited["days"][0]["attractions"][1]["name"] == name_before

    def test_edit_returns_full_trip_plan(self, client: TestClient, trip_plan: dict):
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 0,
            "attraction_index": 0,
        })
        assert resp.status_code == 200
        edited = resp.json()
        assert "destination" in edited
        assert "weather_summary" in edited
        assert "budget_summary" in edited
        assert "map_points" in edited

    def test_edit_invalid_operation_returns_422(self, client: TestClient, trip_plan: dict):
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "teleport_attraction",
            "day_index": 0,
            "attraction_index": 0,
        })
        assert resp.status_code == 422

    def test_edit_out_of_bounds_day_returns_422(self, client: TestClient, trip_plan: dict):
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 999,
            "attraction_index": 0,
        })
        assert resp.status_code == 422

    def test_edit_out_of_bounds_attraction_returns_422(self, client: TestClient, trip_plan: dict):
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 0,
            "attraction_index": 999,
        })
        assert resp.status_code == 422

    def test_edit_does_not_mutate_original(self, client: TestClient, trip_plan: dict):
        original_count = len(trip_plan["days"][0]["attractions"])
        client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 0,
            "attraction_index": 0,
        })
        assert len(trip_plan["days"][0]["attractions"]) == original_count

    def test_edit_increments_plan_version(self, client: TestClient, trip_plan: dict):
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 0,
            "attraction_index": 0,
        })
        edited = resp.json()
        assert edited["plan_version"] == trip_plan["plan_version"] + 1


# ---------------------------------------------------------------------------
# 验收标准：V0 非目标不得出现在响应中
# ---------------------------------------------------------------------------

class TestAcceptanceNonGoals:
    def test_no_user_account_field_in_response(self, trip_plan: dict):
        assert "user_id" not in trip_plan
        assert "saved" not in trip_plan
