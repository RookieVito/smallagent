"""阶段二测试 — OpenAPI/Swagger 结构验证。"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from trip_planner.api import app
    return TestClient(app)


@pytest.fixture(scope="module")
def openapi_schema(client: TestClient) -> dict:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    return resp.json()


class TestOpenAPISchema:
    def test_openapi_json_accessible(self, client: TestClient):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/json"

    def test_has_title_and_version(self, openapi_schema: dict):
        assert openapi_schema["info"]["title"] == "智能旅行助手 API"
        assert openapi_schema["info"]["version"] == "0.1.0"

    def test_has_tags(self, openapi_schema: dict):
        tags = {t["name"] for t in openapi_schema.get("tags", [])}
        assert "健康检查" in tags
        assert "行程规划" in tags

    def test_plan_endpoint_has_description(self, openapi_schema: dict):
        path = openapi_schema["paths"]["/api/trip/plan"]["post"]
        assert path.get("summary") != ""
        assert path.get("description") != ""

    def test_edit_endpoint_has_description(self, openapi_schema: dict):
        path = openapi_schema["paths"]["/api/trip/edit"]["post"]
        assert path.get("summary") != ""
        assert path.get("description") != ""

    def test_plan_endpoint_has_422_response(self, openapi_schema: dict):
        path = openapi_schema["paths"]["/api/trip/plan"]["post"]
        assert "422" in path.get("responses", {})

    def test_plan_endpoint_has_503_response(self, openapi_schema: dict):
        path = openapi_schema["paths"]["/api/trip/plan"]["post"]
        assert "503" in path.get("responses", {})

    def test_error_response_model_defined(self, openapi_schema: dict):
        schemas = openapi_schema.get("components", {}).get("schemas", {})
        assert "ErrorResponse" in schemas
        err = schemas["ErrorResponse"]
        assert "error_code" in err.get("properties", {})
        assert "message" in err.get("properties", {})
        assert "details" in err.get("properties", {})


class TestErrorResponseContract:
    def test_422_response_has_error_code(self, client: TestClient):
        resp = client.post("/api/trip/plan", json={
            "destination": "京都",
            "start_date": "2025-05-05",
            "end_date": "2025-05-01",
            "preferences": ["美食"],
            "budget_level": "moderate",
            "accommodation_type": "hotel",
        })
        assert resp.status_code == 422
        body = resp.json()
        assert body["error_code"] == "VALIDATION_ERROR"
        assert body["message"] != ""
        assert isinstance(body["details"], list)

    def test_503_response_has_error_code(self, client: TestClient):
        from unittest.mock import patch

        with patch(
            "trip_planner.api.run_planner",
            side_effect=RuntimeError("规划失败: 景点服务不可用"),
        ):
            resp = client.post("/api/trip/plan", json={
                "destination": "京都",
                "start_date": "2025-05-01",
                "end_date": "2025-05-04",
                "preferences": ["美食"],
                "budget_level": "moderate",
                "accommodation_type": "hotel",
            })
        assert resp.status_code == 503
        body = resp.json()
        assert body["error_code"] == "PLAN_FAILED"
        assert body["message"] != ""

    def test_422_details_contain_loc_and_msg(self, client: TestClient):
        resp = client.post("/api/trip/plan", json={
            "destination": "京都",
            "start_date": "2025-05-05",
            "end_date": "2025-05-01",
            "preferences": ["美食"],
            "budget_level": "moderate",
            "accommodation_type": "hotel",
        })
        details = resp.json()["details"]
        assert len(details) >= 1
        assert "loc" in details[0]
        assert "msg" in details[0]


class TestModelSchemas:
    def test_trip_plan_schema_has_all_top_level_fields(self, openapi_schema: dict):
        schemas = openapi_schema["components"]["schemas"]
        # FastAPI 生成 response_model 时使用 -Output 后缀
        plan = schemas["TripPlan-Output"]
        props = set(plan["properties"].keys())
        required_fields = {
            "destination", "days", "weather_summary",
            "budget_summary", "map_points", "plan_version",
        }
        optional_fields = {"cover_image_url", "created_at"}
        assert required_fields.issubset(props)
        assert optional_fields.issubset(props)

    def test_attraction_schema_has_image_url(self, openapi_schema: dict):
        schemas = openapi_schema["components"]["schemas"]
        assert "image_url" in schemas["Attraction-Output"]["properties"]

    def test_day_plan_schema_has_cover_image_url(self, openapi_schema: dict):
        schemas = openapi_schema["components"]["schemas"]
        assert "cover_image_url" in schemas["DayPlan-Output"]["properties"]

    def test_budget_breakdown_schema_exists(self, openapi_schema: dict):
        schemas = openapi_schema["components"]["schemas"]
        bb = schemas["BudgetBreakdown-Output"]
        for field in ["accommodation", "dining", "attractions", "transport"]:
            assert field in bb["properties"]

    def test_daily_forecast_schema_exists(self, openapi_schema: dict):
        schemas = openapi_schema["components"]["schemas"]
        df = schemas["DailyForecast"]
        for field in ["date", "condition", "high_celsius", "low_celsius"]:
            assert field in df["properties"]

    def test_edit_request_schema_exists(self, openapi_schema: dict):
        schemas = openapi_schema["components"]["schemas"]
        assert "EditRequest" in schemas
        assert "operation" in schemas["EditRequest"]["properties"]
        assert "day_index" in schemas["EditRequest"]["properties"]
        assert "attraction_index" in schemas["EditRequest"]["properties"]

    def test_field_descriptions_present(self, openapi_schema: dict):
        schemas = openapi_schema["components"]["schemas"]
        trip_plan_desc = schemas["TripPlan-Output"]["properties"]["destination"]
        assert trip_plan_desc.get("description") != ""
