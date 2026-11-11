from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.modules.loans.domain.entities.loan import Loan, LoanStatus
from src.modules.loans.domain.exceptions import (
    BookUnavailableError,
    LoanLimitExceededError,
    LoanNotFoundError,
)
from src.modules.loans.domain.policies.fine_policy import StandardDailyFinePolicy
from src.modules.loans.domain.usecases.borrow_book import BorrowBookUseCase
from src.modules.loans.domain.usecases.return_book import ReturnBookUseCase


class InMemoryLoanRepository:
    def __init__(self) -> None:
        self._loans: dict[UUID, Loan] = {}

    def save(self, loan: Loan) -> Loan:
        self._loans[loan.id] = loan
        return loan

    def get_by_id(self, loan_id: UUID) -> Loan | None:
        return self._loans.get(loan_id)

    def count_active_by_reader(self, reader_id: UUID) -> int:
        return sum(
            1
            for loan in self._loans.values()
            if loan.reader_id == reader_id and loan.status == LoanStatus.ACTIVE
        )

    def has_active_loan_for_book(self, book_id: UUID) -> bool:
        return any(
            loan.book_id == book_id and loan.status == LoanStatus.ACTIVE
            for loan in self._loans.values()
        )

    def list_all(self) -> list[Loan]:
        return list(self._loans.values())


def test_borrow_and_return_book_use_cases() -> None:
    repo = InMemoryLoanRepository()
    borrow_uc = BorrowBookUseCase(repo)
    return_uc = ReturnBookUseCase(repo, StandardDailyFinePolicy())

    loan = borrow_uc.execute(
        book_id=uuid4(),
        reader_id=uuid4(),
        borrowed_at=date(2026, 11, 1),
        due_date=date(2026, 11, 5),
    )
    assert loan.status == LoanStatus.ACTIVE

    returned = return_uc.execute(loan_id=loan.id, returned_at=date(2026, 11, 7))
    assert returned.status == LoanStatus.RETURNED
    assert returned.fine_amount == Decimal("4.00")


def test_cannot_borrow_already_borrowed_book() -> None:
    repo = InMemoryLoanRepository()
    borrow_uc = BorrowBookUseCase(repo)
    book_id = uuid4()

    borrow_uc.execute(book_id, uuid4(), date(2026, 11, 1), date(2026, 11, 8))

    with pytest.raises(BookUnavailableError):
        borrow_uc.execute(book_id, uuid4(), date(2026, 11, 2), date(2026, 11, 9))


def test_reader_cannot_exceed_three_active_loans() -> None:
    repo = InMemoryLoanRepository()
    borrow_uc = BorrowBookUseCase(repo)
    reader_id = uuid4()

    for _ in range(3):
        borrow_uc.execute(uuid4(), reader_id, date(2026, 11, 1), date(2026, 11, 8))

    with pytest.raises(LoanLimitExceededError):
        borrow_uc.execute(uuid4(), reader_id, date(2026, 11, 1), date(2026, 11, 8))


def test_return_nonexistent_loan_raises_not_found() -> None:
    repo = InMemoryLoanRepository()
    return_uc = ReturnBookUseCase(repo, StandardDailyFinePolicy())

    with pytest.raises(LoanNotFoundError):
        return_uc.execute(loan_id=uuid4(), returned_at=date(2026, 11, 8))
