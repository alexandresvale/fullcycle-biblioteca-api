from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from src.core.exceptions import DomainError
from src.modules.loans.domain.exceptions import LoanAlreadyReturnedError
from src.modules.loans.domain.policies.fine_policy import FinePolicy


class LoanStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"


@dataclass
class Loan:
    book_id: UUID
    reader_id: UUID
    borrowed_at: date
    due_date: date
    id: UUID = field(default_factory=uuid4)
    returned_at: date | None = None
    fine_amount: Decimal = Decimal("0.00")
    status: LoanStatus = LoanStatus.ACTIVE

    def __post_init__(self) -> None:
        if self.due_date < self.borrowed_at:
            raise DomainError("Data de vencimento não pode ser anterior ao empréstimo.")

    def days_overdue(self, reference_date: date) -> int:
        if reference_date <= self.due_date:
            return 0
        return (reference_date - self.due_date).days

    def return_book(self, returned_at: date, fine_policy: FinePolicy) -> Decimal:
        if self.status == LoanStatus.RETURNED:
            raise LoanAlreadyReturnedError("Este empréstimo já foi finalizado.")
        if returned_at < self.borrowed_at:
            raise DomainError("Data de devolução não pode ser anterior ao empréstimo.")
        overdue_days = self.days_overdue(returned_at)
        self.fine_amount = fine_policy.calculate_fine(overdue_days)
        self.returned_at = returned_at
        self.status = LoanStatus.RETURNED
        return self.fine_amount
