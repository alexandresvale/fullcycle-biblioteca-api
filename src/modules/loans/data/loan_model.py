from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class LoanModel(Base):
    __tablename__ = "loans"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    book_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    reader_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    borrowed_at: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    returned_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    fine_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
