from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from api.database import Base
from api.models.mixins import IdMixin, TimeStampMixin


class User(Base, IdMixin, TimeStampMixin):
    __tablename__ = "user"
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_verified: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    verification_code: Mapped[str] = mapped_column(
        unique=True, server_default=text("gen_random_uuid()"), nullable=True
    )
