import operator
from typing import Annotated

from pydantic import BaseModel, Field

from .plan import TripPlan
from .request import TripPlanRequest


class PlannerState(BaseModel):
    request: TripPlanRequest | None = None
    candidate_attractions: list[dict] = Field(default_factory=list)
    weather_data: dict = Field(default_factory=dict)
    hotel_candidates: list[dict] = Field(default_factory=list)
    trip_plan: TripPlan | None = None
    errors: Annotated[list[str], operator.add] = Field(default_factory=list)
