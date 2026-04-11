from pydantic import BaseModel

from app.models.evaluation import Evaluation
from app.models.review_cycle import ReviewCycle


class NineBoxEmployeeSummary(BaseModel):
    employee_id: int
    employee_number: str
    employee_name: str
    job_title: str
    department: str
    manager_name: str | None
    is_active: bool
    evaluation_id: int
    performance_rating: float
    potential_rating: int
    performance_tier: str
    potential_tier: str
    nine_box_code: str
    nine_box_label: str
    summary_comment: str | None
    evaluation_status: str

    @classmethod
    def from_evaluation(cls, evaluation: Evaluation) -> "NineBoxEmployeeSummary":
        manager_name = (
            evaluation.employee.manager.full_name
            if evaluation.employee.manager is not None
            else None
        )
        return cls(
            employee_id=evaluation.employee_id,
            employee_number=evaluation.employee.employee_number,
            employee_name=evaluation.employee.full_name,
            job_title=evaluation.employee.job_title,
            department=evaluation.employee.department,
            manager_name=manager_name,
            is_active=evaluation.employee.is_active,
            evaluation_id=evaluation.id,
            performance_rating=float(evaluation.performance_rating),
            potential_rating=evaluation.potential_rating,
            performance_tier=evaluation.performance_tier,
            potential_tier=evaluation.potential_tier,
            nine_box_code=evaluation.nine_box_code,
            nine_box_label=evaluation.nine_box_label,
            summary_comment=evaluation.summary_comment,
            evaluation_status=evaluation.status,
        )


class NineBoxCellResponse(BaseModel):
    box_code: str
    box_label: str
    performance_tier: str
    performance_label: str
    potential_tier: str
    potential_label: str
    employee_count: int
    employees: list[NineBoxEmployeeSummary]


class NineBoxMatrixResponse(BaseModel):
    review_cycle_id: int
    review_cycle_name: str
    review_cycle_status: str
    total_employees: int
    cells: list[NineBoxCellResponse]

    @classmethod
    def from_review_cycle(
        cls,
        review_cycle: ReviewCycle,
        cells: list[NineBoxCellResponse],
        total_employees: int,
    ) -> "NineBoxMatrixResponse":
        return cls(
            review_cycle_id=review_cycle.id,
            review_cycle_name=review_cycle.name,
            review_cycle_status=review_cycle.status,
            total_employees=total_employees,
            cells=cells,
        )
