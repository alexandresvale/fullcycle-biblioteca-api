from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.modules.loans.data.loan_model import LoanModel
from src.modules.loans.domain.entities.loan import Loan, LoanStatus


class SqlAlchemyLoanRepository:
    """Implementação concreta do LoanRepository com PostgreSQL + SQLAlchemy 2.0."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, loan: Loan) -> Loan:
        model = self._session.get(LoanModel, loan.id)
        if model is None:
            model = LoanModel(
                id=loan.id,
                book_id=loan.book_id,
                reader_id=loan.reader_id,
                borrowed_at=loan.borrowed_at,
                due_date=loan.due_date,
                returned_at=loan.returned_at,
                fine_amount=loan.fine_amount,
                status=loan.status.value,
            )
            self._session.add(model)
        else:
            model.returned_at = loan.returned_at
            model.fine_amount = loan.fine_amount
            model.status = loan.status.value

        self._session.commit()
        return loan

    def get_by_id(self, loan_id: UUID) -> Loan | None:
        model = self._session.get(LoanModel, loan_id)
        if model is None:
            return None
        return self._to_entity(model)

    def count_active_by_reader(self, reader_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(LoanModel)
            .where(
                LoanModel.reader_id == reader_id,
                LoanModel.status == LoanStatus.ACTIVE.value,
            )
        )
        return int(self._session.scalar(stmt) or 0)

    def has_active_loan_for_book(self, book_id: UUID) -> bool:
        stmt = (
            select(func.count())
            .select_from(LoanModel)
            .where(
                LoanModel.book_id == book_id,
                LoanModel.status == LoanStatus.ACTIVE.value,
            )
        )
        return int(self._session.scalar(stmt) or 0) > 0

    def list_all(self) -> list[Loan]:
        stmt = select(LoanModel).order_by(LoanModel.borrowed_at.desc())
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_entity(model: LoanModel) -> Loan:
        return Loan(
            id=model.id,
            book_id=model.book_id,
            reader_id=model.reader_id,
            borrowed_at=model.borrowed_at,
            due_date=model.due_date,
            returned_at=model.returned_at,
            fine_amount=Decimal(str(model.fine_amount)),
            status=LoanStatus(model.status),
        )
