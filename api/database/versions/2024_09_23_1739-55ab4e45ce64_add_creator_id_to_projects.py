"""add_creator_id_to_projects

Revision ID: 55ab4e45ce64
Revises: 4990477aa5eb
Create Date: 2024-09-23 17:39:32.239018+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "55ab4e45ce64"
down_revision: Union[str, None] = "4990477aa5eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("projects", sa.Column("creator_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        op.f("fk_projects_creator_id_users"),
        "projects",
        "users",
        ["creator_id"],
        ["id"],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("fk_projects_creator_id_users"), "projects", type_="foreignkey"
    )
    op.drop_column("projects", "creator_id")
    # ### end Alembic commands ###