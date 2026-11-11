from datetime import date
from uuid import UUID

from src.modules.loans.domain.entities.loan import Loan
from src.modules.loans.domain.exceptions import LoanNotFoundError
from src.modules.loans.domain.policies.fine_policy import FinePolicy
from src.modules.loans.domain.repositories.loan_repository import LoanRepository


class ReturnBookUseCase:
    """Caso de uso: Registrar devolução e calcular multa via Strategy."""

    def __init__(self, loan_repo: LoanRepository, fine_policy: FinePolicy) -> None:
        self._loan_repo = loan_repo
        self._fine_policy = fine_policy

    def execute(self, loan_id: UUID, returned_at: date) -> Loan:
        loan = self._loan_repo.get_by_id(loan_id)
        if loan is None:
            raise LoanNotFoundError("Empréstimo não encontrado.")

        loan.return_book(returned_at=returned_at, fine_policy=self._fine_policy)
        return self._loan_repo.save(loan)
