from typing import Annotated, Literal

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.loans.data.loan_repository_sqlalchemy import SqlAlchemyLoanRepository
from src.modules.loans.domain.policies.fine_policy import (
    AcademicGraceFinePolicy,
    FinePolicy,
    StandardDailyFinePolicy,
)
from src.modules.loans.domain.repositories.loan_repository import LoanRepository
from src.modules.loans.domain.usecases.borrow_book import BorrowBookUseCase

DbSession = Annotated[Session, Depends(get_db)]


def get_loan_repository(db: DbSession) -> LoanRepository:
    return SqlAlchemyLoanRepository(db)


LoanRepoDep = Annotated[LoanRepository, Depends(get_loan_repository)]


def get_borrow_book_use_case(repo: LoanRepoDep) -> BorrowBookUseCase:
    return BorrowBookUseCase(repo)


BorrowBookUseCaseDep = Annotated[BorrowBookUseCase, Depends(get_borrow_book_use_case)]


def resolve_fine_policy(policy_type: Literal["STANDARD", "ACADEMIC"]) -> FinePolicy:
    if policy_type == "ACADEMIC":
        return AcademicGraceFinePolicy()
    return StandardDailyFinePolicy()
