from datetime import date
from uuid import UUID
from api.database.models import BaseDatabaseModel, TimestampedModelMixin
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import types, text


class Project(BaseDatabaseModel, TimestampedModelMixin):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        init=False,
        server_default=text("gen_random_uuid()"),
    )

    title: Mapped[str] = mapped_column(types.String(75), nullable=False)

    description: Mapped[str] = mapped_column(
        types.Text(),
        nullable=True,
    )

    start_date: Mapped[date] = mapped_column(types.Date(), nullable=True)

    finish_date: Mapped[date] = mapped_column(types.Date(), nullable=True)

    deadline: Mapped[date] = mapped_column(types.Date(), nullable=True)
