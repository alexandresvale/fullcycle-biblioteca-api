from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.loan import Loan, LoanStatus
from src.domain.exceptions import DomainError, LoanAlreadyReturnedError
from src.domain.policies.fine_policy import (
    AcademicGraceFinePolicy,
    StandardDailyFinePolicy,
)


def test_return_loan_on_time_has_zero_fine() -> None:
    loan = Loan(
        book_id=uuid4(),
        reader_id=uuid4(),
        borrowed_at=date(2026, 11, 1),
        due_date=date(2026, 11, 8),
    )
    fine = loan.return_book(date(2026, 11, 8), StandardDailyFinePolicy())
    assert fine == Decimal("0.00")
    assert loan.status == LoanStatus.RETURNED
    assert loan.returned_at == date(2026, 11, 8)


def test_return_loan_overdue_with_standard_policy() -> None:
    loan = Loan(
        book_id=uuid4(),
        reader_id=uuid4(),
        borrowed_at=date(2026, 11, 1),
        due_date=date(2026, 11, 5),
    )
    fine = loan.return_book(date(2026, 11, 8), StandardDailyFinePolicy())
    assert fine == Decimal("6.00")
    assert loan.fine_amount == Decimal("6.00")


def test_return_loan_overdue_with_academic_grace_policy() -> None:
    policy = AcademicGraceFinePolicy(grace_days = 2, daily_rate = Decimal("1.50"))
    loan_within_grace = Loan(
        book_id=uuid4(),
        reader_id=uuid4(),
        borrowed_at=date(2026, 11, 1),
        due_date=date(2026, 11, 5),
    )
    loan_beyond_grace = Loan(
        book_id=uuid4(),
        reader_id=uuid4(),
        borrowed_at=date(2026, 11, 1),
        due_date=date(2026, 11, 5),
    )
    assert loan_within_grace.return_book(date(2026, 11, 7), policy) == Decimal("0.00")
    assert loan_beyond_grace.return_book(date(2026, 11, 10), policy) == Decimal("4.50")


def test_cannot_return_loan_twice() -> None:
    loan = Loan(
        book_id=uuid4(),
        reader_id=uuid4(),
        borrowed_at=date(2026, 11, 1),
        due_date=date(2026, 11, 5),
    )
    loan.return_book(date(2026, 11, 5), StandardDailyFinePolicy())
    with pytest.raises(LoanAlreadyReturnedError):
        loan.return_book(date(2026, 11, 6), StandardDailyFinePolicy())


def test_invalid_loan_dates_raise_domain_error() -> None:
    with pytest.raises(DomainError):
        Loan(
            book_id=uuid4(),
            reader_id=uuid4(),
            borrowed_at=date(2026, 11, 10),
            due_date=date(2026, 11, 5),
        )
