import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .group_user import GroupUser


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Authentication fields
    username: Mapped[str] = mapped_column(unique=True, index=True)
    # Will be incorporated in future updates
    password_hash: Mapped[str | None]

    email: Mapped[str | None] = mapped_column(unique=True, index=True)

    role: Mapped[str] = mapped_column(String(50), default="user")

    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now(dt.timezone.utc))
    updated_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now(dt.timezone.utc), onupdate=dt.datetime.now(dt.timezone.utc))

    groups: Mapped[list["GroupUser"]] = relationship(back_populates="user", cascade="all, delete-orphan")
