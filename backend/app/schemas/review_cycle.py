from datetime import date

from pydantic import BaseModel, Field

from app.models.review_cycle import ReviewCycle


class ReviewCycleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    cycle_type: str = Field(min_length=1, max_length=40)
    start_date: date
    end_date: date
    status: str = Field(min_length=1, max_length=40)


class ReviewCycleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    cycle_type: str | None = Field(default=None, min_length=1, max_length=40)
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(default=None, min_length=1, max_length=40)


class ReviewCycleResponse(BaseModel):
    id: int
    name: str
    cycle_type: str
    start_date: date
    end_date: date
    status: str
    created_by_user_id: int
    updated_by_user_id: int

    @classmethod
    def from_review_cycle(cls, review_cycle: ReviewCycle) -> "ReviewCycleResponse":
        return cls(
            id=review_cycle.id,
            name=review_cycle.name,
            cycle_type=review_cycle.cycle_type,
            start_date=review_cycle.start_date,
            end_date=review_cycle.end_date,
            status=review_cycle.status,
            created_by_user_id=review_cycle.created_by_user_id,
            updated_by_user_id=review_cycle.updated_by_user_id,
        )
