from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class Attraction(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    suggested_duration_minutes: int
    ticket_price: Decimal | None = None


class DayPlan(BaseModel):
    date: date
    attractions: list[Attraction]
    dining_suggestion: str
    accommodation_note: str


class MapPoint(BaseModel):
    name: str
    latitude: float
    longitude: float
    category: str = ""


class BudgetSummary(BaseModel):
    estimated_total: Decimal
    currency: str = "CNY"
    breakdown: dict[str, Decimal] = Field(default_factory=dict)
    notes: str = ""


class WeatherSummary(BaseModel):
    overview: str
    daily_forecasts: list[dict] = Field(default_factory=list)


class TripPlan(BaseModel):
    destination: str
    days: list[DayPlan]
    weather_summary: WeatherSummary
    budget_summary: BudgetSummary
    map_points: list[MapPoint]
