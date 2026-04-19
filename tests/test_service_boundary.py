"""
外部服务边界测试 — TDD 绿阶段

验证三条核心规则（来自 external-service-boundary.md）：
1. 主链路依赖（景点、天气）失败 → API 返回 503，不伪造结果
2. 可降级依赖（酒店）失败 → API 仍返回 200，结果中有降级说明
3. 增强依赖（图片等）失败 → API 仍返回 200，核心字段完整

通过 Services 注入 mock，不依赖 patch。
"""

import pytest
from fastapi.testclient import TestClient

from trip_planner.models.request import TripPlanRequest
from trip_planner.workflow import Services


@pytest.fixture(scope="module")
def client():
    from trip_planner.api import app
    return TestClient(app, raise_server_exceptions=False)


def _valid_payload(**overrides) -> dict:
    base = {
        "destination": "京都",
        "start_date": "2025-05-01",
        "end_date": "2025-05-04",
        "preferences": ["历史文化"],
        "budget_level": "moderate",
        "accommodation_type": "hotel",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 通过 run_planner 直接测试服务注入（不走 HTTP 层）
# ---------------------------------------------------------------------------

from trip_planner.workflow import run_planner
from trip_planner.models.plan import TripPlan
from datetime import date


def _req(**overrides) -> TripPlanRequest:
    from trip_planner.models.enums import BudgetLevel, AccommodationType
    base = dict(
        destination="京都",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 4),
        preferences=["历史文化"],
        budget_level=BudgetLevel.MODERATE,
        accommodation_type=AccommodationType.HOTEL,
    )
    base.update(overrides)
    return TripPlanRequest(**base)


class TestMainChainFailureViaServices:
    def test_attractions_failure_raises_runtime_error(self):
        """景点检索返回空列表 → run_planner 抛出 RuntimeError。"""
        svc = Services(fetch_attractions=lambda req: [])
        with pytest.raises(RuntimeError, match="规划失败"):
            run_planner(_req(), services=svc)

    def test_weather_failure_raises_runtime_error(self):
        """天气查询返回空 dict → run_planner 抛出 RuntimeError。"""
        svc = Services(fetch_weather=lambda req: {})
        with pytest.raises(RuntimeError, match="规划失败"):
            run_planner(_req(), services=svc)

    def test_error_message_mentions_missing_data(self):
        """RuntimeError 消息中包含缺失素材的说明。"""
        svc = Services(fetch_attractions=lambda req: [])
        with pytest.raises(RuntimeError) as exc_info:
            run_planner(_req(), services=svc)
        assert "candidate_attractions" in str(exc_info.value)


class TestDegradableFailureViaServices:
    def test_hotels_failure_still_returns_plan(self):
        """酒店返回空列表 → 仍然产出 TripPlan（降级）。"""
        svc = Services(fetch_hotels=lambda req: [])
        plan = run_planner(_req(), services=svc)
        assert isinstance(plan, TripPlan)

    def test_hotels_failure_accommodation_note_degraded(self):
        """酒店失败时 accommodation_note 包含目的地名称（降级说明）。"""
        svc = Services(fetch_hotels=lambda req: [])
        plan = run_planner(_req(), services=svc)
        assert "京都" in plan.days[0].accommodation_note

    def test_hotels_failure_core_fields_intact(self):
        """酒店失败时 weather_summary、budget_summary、map_points 仍完整。"""
        svc = Services(fetch_hotels=lambda req: [])
        plan = run_planner(_req(), services=svc)
        assert plan.weather_summary.overview != ""
        assert plan.budget_summary.estimated_total > 0
        assert len(plan.map_points) >= 1


# ---------------------------------------------------------------------------
# HTTP 层：主链路失败 → 503
# ---------------------------------------------------------------------------

class TestMainChainFailureViaAPI:
    def test_attractions_failure_returns_503(self, client: TestClient):
        """景点检索失败（主链路）→ 503，不返回伪造的 TripPlan。"""
        from unittest.mock import patch
        with patch("trip_planner.api.run_planner", side_effect=RuntimeError("规划失败: 景点服务不可用")):
            resp = client.post("/api/trip/plan", json=_valid_payload())
        assert resp.status_code == 503

    def test_503_body_contains_detail(self, client: TestClient):
        """503 响应体必须包含 detail 字段。"""
        from unittest.mock import patch
        with patch("trip_planner.api.run_planner", side_effect=RuntimeError("规划失败: 景点服务不可用")):
            resp = client.post("/api/trip/plan", json=_valid_payload())
        assert "detail" in resp.json()

    def test_503_does_not_return_trip_plan_fields(self, client: TestClient):
        """503 响应体不包含 days 或 trip_plan 字段。"""
        from unittest.mock import patch
        with patch("trip_planner.api.run_planner", side_effect=RuntimeError("规划失败: 景点服务不可用")):
            resp = client.post("/api/trip/plan", json=_valid_payload())
        body = resp.json()
        assert "days" not in body
        assert "trip_plan" not in body


# ---------------------------------------------------------------------------
# 服务边界：响应只包含契约定义的字段
# ---------------------------------------------------------------------------

class TestServiceFieldBoundary:
    def test_response_contains_only_defined_top_level_fields(self, client: TestClient):
        """响应体只包含 TripPlan 契约中定义的顶层字段。"""
        resp = client.post("/api/trip/plan", json=_valid_payload())
        allowed = {"destination", "days", "weather_summary", "budget_summary", "map_points"}
        extra = set(resp.json().keys()) - allowed
        assert extra == set(), f"响应包含未定义字段: {extra}"

    def test_attraction_contains_only_defined_fields(self, client: TestClient):
        """景点对象只包含 Attraction 契约中定义的字段。"""
        resp = client.post("/api/trip/plan", json=_valid_payload())
        allowed = {"name", "address", "latitude", "longitude",
                   "suggested_duration_minutes", "ticket_price"}
        for day in resp.json()["days"]:
            for attr in day["attractions"]:
                extra = set(attr.keys()) - allowed
                assert extra == set(), f"景点包含未定义字段: {extra}"
