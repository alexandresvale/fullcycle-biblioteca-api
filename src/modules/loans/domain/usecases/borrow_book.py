from datetime import date
from uuid import UUID

from src.modules.loans.domain.entities.loan import Loan
from src.modules.loans.domain.exceptions import BookUnavailableError, LoanLimitExceededError
from src.modules.loans.domain.repositories.loan_repository import LoanRepository

MAX_ACTIVE_LOANS_PER_READER = 3


class BorrowBookUseCase:
    """Caso de uso: Realizar um novo empréstimo de livro."""

    def __init__(self, loan_repo: LoanRepository) -> None:
        self._loan_repo = loan_repo

    def execute(self, book_id: UUID, reader_id: UUID, borrowed_at: date, due_date: date) -> Loan:
        if self._loan_repo.has_active_loan_for_book(book_id):
            raise BookUnavailableError("Este exemplar já está emprestado no momento.")

        active_count = self._loan_repo.count_active_by_reader(reader_id)
        if active_count >= MAX_ACTIVE_LOANS_PER_READER:
            raise LoanLimitExceededError("Leitor atingiu o limite de 3 empréstimos ativos.")

        loan = Loan(
            book_id=book_id,
            reader_id=reader_id,
            borrowed_at=borrowed_at,
            due_date=due_date,
        )

        return self._loan_repo.save(loan)
