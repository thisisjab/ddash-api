from api.database.models import BaseDatabaseModel, TimestampedModelMixin
from uuid import UUID
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import types, text


class User(BaseDatabaseModel, TimestampedModelMixin):
    # Only add authentication-related fields here.

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        init=False,
        server_default=text("gen_random_uuid()"),
    )

    email: Mapped[str] = mapped_column(types.String(255), unique=True, nullable=False)

    password: Mapped[str] = mapped_column(types.String(255), nullable=False)