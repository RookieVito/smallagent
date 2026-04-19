from datetime import date

from pydantic import BaseModel, field_validator, model_validator

from .enums import AccommodationType, BudgetLevel


class TripPlanRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    preferences: list[str]
    budget_level: BudgetLevel
    accommodation_type: AccommodationType

    @field_validator("destination")
    @classmethod
    def destination_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("destination 不能为空")
        return v

    @field_validator("preferences")
    @classmethod
    def preferences_not_empty_list(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("preferences 至少需要一项")
        return [p.strip() for p in v if p.strip()]

    @model_validator(mode="after")
    def date_range_valid(self) -> "TripPlanRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date 不能早于 start_date")
        if self.end_date == self.start_date:
            raise ValueError("行程至少需要一天（end_date 须晚于 start_date）")
        return self

    @property
    def trip_days(self) -> int:
        return (self.end_date - self.start_date).days
