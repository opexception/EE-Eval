"""Add sensitive evaluation fields and audit entries."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260410_0005"
down_revision: str | None = "20260410_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "evaluations",
        sa.Column("manager_rationale", sa.Text(), nullable=True),
    )
    op.add_column(
        "evaluations",
        sa.Column("promotion_recommendation", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "evaluations",
        sa.Column("promotion_rationale", sa.Text(), nullable=True),
    )

    op.create_table(
        "audit_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resource_type", sa.String(length=40), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("field_changes", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_audit_entries_resource_lookup",
        "audit_entries",
        ["resource_type", "resource_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_entries_resource_lookup", table_name="audit_entries")
    op.drop_table("audit_entries")
    op.drop_column("evaluations", "promotion_rationale")
    op.drop_column("evaluations", "promotion_recommendation")
    op.drop_column("evaluations", "manager_rationale")
