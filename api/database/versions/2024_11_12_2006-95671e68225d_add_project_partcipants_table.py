"""add_project_partcipants_table

Revision ID: 95671e68225d
Revises: 8ba8a2bfa1f8
Create Date: 2024-11-12 20:06:20.758015+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "95671e68225d"
down_revision: Union[str, None] = "8ba8a2bfa1f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "project_participants",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "participation_type",
            sa.Enum("CONTRIBUTOR", "VIEWER", name="projectparticipationtype"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "modified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_project_participants_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_project_participants_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "project_id", "user_id", name=op.f("pk_project_participants")
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("project_participants")
    # ### end Alembic commands ###
