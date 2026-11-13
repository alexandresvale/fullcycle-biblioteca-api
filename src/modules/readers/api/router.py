from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.core.exceptions import DomainError
from src.modules.readers.api.dependencies import (
    GetReaderUseCaseDep,
    ListReadersUseCaseDep,
    RegisterReaderUseCaseDep,
)
from src.modules.readers.api.schemas import CreateReaderRequest, ReaderResponse
from src.modules.readers.domain.exceptions import DuplicateReaderError, ReaderNotFoundError

router = APIRouter(prefix="/readers", tags=["Readers"])


@router.post(
    "",
    response_model=ReaderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar leitor",
)
def create_reader(
    payload: CreateReaderRequest,
    use_case: RegisterReaderUseCaseDep,
) -> ReaderResponse:
    """Cadastra um novo leitor garantindo unicidade de e-mail e documento."""
    try:
        reader = use_case.execute(
            name=payload.name,
            email=payload.email,
            document=payload.document,
            category=payload.category,
            active=payload.active,
        )
        return ReaderResponse.model_validate(reader)
    except DuplicateReaderError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[ReaderResponse],
    summary="Listar leitores",
)
def list_readers(use_case: ListReadersUseCaseDep) -> list[ReaderResponse]:
    """Retorna todos os leitores cadastrados ordenados por nome."""
    readers = use_case.execute()
    return [ReaderResponse.model_validate(reader) for reader in readers]


@router.get(
    "/{reader_id}",
    response_model=ReaderResponse,
    summary="Buscar leitor por ID",
)
def get_reader(reader_id: UUID, use_case: GetReaderUseCaseDep) -> ReaderResponse:
    """Consulta os detalhes de um leitor específico pelo ID."""
    try:
        reader = use_case.execute(reader_id)
        return ReaderResponse.model_validate(reader)
    except ReaderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
