from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import case, select
from sqlalchemy.orm import Session, selectinload

from app.models.employee import Employee
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.review_cycle import ReviewCycle, ReviewCycleStatus
from app.models.role import RoleName
from app.models.user import User
from app.schemas.nine_box import (
    NineBoxCellResponse,
    NineBoxEmployeeSummary,
    NineBoxMatrixResponse,
)
from app.services.access_service import AccessService
from app.services.errors import AuthorizationError, NotFoundError, ValidationError


@dataclass(frozen=True)
class NineBoxPlacementSnapshot:
    performance_tier: str
    performance_label: str
    potential_tier: str
    potential_label: str
    nine_box_code: str
    nine_box_label: str


class NineBoxService:
    PERFORMANCE_LABELS = {
        "at_risk": "At-Risk Performance",
        "effective": "Effective Performance",
        "high": "High Performance",
    }
    POTENTIAL_LABELS = {
        "limited": "Limited Potential",
        "moderate": "Moderate Potential",
        "high": "High Potential",
    }
    BOX_DEFINITIONS = {
        ("high", "at_risk"): (
            "high_potential_at_risk_performance",
            "Misplaced",
        ),
        ("high", "effective"): (
            "high_potential_effective_performance",
            "Emerging",
        ),
        ("high", "high"): (
            "high_potential_high_performance",
            "Accelerator",
        ),
        ("moderate", "at_risk"): (
            "moderate_potential_at_risk_performance",
            "Unstable",
        ),
        ("moderate", "effective"): (
            "moderate_potential_effective_performance",
            "Contributor",
        ),
        ("moderate", "high"): (
            "moderate_potential_high_performance",
            "Anchor",
        ),
        ("limited", "at_risk"): (
            "limited_potential_at_risk_performance",
            "Strained",
        ),
        ("limited", "effective"): (
            "limited_potential_effective_performance",
            "Dependable",
        ),
        ("limited", "high"): (
            "limited_potential_high_performance",
            "Expert",
        ),
    }
    POTENTIAL_ROW_ORDER = ("high", "moderate", "limited")
    PERFORMANCE_COLUMN_ORDER = ("at_risk", "effective", "high")

    def __init__(self, access_service: AccessService | None = None) -> None:
        self.access_service = access_service or AccessService()

    def build_snapshot(
        self,
        performance_rating: Decimal | float | int,
        potential_rating: int,
    ) -> NineBoxPlacementSnapshot:
        normalized_performance = Decimal(str(performance_rating)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        performance_tier = self._resolve_performance_tier(normalized_performance)
        potential_tier = self._resolve_potential_tier(potential_rating)
        nine_box_code, nine_box_label = self.BOX_DEFINITIONS[
            (potential_tier, performance_tier)
        ]
        return NineBoxPlacementSnapshot(
            performance_tier=performance_tier,
            performance_label=self.PERFORMANCE_LABELS[performance_tier],
            potential_tier=potential_tier,
            potential_label=self.POTENTIAL_LABELS[potential_tier],
            nine_box_code=nine_box_code,
            nine_box_label=nine_box_label,
        )

    def get_matrix(
        self,
        session: Session,
        current_user: User,
        review_cycle_id: int | None = None,
    ) -> NineBoxMatrixResponse:
        if not self.access_service.can_view_evaluations(current_user):
            raise AuthorizationError("You do not have permission to view 9-box placements.")

        review_cycle = self._resolve_review_cycle(session, review_cycle_id)
        visible_employee_ids = self._get_matrix_employee_ids(session, current_user)

        evaluations: list[Evaluation]
        if not visible_employee_ids:
            evaluations = []
        else:
            statement = (
                select(Evaluation)
                .join(Evaluation.employee)
                .options(
                    selectinload(Evaluation.employee).selectinload(Employee.manager),
                    selectinload(Evaluation.review_cycle),
                )
                .where(
                    Evaluation.review_cycle_id == review_cycle.id,
                    Evaluation.status != EvaluationStatus.ARCHIVED.value,
                    Evaluation.employee_id.in_(visible_employee_ids),
                )
                .order_by(Employee.last_name, Employee.first_name, Evaluation.id)
            )
            evaluations = list(session.scalars(statement).all())

        employees_by_box: dict[str, list[NineBoxEmployeeSummary]] = {
            self.BOX_DEFINITIONS[(potential_tier, performance_tier)][0]: []
            for potential_tier in self.POTENTIAL_ROW_ORDER
            for performance_tier in self.PERFORMANCE_COLUMN_ORDER
        }

        for evaluation in evaluations:
            employees_by_box[evaluation.nine_box_code].append(
                NineBoxEmployeeSummary.from_evaluation(evaluation)
            )

        cells: list[NineBoxCellResponse] = []
        for potential_tier in self.POTENTIAL_ROW_ORDER:
            for performance_tier in self.PERFORMANCE_COLUMN_ORDER:
                box_code, box_label = self.BOX_DEFINITIONS[
                    (potential_tier, performance_tier)
                ]
                employees = employees_by_box[box_code]
                cells.append(
                    NineBoxCellResponse(
                        box_code=box_code,
                        box_label=box_label,
                        performance_tier=performance_tier,
                        performance_label=self.PERFORMANCE_LABELS[performance_tier],
                        potential_tier=potential_tier,
                        potential_label=self.POTENTIAL_LABELS[potential_tier],
                        employee_count=len(employees),
                        employees=employees,
                    )
                )

        return NineBoxMatrixResponse.from_review_cycle(
            review_cycle=review_cycle,
            cells=cells,
            total_employees=len(evaluations),
        )

    def _resolve_review_cycle(
        self,
        session: Session,
        review_cycle_id: int | None,
    ) -> ReviewCycle:
        if review_cycle_id is not None:
            review_cycle = session.get(ReviewCycle, review_cycle_id)
            if review_cycle is None:
                raise NotFoundError("Review cycle not found.")
            return review_cycle

        statement = select(ReviewCycle).order_by(
            case(
                (ReviewCycle.status == ReviewCycleStatus.ACTIVE.value, 0),
                else_=1,
            ),
            ReviewCycle.end_date.desc(),
            ReviewCycle.id.desc(),
        )
        review_cycle = session.scalar(statement)
        if review_cycle is None:
            raise NotFoundError("No review cycles are available yet.")
        return review_cycle

    def _get_matrix_employee_ids(
        self,
        session: Session,
        current_user: User,
    ) -> set[int]:
        visible_employee_ids = self.access_service.get_visible_employee_ids(
            session,
            current_user,
        )
        if current_user.role_names.intersection(
            {
                RoleName.PEOPLE_MANAGER.value,
                RoleName.UPPER_MANAGER.value,
            }
        ):
            linked_employee = self.access_service.get_linked_employee(session, current_user)
            if linked_employee is not None:
                visible_employee_ids.discard(linked_employee.id)

        return visible_employee_ids

    def _resolve_performance_tier(self, performance_rating: Decimal) -> str:
        if performance_rating < Decimal("3.00"):
            return "at_risk"

        if performance_rating < Decimal("3.50"):
            return "effective"

        return "high"

    def _resolve_potential_tier(self, potential_rating: int) -> str:
        if potential_rating == 1:
            return "limited"

        if potential_rating == 2:
            return "moderate"

        if potential_rating == 3:
            return "high"

        raise ValidationError("Potential rating must be between 1 and 3.")
