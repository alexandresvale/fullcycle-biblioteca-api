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


@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar novo empréstimo",
)
def create_loan(payload: CreateLoanRequest, use_case: BorrowBookUseCaseDep) -> LoanResponse:
    """Registra o empréstimo de um exemplar para um leitor, validando disponibilidade e limite."""
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


@router.post(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Registrar devolução de livro",
)
def return_loan(loan_id: UUID, payload: ReturnLoanRequest, repo: LoanRepoDep) -> LoanResponse:
    """Finaliza um empréstimo ativo e calcula eventual multa por atraso via Strategy Pattern."""
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


@router.get(
    "",
    response_model=list[LoanResponse],
    summary="Listar empréstimos",
)
def list_loans(repo: LoanRepoDep) -> list[LoanResponse]:
    """Retorna todos os empréstimos cadastrados ordenados pela data de empréstimo."""
    return [LoanResponse.model_validate(loan) for loan in repo.list_all()]


@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Buscar empréstimo por ID",
)
def get_loan(loan_id: UUID, repo: LoanRepoDep) -> LoanResponse:
    """Consulta os detalhes, status e valor de multa de um empréstimo específico."""
    loan = repo.get_by_id(loan_id)
    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Empréstimo não encontrado."
        )
    return LoanResponse.model_validate(loan)
