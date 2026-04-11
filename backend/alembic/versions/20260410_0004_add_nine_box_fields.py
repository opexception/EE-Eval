"""Add stored 9-box placement fields to evaluations."""

from collections.abc import Sequence
from decimal import Decimal

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260410_0004"
down_revision: str | None = "20260410_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "evaluations",
        sa.Column("performance_tier", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "evaluations",
        sa.Column("potential_tier", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "evaluations",
        sa.Column("nine_box_code", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "evaluations",
        sa.Column("nine_box_label", sa.String(length=80), nullable=True),
    )

    evaluations = sa.table(
        "evaluations",
        sa.column("id", sa.Integer()),
        sa.column("performance_rating", sa.Numeric(3, 2)),
        sa.column("potential_rating", sa.Integer()),
        sa.column("performance_tier", sa.String(length=32)),
        sa.column("potential_tier", sa.String(length=32)),
        sa.column("nine_box_code", sa.String(length=64)),
        sa.column("nine_box_label", sa.String(length=80)),
    )

    connection = op.get_bind()
    result = connection.execute(
        sa.select(
            evaluations.c.id,
            evaluations.c.performance_rating,
            evaluations.c.potential_rating,
        )
    )

    for row in result:
        performance_tier = _resolve_performance_tier(row.performance_rating)
        potential_tier = _resolve_potential_tier(row.potential_rating)
        nine_box_code, nine_box_label = BOX_DEFINITIONS[
            (potential_tier, performance_tier)
        ]
        connection.execute(
            evaluations.update()
            .where(evaluations.c.id == row.id)
            .values(
                performance_tier=performance_tier,
                potential_tier=potential_tier,
                nine_box_code=nine_box_code,
                nine_box_label=nine_box_label,
            )
        )

    op.alter_column("evaluations", "performance_tier", nullable=False)
    op.alter_column("evaluations", "potential_tier", nullable=False)
    op.alter_column("evaluations", "nine_box_code", nullable=False)
    op.alter_column("evaluations", "nine_box_label", nullable=False)


def downgrade() -> None:
    op.drop_column("evaluations", "nine_box_label")
    op.drop_column("evaluations", "nine_box_code")
    op.drop_column("evaluations", "potential_tier")
    op.drop_column("evaluations", "performance_tier")


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


def _resolve_performance_tier(performance_rating: Decimal) -> str:
    normalized = Decimal(str(performance_rating))
    if normalized < Decimal("3.00"):
        return "at_risk"

    if normalized < Decimal("3.50"):
        return "effective"

    return "high"


def _resolve_potential_tier(potential_rating: int) -> str:
    if potential_rating == 1:
        return "limited"

    if potential_rating == 2:
        return "moderate"

    return "high"
