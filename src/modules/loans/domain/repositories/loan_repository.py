from typing import Protocol
from uuid import UUID

from src.modules.loans.domain.entities.loan import Loan


class LoanRepository(Protocol):
    """Contrato de persistência para empréstimos (DIP - SOLID)."""

    def save(self, loan: Loan) -> Loan: ...

    def get_by_id(self, loan_id: UUID) -> Loan | None: ...

    def count_active_by_reader(self, reader_id: UUID) -> int: ...

    def has_active_loan_for_book(self, book_id: UUID) -> bool: ...

    def list_all(self) -> list[Loan]: ...
