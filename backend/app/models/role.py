from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RoleName(str, Enum):
    EMPLOYEE = "employee"
    PEOPLE_MANAGER = "people_manager"
    UPPER_MANAGER = "upper_manager"
    EXECUTIVE = "executive"
    HR_ADMIN = "hr_admin"
    SYSTEM_ADMIN = "system_admin"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user_roles = relationship("UserRole", back_populates="role")

