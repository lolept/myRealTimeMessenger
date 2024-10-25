from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column


class TimeStampMixin:
    created: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    modified: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True)
