"""阶段四测试 — 验证 contract 文档的完整性。"""

import json
import os

import pytest

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "RookieVito")


class TestFieldStabilityDocument:
    def test_file_exists(self):
        path = os.path.join(DOCS_DIR, "02-field-stability.md")
        assert os.path.isfile(path)

    def test_contains_stable_marker(self):
        path = os.path.join(DOCS_DIR, "02-field-stability.md")
        content = open(path, encoding="utf-8").read()
        assert "稳定" in content

    def test_contains_experimental_marker(self):
        path = os.path.join(DOCS_DIR, "02-field-stability.md")
        content = open(path, encoding="utf-8").read()
        assert "实验性" in content

    def test_covers_all_models(self):
        path = os.path.join(DOCS_DIR, "02-field-stability.md")
        content = open(path, encoding="utf-8").read()
        required_models = [
            "TripPlan", "TripPlanRequest", "EditRequest",
            "DayPlan", "Attraction", "BudgetSummary", "WeatherSummary",
            "MapPoint", "DailyForecast", "BudgetBreakdown",
        ]
        for model in required_models:
            assert model in content, f"文档缺少 {model} 的字段说明"

    def test_covers_readonly_and_edit_directions(self):
        path = os.path.join(DOCS_DIR, "02-field-stability.md")
        content = open(path, encoding="utf-8").read()
        assert "只读" in content
        assert "编辑" in content

    def test_answers_export_question(self):
        path = os.path.join(DOCS_DIR, "02-field-stability.md")
        content = open(path, encoding="utf-8").read()
        assert "导出" in content

    def test_answers_image_question(self):
        path = os.path.join(DOCS_DIR, "02-field-stability.md")
        content = open(path, encoding="utf-8").read()
        assert "图片补全" in content


class TestContractChangelog:
    def test_file_exists(self):
        path = os.path.join(DOCS_DIR, "CONTRACT_CHANGELOG.md")
        assert os.path.isfile(path)

    def test_has_initial_version(self):
        path = os.path.join(DOCS_DIR, "CONTRACT_CHANGELOG.md")
        content = open(path, encoding="utf-8").read()
        assert "v0.1.0" in content

    def test_lists_added_fields(self):
        path = os.path.join(DOCS_DIR, "CONTRACT_CHANGELOG.md")
        content = open(path, encoding="utf-8").read()
        assert "image_url" in content
        assert "created_at" in content
        assert "plan_version" in content

    def test_lists_error_codes(self):
        path = os.path.join(DOCS_DIR, "CONTRACT_CHANGELOG.md")
        content = open(path, encoding="utf-8").read()
        assert "VALIDATION_ERROR" in content
        assert "PLAN_FAILED" in content

    def test_lists_api_endpoints(self):
        path = os.path.join(DOCS_DIR, "CONTRACT_CHANGELOG.md")
        content = open(path, encoding="utf-8").read()
        assert "/api/trip/plan" in content
        assert "/api/trip/edit" in content

    def test_marks_experimental_fields(self):
        path = os.path.join(DOCS_DIR, "CONTRACT_CHANGELOG.md")
        content = open(path, encoding="utf-8").read()
        assert "实验性" in content


class TestOpenAPIExportExists:
    def test_openapi_json_exists(self):
        path = os.path.join(DOCS_DIR, "openapi.json")
        assert os.path.isfile(path)

    def test_openapi_json_valid(self):
        path = os.path.join(DOCS_DIR, "openapi.json")
        data = json.load(open(path, encoding="utf-8"))
        assert "openapi" in data
        assert "paths" in data
        assert "components" in data


class TestDeliveryPlanUpdated:
    def test_all_phases_marked_done(self):
        path = os.path.join(DOCS_DIR, "01-delivery-plan.md")
        content = open(path, encoding="utf-8").read()
        assert "阶段一：模型冻结与强化 ✅" in content
        assert "阶段二：OpenAPI/Swagger 完善 ✅" in content
        assert "阶段三：示例 JSON 交付物 ✅" in content
        assert "阶段四：Contract 文档与通知机制 ✅" in content
