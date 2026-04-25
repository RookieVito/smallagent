from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .plan import TripPlan


class EditRequest(BaseModel):
    """行程编辑请求体。"""

    plan: TripPlan = Field(description="当前完整行程计划")
    operation: Literal["delete_attraction", "move_attraction"] = Field(
        description="编辑操作：delete_attraction（删除景点）或 move_attraction（移动景点顺序）"
    )
    day_index: int = Field(description="目标天数索引（从 0 开始）")
    attraction_index: int = Field(description="目标景点索引（从 0 开始）")
    direction: Literal["up", "down"] | None = Field(
        default=None, description="移动方向，仅 move_attraction 操作时必填"
    )

    @model_validator(mode="after")
    def validate_bounds_and_direction(self) -> "EditRequest":
        days = self.plan.days
        if self.day_index < 0 or self.day_index >= len(days):
            raise ValueError(
                f"day_index {self.day_index} 越界（共 {len(days)} 天）"
            )
        attractions = days[self.day_index].attractions
        if self.attraction_index < 0 or self.attraction_index >= len(attractions):
            raise ValueError(
                f"attraction_index {self.attraction_index} 越界（第 {self.day_index} 天共 {len(attractions)} 个景点）"
            )
        if self.operation == "move_attraction" and self.direction is None:
            raise ValueError("move_attraction 操作必须提供 direction")
        return self
