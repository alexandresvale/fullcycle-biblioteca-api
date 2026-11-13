from uuid import UUID

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ReaderModel(Base):
    """Modelo ORM SQLAlchemy 2.0 para a tabela de leitores."""

    __tablename__ = "readers"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    document: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
