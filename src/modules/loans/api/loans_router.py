from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.core.exceptions import DomainError
from src.modules.loans.api.dependencies import (
    BorrowBookUseCaseDep,
    LoanRepoDep,
    resolve_fine_policy,
)
from src.modules.loans.api.loan_schema import (
    CreateLoanRequest,
    LoanResponse,
    ReturnLoanRequest,
)
from src.modules.loans.domain.exceptions import (
    BookUnavailableError,
    LoanAlreadyReturnedError,
    LoanLimitExceededError,
    LoanNotFoundError,
)
from src.modules.loans.domain.usecases.return_book import ReturnBookUseCase

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(payload: CreateLoanRequest, use_case: BorrowBookUseCaseDep) -> LoanResponse:
    try:
        loan = use_case.execute(
            book_id=payload.book_id,
            reader_id=payload.reader_id,
            borrowed_at=payload.borrowed_at,
            due_date=payload.due_date,
        )
        return LoanResponse.model_validate(loan)
    except BookUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LoanLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{loan_id}/return", response_model=LoanResponse)
def return_loan(loan_id: UUID, payload: ReturnLoanRequest, repo: LoanRepoDep) -> LoanResponse:
    policy = resolve_fine_policy(payload.policy_type)
    use_case = ReturnBookUseCase(repo, policy)
    try:
        loan = use_case.execute(loan_id=loan_id, returned_at=payload.returned_at)
        return LoanResponse.model_validate(loan)
    except LoanNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LoanAlreadyReturnedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[LoanResponse])
def list_loans(repo: LoanRepoDep) -> list[LoanResponse]:
    return [LoanResponse.model_validate(loan) for loan in repo.list_all()]


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: UUID, repo: LoanRepoDep) -> LoanResponse:
    loan = repo.get_by_id(loan_id)
    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Empréstimo não encontrado."
        )
    return LoanResponse.model_validate(loan)
