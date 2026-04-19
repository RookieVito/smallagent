"""
V0 验收测试 — TDD 红阶段

把 v0-acceptance-and-non-goals.md 的通过标准逐条翻译为可执行断言：

1. 用户能提交结构化旅行请求
2. 后端基于 LangGraph 工作流生成完整 TripPlan
3. 前端所需的五个展示板块字段完整（行程概览、预算、地图、每日行程、天气摘要）
4. 用户能对单日景点做删除与顺序调整，并看到结果刷新

第 4 条需要 POST /api/trip/edit 端点，目前不存在 → 红阶段。
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from trip_planner.api import app
    return TestClient(app)


@pytest.fixture(scope="module")
def trip_plan(client: TestClient) -> dict:
    """生成一次规划结果，供多个验收测试复用。"""
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
        assert len(trip_plan["days"]) == 3  # 06-01 到 06-04 = 3 天

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
        """行程概览：destination + days 非空。"""
        assert trip_plan["destination"]
        assert trip_plan["days"]

    def test_has_budget_summary(self, trip_plan: dict):
        """预算板块：estimated_total > 0，有 breakdown，有 currency。"""
        b = trip_plan["budget_summary"]
        assert float(b["estimated_total"]) > 0
        assert b["currency"] == "CNY"
        assert b["breakdown"]

    def test_has_map_points(self, trip_plan: dict):
        """地图板块：map_points 非空，每个点有经纬度和名称。"""
        assert len(trip_plan["map_points"]) >= 1
        for pt in trip_plan["map_points"]:
            assert "latitude" in pt and "longitude" in pt and "name" in pt

    def test_has_daily_itinerary(self, trip_plan: dict):
        """每日行程板块：每天有景点、餐饮建议、住宿说明。"""
        for day in trip_plan["days"]:
            assert day["attractions"]
            assert day["dining_suggestion"]
            assert day["accommodation_note"]

    def test_has_weather_summary(self, trip_plan: dict):
        """天气摘要板块：overview 非空字符串。"""
        assert trip_plan["weather_summary"]["overview"] != ""


# ---------------------------------------------------------------------------
# 验收标准 4：用户能对单日景点做删除与顺序调整
# ---------------------------------------------------------------------------

class TestAcceptance4_EditItinerary:
    def test_edit_endpoint_exists(self, client: TestClient):
        """POST /api/trip/edit 端点必须存在（不返回 404/405）。"""
        resp = client.post("/api/trip/edit", json={})
        assert resp.status_code != 404
        assert resp.status_code != 405

    def test_delete_attraction_removes_it(self, client: TestClient, trip_plan: dict):
        """删除第 0 天第 0 个景点后，该天景点数量减少 1。"""
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
        """把第 0 天第 1 个景点上移后，它变成第 0 个。"""
        # 确保第 0 天有至少 2 个景点（通过多天规划保证）
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
        """把第 0 天第 0 个景点下移后，它变成第 1 个。"""
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
        """编辑后返回完整的 TripPlan 结构（不只是被修改的 day）。"""
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
        """不支持的 operation 返回 422。"""
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "teleport_attraction",
            "day_index": 0,
            "attraction_index": 0,
        })
        assert resp.status_code == 422

    def test_edit_out_of_bounds_day_returns_422(self, client: TestClient, trip_plan: dict):
        """day_index 越界返回 422。"""
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 999,
            "attraction_index": 0,
        })
        assert resp.status_code == 422

    def test_edit_out_of_bounds_attraction_returns_422(self, client: TestClient, trip_plan: dict):
        """attraction_index 越界返回 422。"""
        resp = client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 0,
            "attraction_index": 999,
        })
        assert resp.status_code == 422

    def test_edit_does_not_mutate_original(self, client: TestClient, trip_plan: dict):
        """编辑操作不修改传入的 plan，返回新对象。"""
        original_count = len(trip_plan["days"][0]["attractions"])
        client.post("/api/trip/edit", json={
            "plan": trip_plan,
            "operation": "delete_attraction",
            "day_index": 0,
            "attraction_index": 0,
        })
        # 原始 fixture 中的景点数量不变
        assert len(trip_plan["days"][0]["attractions"]) == original_count


# ---------------------------------------------------------------------------
# 验收标准：V0 非目标不得出现在响应中
# ---------------------------------------------------------------------------

class TestAcceptanceNonGoals:
    def test_no_export_field_in_response(self, trip_plan: dict):
        """响应中不包含导出相关字段（V0 非目标）。"""
        assert "export_url" not in trip_plan
        assert "pdf_url" not in trip_plan
        assert "image_url" not in trip_plan

    def test_no_user_account_field_in_response(self, trip_plan: dict):
        """响应中不包含账号体系字段（V0 非目标）。"""
        assert "user_id" not in trip_plan
        assert "saved" not in trip_plan
