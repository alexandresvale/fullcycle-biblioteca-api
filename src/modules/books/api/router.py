from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.core.exceptions import DomainError
from src.modules.books.api.dependencies import (
    GetBookUseCaseDep,
    ListBooksUseCaseDep,
    RegisterBookUseCaseDep,
)
from src.modules.books.api.schemas import BookResponse, CreateBookRequest
from src.modules.books.domain.exceptions import BookNotFoundError, DuplicateIsbnError

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar livro no acervo",
)
def create_book(
    payload: CreateBookRequest,
    use_case: RegisterBookUseCaseDep,
) -> BookResponse:
    """Cadastra um novo livro no acervo garantindo unicidade de ISBN."""
    try:
        book = use_case.execute(
            title=payload.title,
            author=payload.author,
            isbn=payload.isbn,
            total_copies=payload.total_copies,
        )
        return BookResponse.model_validate(book)
    except DuplicateIsbnError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[BookResponse],
    summary="Listar livros do acervo",
)
def list_books(
    use_case: ListBooksUseCaseDep,
    available_only: bool = Query(default=False, description="Filtrar apenas livros disponíveis"),
) -> list[BookResponse]:
    """Retorna os livros cadastrados no acervo, com filtro opcional de disponibilidade."""
    books = use_case.execute(available_only=available_only)
    return [BookResponse.model_validate(book) for book in books]


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Buscar livro por ID",
)
def get_book(book_id: UUID, use_case: GetBookUseCaseDep) -> BookResponse:
    """Consulta os detalhes e o saldo de exemplares de um livro específico."""
    try:
        book = use_case.execute(book_id)
        return BookResponse.model_validate(book)
    except BookNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
