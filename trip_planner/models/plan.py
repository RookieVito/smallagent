from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class Attraction(BaseModel):
    """单个景点信息。"""

    name: str = Field(description="景点名称")
    address: str = Field(description="景点地址")
    latitude: float = Field(description="纬度")
    longitude: float = Field(description="经度")
    suggested_duration_minutes: int = Field(description="建议游览时长（分钟）")
    ticket_price: Decimal | None = Field(default=None, description="门票价格，免费景点为 null")
    image_url: str | None = Field(default=None, description="景点图片 URL，未补全时为 null")


class DailyForecast(BaseModel):
    """每日天气预报。"""

    date: str = Field(description="日期，格式 YYYY-MM-DD")
    condition: str = Field(description="天气状况，如 晴/多云/小雨")
    high_celsius: int = Field(description="最高温度（摄氏度）")
    low_celsius: int = Field(description="最低温度（摄氏度）")


class DayPlan(BaseModel):
    """单日行程安排。"""

    date: Annotated[date, Field(description="日期")]
    attractions: list[Attraction] = Field(description="当日景点列表")
    dining_suggestion: str = Field(description="餐饮建议")
    accommodation_note: str = Field(description="住宿说明")
    cover_image_url: str | None = Field(default=None, description="当日封面图片 URL，未补全时为 null")


class MapPoint(BaseModel):
    """地图标记点。"""

    name: str = Field(description="标记点名称")
    latitude: float = Field(description="纬度")
    longitude: float = Field(description="经度")
    category: str = Field(default="", description="分类标签，如 attraction/restaurant/hotel")


class BudgetBreakdown(BaseModel):
    """预算细分明细。"""

    accommodation: Decimal = Field(description="住宿费用")
    dining: Decimal = Field(description="餐饮费用")
    attractions: Decimal = Field(description="景点门票费用")
    transport: Decimal = Field(description="交通费用")


class BudgetSummary(BaseModel):
    """预算汇总。"""

    estimated_total: Decimal = Field(description="预估总费用")
    currency: str = Field(default="CNY", description="货币代码")
    breakdown: BudgetBreakdown = Field(description="预算明细")


class WeatherSummary(BaseModel):
    """天气汇总。"""

    overview: str = Field(description="天气概述")
    daily_forecasts: list[DailyForecast] = Field(default_factory=list, description="每日天气预报列表")


class TripPlan(BaseModel):
    """完整旅行计划。"""

    destination: str = Field(description="目的地名称")
    days: list[DayPlan] = Field(description="每日行程列表")
    weather_summary: WeatherSummary = Field(description="天气汇总")
    budget_summary: BudgetSummary = Field(description="预算汇总")
    map_points: list[MapPoint] = Field(description="地图标记点列表")
    cover_image_url: str | None = Field(default=None, description="行程封面图片 URL，未补全时为 null")
    created_at: datetime | None = Field(default=None, description="计划创建时间，由服务端生成")
    plan_version: int = Field(default=1, description="计划版本号，每次编辑递增")
