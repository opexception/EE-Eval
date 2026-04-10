from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.evaluation import Evaluation


class EvaluationCreateRequest(BaseModel):
    employee_id: int = Field(gt=0)
    review_cycle_id: int = Field(gt=0)
    performance_rating: Decimal = Field(ge=0, le=5)
    potential_rating: int = Field(ge=1, le=3)
    summary_comment: str | None = Field(default=None, max_length=4000)
    status: str = Field(min_length=1, max_length=40)


class EvaluationUpdateRequest(BaseModel):
    performance_rating: Decimal | None = Field(default=None, ge=0, le=5)
    potential_rating: int | None = Field(default=None, ge=1, le=3)
    summary_comment: str | None = Field(default=None, max_length=4000)
    status: str | None = Field(default=None, min_length=1, max_length=40)


class EvaluationResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    review_cycle_id: int
    review_cycle_name: str
    author_user_id: int
    updated_by_user_id: int
    performance_rating: float
    potential_rating: int
    summary_comment: str | None
    status: str

    @classmethod
    def from_evaluation(cls, evaluation: Evaluation) -> "EvaluationResponse":
        return cls(
            id=evaluation.id,
            employee_id=evaluation.employee_id,
            employee_name=evaluation.employee.full_name,
            review_cycle_id=evaluation.review_cycle_id,
            review_cycle_name=evaluation.review_cycle.name,
            author_user_id=evaluation.author_user_id,
            updated_by_user_id=evaluation.updated_by_user_id,
            performance_rating=float(evaluation.performance_rating),
            potential_rating=evaluation.potential_rating,
            summary_comment=evaluation.summary_comment,
            status=evaluation.status,
        )
