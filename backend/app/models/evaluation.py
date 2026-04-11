from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EvaluationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ARCHIVED = "archived"


class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "review_cycle_id",
            name="uq_evaluations_employee_review_cycle",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
    )
    review_cycle_id: Mapped[int] = mapped_column(
        ForeignKey("review_cycles.id"),
        nullable=False,
    )
    author_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    updated_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    performance_rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
    )
    potential_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    performance_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    potential_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    nine_box_code: Mapped[str] = mapped_column(String(64), nullable=False)
    nine_box_label: Mapped[str] = mapped_column(String(80), nullable=False)
    summary_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    manager_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    promotion_recommendation: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )
    promotion_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    employee = relationship("Employee", back_populates="evaluations")
    review_cycle = relationship("ReviewCycle", back_populates="evaluations")
