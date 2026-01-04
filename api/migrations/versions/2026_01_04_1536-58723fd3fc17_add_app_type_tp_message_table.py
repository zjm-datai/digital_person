"""add app_type tp message table

Revision ID: 58723fd3fc17
Revises: e5d8f5b988f0
Create Date: 2026-01-04 15:36:14.667272
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "58723fd3fc17"
down_revision = "e5d8f5b988f0"
branch_labels = None
depends_on = None


def upgrade():
    """
    Why this is needed:
    - PostgreSQL will fail if you add a NOT NULL column to a table that already
      has rows, unless you provide a default or fill existing rows first.
    - This migration adds `app_type` and `role` as NOT NULL, so we provide
      server_default to backfill existing rows, then drop the defaults so future
      inserts must explicitly provide values.
    """

    # 1) Add columns with server defaults to satisfy existing rows
    with op.batch_alter_table("messages", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "app_type",
                sa.String(length=255),
                nullable=False,
                server_default=sa.text("'pifuke'"),  # TODO: change if your default differs
            )
        )
        batch_op.add_column(
            sa.Column(
                "current_stage",
                sa.String(length=255),
                nullable=True,
                comment="只有 role 为 assistant 的时候存在该字段，代表提问时所处的问诊阶段",
            )
        )
        batch_op.add_column(
            sa.Column(
                "current_field",
                sa.String(length=255),
                nullable=True,
                comment="只有 role 为 assistant 的时候存在该字段，代表提问时所提问的问诊字段",
            )
        )
        batch_op.add_column(
            sa.Column(
                "role",
                sa.String(length=255),
                nullable=False,
                server_default=sa.text("'user'"),  # TODO: change if your default differs
            )
        )

    # 2) (Optional but safe) Ensure any weird rows are filled (usually redundant with server_default)
    op.execute("UPDATE messages SET app_type = 'pifuke' WHERE app_type IS NULL")
    op.execute("UPDATE messages SET role = 'user' WHERE role IS NULL")

    # 3) Drop defaults to avoid silently defaulting on future inserts
    with op.batch_alter_table("messages", schema=None) as batch_op:
        batch_op.alter_column("app_type", server_default=None)
        batch_op.alter_column("role", server_default=None)


def downgrade():
    with op.batch_alter_table("messages", schema=None) as batch_op:
        batch_op.drop_column("role")
        batch_op.drop_column("current_field")
        batch_op.drop_column("current_stage")
        batch_op.drop_column("app_type")
